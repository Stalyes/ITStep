from flask import Flask, render_template, request, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, random, string, tempfile
import requests
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "step-railway-secret-key-final"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Tornike31@localhost:5432/railway_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

API = "https://railway.stepprojects.ge"

DAYS_KA = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]

GEO_MAP = {
    'ა':'a','ბ':'b','გ':'g','დ':'d','ე':'e','ვ':'v','ზ':'z','თ':'t','ი':'i',
    'კ':'k','ლ':'l','მ':'m','ნ':'n','ო':'o','პ':'p','ჟ':'zh','რ':'r','ს':'s',
    'ტ':'t','უ':'u','ფ':'p','ქ':'k','ღ':'gh','ყ':'q','შ':'sh','ჩ':'ch','ც':'ts',
    'ძ':'dz','წ':'ts','ჭ':'ch','ხ':'kh','ჯ':'j','ჰ':'h'
}


# ============ MODELS ============

class Passenger(db.Model):
    __tablename__ = "passengers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    personal_id = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    tickets = db.relationship("Ticket", backref="passenger", lazy=True)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(50), unique=True, nullable=False)
    train_id = db.Column(db.Integer, nullable=False)
    departure_city = db.Column(db.String(100), nullable=False)
    arrival_city = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tickets = db.relationship("Ticket", backref="booking", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="booking", lazy=True, cascade="all, delete-orphan")


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey("passengers.id"), nullable=False)
    carriage_number = db.Column(db.String(50))
    seat_number = db.Column(db.String(20))
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============ HELPERS ============

def transliterate(s):
    if not s: return ""
    return "".join(GEO_MAP.get(c, c) for c in str(s))


