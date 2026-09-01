# train tickets - step academy course project
from flask import Flask, render_template, request, session, send_file, jsonify, make_response
import requests
from fpdf import FPDF
import tempfile, os, random, string
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

S = "https://railway.stepprojects.ge"
mem = {}

# api days are georgian weekday names not calendar dates
D = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]

# pdf fallback when sylfaen missing
M = {
"ა":"a","ბ":"b","გ":"g","დ":"d","ე":"e","ვ":"v","ზ":"z","თ":"t","ი":"i","კ":"k","ლ":"l","მ":"m","ნ":"n","ო":"o",
"პ":"p","ჟ":"zh","რ":"r","ს":"s","ტ":"t","უ":"u","ფ":"p","ქ":"k","ღ":"gh","ყ":"q","შ":"sh","ჩ":"ch","ც":"ts",
"ძ":"dz","წ":"ts","ჭ":"ch","ხ":"kh","ჯ":"j","ჰ":"h"
}

def g(p):
    try:
        r = requests.get(S + p, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def tr(x):
    if x is None: return ""
    return "".join(M[c] if c in M else c for c in str(x))


@app.route("/")
def index():
    deps = g("/api/departures")
    cset = set()
    if deps:
        i = 0
        while i < len(deps):
            row = deps[i]
            if "source" in row and row["source"]:
                cset.add(row["source"].strip())
            if "destination" in row and row["destination"]:
                cset.add(row["destination"].strip())
            i += 1
    return render_template("index.html", cities=sorted(list(cset)), days=D)


@app.route("/trains")
def trains():
    frm = request.args["from_city"].strip() if "from_city" in request.args else ""
    to = request.args["to_city"].strip() if "to_city" in request.args else ""
    day = request.args["date"].strip() if "date" in request.args else ""
    try:
        cnt = int(request.args.get("tickets", 1))
    except:
        cnt = 1

    session["src"] = frm
    session["dst"] = to
    session["day"] = day
    session["count"] = cnt

    out = []
    deps = g("/api/departures")
    if deps is not None:
        for row in deps:
            ok = True
            if row.get("source", "").strip() != frm: ok = False
            if ok and row.get("destination", "").strip() != to: ok = False
            if ok and row.get("date", "").strip() != day: ok = False
            if ok:
                ts = row.get("trains")
                if ts:
                    out.extend(ts)

    # price from first free seat we find
    vag = g("/api/vagons")
    if vag:
        for t in out:
            t["price"] = 25
            for v in vag:
                if v.get("trainId") == t.get("id"):
                    if v.get("seats"):
                        t["price"] = v["seats"][0].get("price", 25)
                    break

    return render_template(
        "trains.html", trains=out, date=day, from_name=frm, to_name=to, num_tickets=cnt
    )


@app.route("/passengers/<int:train_id>")
def passengers(train_id):
    session["train_id"] = train_id
    train = None
    deps = g("/api/departures") or []
    for block in deps:
        for t in block.get("trains") or []:
            if t.get("id") == train_id:
                train = t
                break
        if train is not None:
            break

    wagons = []
    for v in g("/api/vagons") or []:
        if v.get("trainId") == train_id:
            wagons.append(v)

    if train is None:
        train = dict(id=train_id, number="?", name="მატარებელი", departure="--:--", arrive="--:--")
    train["vagons"] = wagons
    session["train"] = train

    html = render_template(
        "passengers.html",
        num_tickets=session.get("count", 1),
        train=train,
        from_name=session.get("src", ""),
        to_name=session.get("dst", ""),
        date=session.get("day", ""),
    )
    return html


@app.route("/api/vagon/<int:vagon_id>")
def api_vagon(vagon_id):
    data = g("/api/vagons")
    if not data:
        return jsonify({})
    for item in data:
        if item.get("id") == vagon_id:
            return jsonify(item)
    return jsonify({})


@app.route("/payment", methods=["POST"])
def payment():
    session["email"] = request.form["email"].strip() if "email" in request.form else ""
    session["phone"] = request.form["phone"].strip() if "phone" in request.form else ""
    n = session.get("count", 1)
    plist = []
    for i in range(n):
        sp = request.form.get("seat_price_" + str(i), "25")
        try:
            price = float(sp)
        except ValueError:
            price = 25.0
        plist.append({
            "name": request.form.get("first_name_" + str(i), ""),
            "surname": request.form.get("last_name_" + str(i), ""),
            "idNumber": request.form.get("personal_id_" + str(i), ""),
            "seatId": request.form.get("seat_id_" + str(i), ""),
            "seatNumber": request.form.get("seat_number_" + str(i), ""),
            "vagonName": request.form.get("vagon_name_" + str(i), ""),
            "seatPrice": price,
        })
    session["plist"] = plist
    total = 0
    for p in plist:
        total = total + p["seatPrice"]
    session["total"] = total
    return render_template("payment.html", total=total, passengers=plist, train=session.get("train"), from_name=session.get("src"), to_name=session.get("dst"))


@app.route("/process_payment", methods=["POST"])
def process_payment():
    plist = session.get("plist", [])
    train_id = session.get("train_id", 0)

    people = []
    for p in plist:
        people.append({
            "seatId": p["seatId"],
            "name": p["name"],
            "surname": p["surname"],
            "idNumber": p["idNumber"],
            "status": "active",
            "payoutCompleted": True,
        })

    payload = {
        "trainId": int(train_id),
        "date": datetime.now().isoformat() + "Z",
        "email": session.get("email", ""),
        "phoneNumber": session.get("phone", ""),
        "people": people,
    }

    ticket = None
    try:
        rr = requests.post(S + "/api/tickets/register", json=payload, timeout=5)
        if rr.status_code in (200, 201):
            ticket = rr.json()
    except Exception as e:
        print(e)

    if ticket is not None and "id" in ticket:
        conf = g("/api/tickets/confirm/" + str(ticket["id"]))
        if conf:
            ticket = conf
    else:
        # offline demo ticket
        chars = string.ascii_uppercase + string.digits
        code = "GEO-"
        for _ in range(8):
            code += random.choice(chars)
        tinfo = session.get("train") or {}
        ticket = {
            "id": code,
            "email": session.get("email"),
            "phone": session.get("phone"),
            "date": session.get("day"),
            "ticketPrice": session.get("total", 0),
            "confirmed": True,
            "status": "Active",
            "train": {
                "number": tinfo.get("number"),
                "name": tinfo.get("name"),
                "from": session.get("src"),
                "to": session.get("dst"),
                "departure": tinfo.get("departure"),
                "arrive": tinfo.get("arrive"),
            },
            "persons": [],
        }
        for p in plist:
            ticket["persons"].append({
                "name": p["name"],
                "surname": p["surname"],
                "idNumber": p["idNumber"],
                "seat": {"number": p["seatNumber"]},
                "vagonName": p["vagonName"],
                "status": "active",
            })

    mem[str(ticket["id"])] = ticket
    session["ticket"] = ticket
    return render_template("ticket_result.html", ticket=ticket, train=session.get("train"), from_name=session.get("src"), to_name=session.get("dst"), date=session.get("day"), total=session.get("total", 0), passengers=plist)


@app.route("/download_ticket")
def download_ticket():
    tk = session.get("ticket") or {}
    trn = session.get("train") or {}
    pl = session.get("plist") or []

    pdf = FPDF()
    pdf.add_page()
    unicode_ok = False
    for path in [r"C:\Windows\Fonts\sylfaen.ttf", r"C:\Windows\Fonts\arial.ttf"]:
        if os.path.isfile(path):
            try:
                pdf.add_font("Ka", fname=path)
                pdf.set_font("Ka", size=12)
                unicode_ok = True
                break
            except Exception:
                continue
    if unicode_ok is False:
        pdf.set_font("Helvetica", size=12)

    def tx(s):
        if unicode_ok:
            return str(s)
        return tr(s)

    pdf.set_font_size(18)
    pdf.cell(0, 15, "RAILWAY TICKET", ln=True, align="C")
    pdf.ln(3)
    pdf.set_font_size(11)
    pdf.cell(0, 7, "Ticket ID: " + str(tk.get("id", "")), ln=True)
    pdf.cell(0, 7, "Route: " + tx(session.get("src", "")) + " -> " + tx(session.get("dst", "")), ln=True)
    pdf.cell(0, 7, "Day: " + tx(session.get("day", "")), ln=True)
    if trn:
        pdf.cell(0, 7, "Train #" + str(trn.get("number", "")) + " (" + tx(trn.get("name", "")) + ")", ln=True)
        pdf.cell(0, 7, "Time: " + str(trn.get("departure", "")) + " - " + str(trn.get("arrive", "")), ln=True)
    pdf.cell(0, 7, "Contact: " + str(tk.get("email", "")) + " | " + str(tk.get("phone", "")), ln=True)
    pdf.ln(5)
    pdf.set_font_size(13)
    pdf.cell(0, 8, "PASSENGERS:", ln=True)
    pdf.set_font_size(10)
    who = tk.get("persons") if tk.get("persons") else pl
    for p in who:
        pdf.ln(2)
        if type(p.get("seat")) is dict:
            sn = p["seat"].get("number", "?")
        else:
            sn = p.get("seatNumber", "?")
        pdf.cell(0, 6, "* " + tx(p.get("name", "")) + " " + tx(p.get("surname", "")) + " (ID: " + str(p.get("idNumber", "")) + ")", ln=True)
        pdf.cell(0, 6, "  Vagon: " + tx(p.get("vagonName", "")) + " | Seat: " + str(sn), ln=True)
    pdf.ln(5)
    pdf.set_font_size(12)
    pdf.cell(0, 8, "TOTAL: " + str(session.get("total", 0)) + " GEL", ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    tmp.close()
    return send_file(tmp.name, as_attachment=1, download_name="ticket_" + str(tk.get("id", "x")) + ".pdf", mimetype="application/pdf")


@app.route("/check_ticket")
def check_ticket():
    resp = make_response(render_template("check_ticket.html"))
    return resp


@app.route("/verify_ticket", methods=["POST"])
def verify_ticket():
    tid = request.form.get("ticket_id")
    if tid:
        tid = tid.strip()
    else:
        tid = ""

    found = g("/api/tickets/checkstatus/" + tid)
    if found is None or not found.get("id"):
        found = None
        lst = g("/api/tickets")
        if lst:
            for t in lst:
                if str(t.get("id")) == tid:
                    found = t
                    break
    if found is None and tid in mem:
        found = mem[tid]

    if found:
        return render_template("check_ticket.html", ticket=found, searched=True)
    err = "ბილეთი ვერ მოიძებნა"
    return render_template("check_ticket.html", error=err, searched=True)


@app.route("/cancel_ticket/<ticket_id>", methods=["POST"])
def cancel_ticket(ticket_id):
    done = False
    try:
        r = requests.delete(S + "/api/tickets/cancel/" + ticket_id, timeout=5)
        done = r.status_code == 200
    except Exception:
        done = False

    if ticket_id in mem:
        mem[ticket_id]["status"] = "Cancelled"
        mem[ticket_id]["confirmed"] = False
        done = True

    if done:
        return render_template("check_ticket.html", cancelled=True, ticket_id=ticket_id)
    return render_template("check_ticket.html", error="ბილეთის გაუქმება ვერ მოხერხდა")


if __name__ == "__main__":
    app.run(port=5000, debug=True)