def api_get(path):
    try:
        r = requests.get(API + path, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("api err:", e)
    return None


def make_ticket_code():
    return "GEO-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ============ ROUTES ============

@app.route("/")
def index():
    deps = api_get("/api/departures") or []
    cities = set()
    for d in deps:
        if d.get("source"): cities.add(d["source"].strip())
        if d.get("destination"): cities.add(d["destination"].strip())
    return render_template("index.html", cities=sorted(cities), days=DAYS_KA)


@app.route("/trains")
def trains():
    src = request.args.get("from_city", "").strip()
    dst = request.args.get("to_city", "").strip()
    day = request.args.get("date", "").strip()
    n = request.args.get("tickets", 1, type=int)

    session["src"] = src
    session["dst"] = dst
    session["day"] = day
    session["count"] = n

    all_deps = api_get("/api/departures") or []
    found = []
    for dep in all_deps:
        if dep.get("source", "").strip() != src: continue
        if dep.get("destination", "").strip() != dst: continue
        if dep.get("date", "").strip() != day: continue
        found.extend(dep.get("trains") or [])

    vagons_all = api_get("/api/vagons") or []
    for t in found:
        t["price"] = 25
        for v in vagons_all:
            if v.get("trainId") == t.get("id") and v.get("seats"):
                t["price"] = v["seats"][0].get("price", 25)
                break

    return render_template("trains.html",
                           trains=found, date=day, from_name=src,
                           to_name=dst, num_tickets=n)


@app.route("/passengers/<int:train_id>")
def passengers_page(train_id):
    session["train_id"] = train_id
    n = session.get("count", 1)

    train_obj = None
    for d in (api_get("/api/departures") or []):
        for t in (d.get("trains") or []):
            if t.get("id") == train_id:
                train_obj = t
                break
        if train_obj: break

    vg = [v for v in (api_get("/api/vagons") or []) if v.get("trainId") == train_id]

    if train_obj:
        train_obj["vagons"] = vg
    else:
        train_obj = {"id": train_id, "number": "?", "name": "მატარებელი",
                     "vagons": vg, "departure": "--:--", "arrive": "--:--"}

    session["train"] = train_obj

    return render_template("passengers.html", num_tickets=n, train=train_obj,
                           from_name=session.get("src", ""),
                           to_name=session.get("dst", ""),
                           date=session.get("day", ""))


@app.route("/api/vagon/<int:vagon_id>")
def api_vagon(vagon_id):
    # merge api data with locally-booked seat status
    for v in (api_get("/api/vagons") or []):
        if v.get("id") == vagon_id:
            # mark seats that already have tickets in our db
            booked_seat_numbers = set()
            active_tickets = db.session.query(Ticket).join(Booking).filter(
                Booking.status == "active",
                Booking.train_id == session.get("train_id", 0)
            ).all()
            for t in active_tickets:
                if t.seat_number:
                    booked_seat_numbers.add(str(t.seat_number))

            for seat in v.get("seats", []):
                if str(seat.get("number")) in booked_seat_numbers:
                    seat["isOccupied"] = True
            return jsonify(v)
    return jsonify({})


@app.route("/payment", methods=["POST"])
def payment():
    n = session.get("count", 1)
    session["email"] = request.form.get("email", "").strip()
    session["phone"] = request.form.get("phone", "").strip()

    plist = []
    for i in range(n):
        plist.append({
            "name": request.form.get(f"first_name_{i}", ""),
            "surname": request.form.get(f"last_name_{i}", ""),
            "idNumber": request.form.get(f"personal_id_{i}", ""),
            "seatId": request.form.get(f"seat_id_{i}", ""),
            "seatNumber": request.form.get(f"seat_number_{i}", ""),
            "vagonName": request.form.get(f"vagon_name_{i}", ""),
            "seatPrice": float(request.form.get(f"seat_price_{i}", 25) or 25),
        })

    session["plist"] = plist
    total = sum(p["seatPrice"] for p in plist)
    session["total"] = total

    return render_template("payment.html", total=total, passengers=plist,
                           train=session.get("train"),
                           from_name=session.get("src"),
                           to_name=session.get("dst"))


@app.route("/process_payment", methods=["POST"])
def process_payment():
    plist = session.get("plist", [])
    total = float(session.get("total", 0))
    train_info = session.get("train") or {}
    train_id = session.get("train_id", 0)

    # 1) create booking
    code = make_ticket_code()
    booking = Booking(
        ticket_code=code,
        train_id=train_id,
        departure_city=session.get("src", ""),
        arrival_city=session.get("dst", ""),
        departure_date=session.get("day", ""),
        departure_time=train_info.get("departure", ""),
        total_price=total,
        status="active",
    )
    db.session.add(booking)
    db.session.flush()

    email = session.get("email", "")
    phone = session.get("phone", "")

    # 2) passengers + 3) tickets
    for p in plist:
        pas = Passenger(
            first_name=p["name"],
            last_name=p["surname"],
            personal_id=p["idNumber"],
            email=email,
            phone=phone,
        )
        db.session.add(pas)
        db.session.flush()

        tk = Ticket(
            booking_id=booking.id,
            passenger_id=pas.id,
            carriage_number=p.get("vagonName"),
            seat_number=p.get("seatNumber"),
            price=p.get("seatPrice", 0),
        )
        db.session.add(tk)

    # 4) payment
    pay = Payment(
        booking_id=booking.id,
        amount=total,
        status="completed",
    )
    db.session.add(pay)
    db.session.commit()

    ticket_view = {
        "id": code,
        "email": email,
        "phone": phone,
        "date": session.get("day"),
        "ticketPrice": total,
        "confirmed": True,
        "status": "Active",
        "train": {
            "number": train_info.get("number"),
            "name": train_info.get("name"),
            "from": session.get("src"),
            "to": session.get("dst"),
            "departure": train_info.get("departure"),
            "arrive": train_info.get("arrive"),
        },
        "persons": [{
            "name": p["name"],
            "surname": p["surname"],
            "idNumber": p["idNumber"],
            "seat": {"number": p["seatNumber"]},
            "vagonName": p["vagonName"],
            "status": "active",
        } for p in plist],
    }
    session["ticket"] = ticket_view

    return render_template("ticket_result.html",
                           ticket=ticket_view,
                           train=train_info,
                           from_name=session.get("src"),
                           to_name=session.get("dst"),
                           date=session.get("day"),
                           total=total,
                           passengers=plist)


@app.route("/download_ticket")
def download_ticket():
    tk = session.get("ticket") or {}
    tr = session.get("train") or {}
    pl = session.get("plist") or []

    pdf = FPDF()
    pdf.add_page()

    font_ok = False
    for pth in [r"C:\Windows\Fonts\sylfaen.ttf", r"C:\Windows\Fonts\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(pth):
            try:
                pdf.add_font("Ka", fname=pth)
                pdf.set_font("Ka", size=12)
                font_ok = True
                break
            except:
                pass

    if not font_ok:
        pdf.set_font("Helvetica", size=12)

    def T(s):
        return str(s) if font_ok else transliterate(s)

    pdf.set_font_size(18)
    pdf.cell(0, 15, "RAILWAY TICKET", ln=True, align="C")
    pdf.ln(3)
    pdf.set_font_size(11)

    pdf.cell(0, 7, f"Ticket ID: {tk.get('id', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Route: {T(session.get('src',''))} -> {T(session.get('dst',''))}", ln=True)
    pdf.cell(0, 7, f"Day: {T(session.get('day',''))}", ln=True)

    if tr:
        pdf.cell(0, 7, f"Train #{tr.get('number','?')} ({T(tr.get('name',''))})", ln=True)
        pdf.cell(0, 7, f"Time: {tr.get('departure','?')} - {tr.get('arrive','?')}", ln=True)

    pdf.cell(0, 7, f"Contact: {tk.get('email','')} | {tk.get('phone','')}", ln=True)
    pdf.ln(5)
    pdf.set_font_size(13)
    pdf.cell(0, 8, "PASSENGERS:", ln=True)
    pdf.set_font_size(10)

    persons = tk.get("persons") or pl
    for p in persons:
        pdf.ln(2)
        if isinstance(p.get("seat"), dict):
            sn = p["seat"].get("number", "?")
        else:
            sn = p.get("seatNumber", "?")
        pdf.cell(0, 6, f"* {T(p.get('name',''))} {T(p.get('surname',''))} (ID: {p.get('idNumber','?')})", ln=True)
        pdf.cell(0, 6, f"  Vagon: {T(p.get('vagonName','?'))} | Seat: {sn}", ln=True)

    pdf.ln(5)
    pdf.set_font_size(12)
    pdf.cell(0, 8, f"TOTAL: {session.get('total', 0)} GEL", ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    tmp.close()

    return send_file(tmp.name, as_attachment=True,
                     download_name=f"ticket_{tk.get('id','x')}.pdf",
                     mimetype="application/pdf")


@app.route("/check_ticket")
def check_ticket():
    return render_template("check_ticket.html")


@app.route("/verify_ticket", methods=["POST"])
def verify_ticket():
    code = request.form.get("ticket_id", "").strip()

    booking = Booking.query.filter_by(ticket_code=code).first()
    if not booking:
        return render_template("check_ticket.html", error="ბილეთი ვერ მოიძებნა", searched=True)

    persons = []
    for t in booking.tickets:
        pas = t.passenger
        persons.append({
            "name": pas.first_name,
            "surname": pas.last_name,
            "idNumber": pas.personal_id,
            "seat": {"number": t.seat_number},
            "vagonName": t.carriage_number,
        })

    email = booking.tickets[0].passenger.email if booking.tickets else ""
    phone = booking.tickets[0].passenger.phone if booking.tickets else ""

    ticket_view = {
        "id": booking.ticket_code,
        "email": email,
        "phone": phone,
        "date": booking.departure_date,
        "ticketPrice": float(booking.total_price),
        "confirmed": booking.status == "active",
        "status": "Active" if booking.status == "active" else "Cancelled",
        "train": {
            "number": booking.train_id,
            "name": f"{booking.departure_city}-{booking.arrival_city}",
            "from": booking.departure_city,
            "to": booking.arrival_city,
            "departure": booking.departure_time,
        },
        "persons": persons,
    }

    return render_template("check_ticket.html", ticket=ticket_view, searched=True)


@app.route("/cancel_ticket/<ticket_id>", methods=["POST"])
def cancel_ticket(ticket_id):
    booking = Booking.query.filter_by(ticket_code=ticket_id).first()
    if not booking:
        return render_template("check_ticket.html", error="ბილეთის გაუქმება ვერ მოხერხდა")

    booking.status = "cancelled"

    # mark payment as refunded (optional)
    for pay in booking.payments:
        pay.status = "refunded"

    db.session.commit()
    return render_template("check_ticket.html", cancelled=True, ticket_id=ticket_id)


# create tables on startup if missing
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
