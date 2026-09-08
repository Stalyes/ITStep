from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from store.models import Station, Train, Wagon, Seat, Booking, Passenger, Ticket, Payment
from api.serializers import WagonSerializer
import os
import random
import re
import string
import tempfile
from datetime import date, datetime
from fpdf import FPDF

DAYS_KA = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]

GEO_MAP = {
    'ა':'a','ბ':'b','გ':'g','დ':'d','ე':'e','ვ':'v','ზ':'z','თ':'t','ი':'i',
    'კ':'k','ლ':'l','მ':'m','ნ':'n','ო':'o','პ':'p','ჟ':'zh','რ':'r','ს':'s',
    'ტ':'t','უ':'u','ფ':'p','ქ':'k','ღ':'gh','ყ':'q','შ':'sh','ჩ':'ch','ც':'ts',
    'ძ':'dz','წ':'ts','ჭ':'ch','ხ':'kh','ჯ':'j','ჰ':'h'
}

def transliterate(s):
    if not s:
        return ""
    return "".join(GEO_MAP.get(c, c) for c in str(s))

def index(request):
    cities = Station.objects.values_list('name', flat=True).order_by('name')
    return render(request, "index.html", {
        'cities': cities,
        'min_date': date.today().isoformat(),
    })

def trains(request):
    src = request.GET.get("from_city", "").strip()
    dst = request.GET.get("to_city", "").strip()
    selected_date = request.GET.get("date", "").strip()
    try:
        departure_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "index.html", {
            'cities': Station.objects.values_list('name', flat=True).order_by('name'),
            'min_date': date.today().isoformat(),
            'error': "გთხოვთ აირჩიოთ სწორი გამგზავრების თარიღი.",
        })

    if departure_date < date.today():
        return render(request, "index.html", {
            'cities': Station.objects.values_list('name', flat=True).order_by('name'),
            'min_date': date.today().isoformat(),
            'error': "წარსული თარიღის არჩევა შეუძლებელია.",
        })

    day = DAYS_KA[departure_date.weekday()]
    try:
        n = max(1, min(5, int(request.GET.get("tickets", 1))))
    except ValueError:
        n = 1

    request.session["src"] = src
    request.session["dst"] = dst
    request.session["day"] = selected_date
    request.session["weekday"] = day
    request.session["count"] = n

    trains_qs = Train.objects.filter(departure_city=src, arrival_city=dst, weekday=day)
    
    found = []
    for t in trains_qs:
        first_seat = Seat.objects.filter(wagon__train=t).first()
        price = float(first_seat.price) if first_seat else 25.0
        found.append({
            "id": t.id,
            "number": t.train_number,
            "name": t.train_name,
            "from": t.departure_city,
            "to": t.arrival_city,
            "departure": t.departure_time,
            "arrive": t.arrival_time,
            "price": price
        })

    return render(request, "trains.html", {
        "trains": found, "date": selected_date, "from_name": src, "to_name": dst, "num_tickets": n
    })

def passengers_page(request, train_id):
    request.session["train_id"] = train_id
    n = request.session.get("count", 1)

    t = get_object_or_404(Train, id=train_id)
    wagons = Wagon.objects.filter(train=t)

    train_data = {
        "id": t.id,
        "number": t.train_number,
        "name": t.train_name,
        "departure": t.departure_time,
        "arrive": t.arrival_time,
        "wagons": [{"id": w.id, "name": f"ვაგონი {w.wagon_number} ({w.wagon_class})"} for w in wagons]
    }
    request.session["train"] = train_data

    return render(request, "passengers.html", {
        "num_tickets": n, "train": train_data,
        "from_name": request.session.get("src", ""),
        "to_name": request.session.get("dst", ""),
        "date": request.session.get("day", "")
    })

def vagon_seats_ajax(request, vagon_id):
    try:
        wagon = Wagon.objects.get(id=vagon_id)
        serializer = WagonSerializer(wagon)
        return JsonResponse(serializer.data)
    except Wagon.DoesNotExist:
        return JsonResponse({})

def payment(request):
    if request.method == "POST":
        n = request.session.get("count", 1)
        request.session["email"] = request.POST.get("email", "").strip()
        request.session["phone"] = request.POST.get("phone", "").strip()

        plist = []
        for i in range(n):
            plist.append({
                "name": request.POST.get(f"first_name_{i}", ""),
                "surname": request.POST.get(f"last_name_{i}", ""),
                "idNumber": request.POST.get(f"personal_id_{i}", ""),
                "seatId": request.POST.get(f"seat_id_{i}", ""),
                "seatNumber": request.POST.get(f"seat_number_{i}", ""),
                "vagonName": request.POST.get(f"vagon_name_{i}", ""),
                "seatPrice": float(request.POST.get(f"seat_price_{i}", 25) or 25),
            })

        request.session["plist"] = plist
        total = sum(p["seatPrice"] for p in plist)
        request.session["total"] = total

        return render(request, "payment.html", {
            "total": total, "passengers": plist,
            "train": request.session.get("train"),
            "from_name": request.session.get("src"),
            "to_name": request.session.get("dst")
        })
    return redirect("/")

def process_payment(request):
    if request.method == "POST":
        plist = request.session.get("plist", [])
        total = float(request.session.get("total", 0))
        train_info = request.session.get("train") or {}
        train_id = request.session.get("train_id", 0)

        card_number = re.sub(r"\s+", "", request.POST.get("card_number", ""))
        expiry = request.POST.get("expiry", "")
        cvv = request.POST.get("cvv", "")
        if (not re.fullmatch(r"\d{16}", card_number)
                or not re.fullmatch(r"\d{2}/\d{2}", expiry)
                or not re.fullmatch(r"\d{3}", cvv)
                or not request.POST.get("card_name", "").strip()):
            return render(request, "payment.html", {
                "total": total, "passengers": plist, "train": train_info,
                "from_name": request.session.get("src"),
                "to_name": request.session.get("dst"),
                "error": "გთხოვთ შეიყვანოთ ბარათის სწორი მონაცემები.",
            })

        train = Train.objects.get(id=train_id)
        email = request.session.get("email", "")
        phone = request.session.get("phone", "")

        try:
            seat_ids = [int(p["seatId"]) for p in plist]
        except (KeyError, TypeError, ValueError):
            seat_ids = []

        if len(seat_ids) != len(plist) or len(set(seat_ids)) != len(seat_ids):
            return render(request, "payment.html", {
                "total": total, "passengers": plist, "train": train_info,
                "from_name": request.session.get("src"),
                "to_name": request.session.get("dst"),
                "error": "თითოეულ მგზავრს განსხვავებული ადგილი უნდა ჰქონდეს.",
            })

        with transaction.atomic():
            seats = list(Seat.objects.select_for_update().filter(
                id__in=seat_ids, wagon__train=train
            ))
            if len(seats) != len(seat_ids) or Ticket.objects.filter(
                    seat_id__in=seat_ids, booking__status="active").exists():
                return render(request, "payment.html", {
                    "total": total, "passengers": plist, "train": train_info,
                    "from_name": request.session.get("src"),
                    "to_name": request.session.get("dst"),
                    "error": "არჩეული ადგილი უკვე დაჯავშნილია. გთხოვთ დაბრუნდეთ და აირჩიოთ სხვა ადგილი.",
                })

            code = 'GEO-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ticket_code=code,
                train=train,
                departure_city=train.departure_city,
                arrival_city=train.arrival_city,
                departure_date=request.session.get("day", ""),
                departure_time=train.departure_time,
                total_price=total,
                status="active"
            )

            seat_by_id = {seat.id: seat for seat in seats}
            for p in plist:
                seat = seat_by_id[int(p["seatId"])]
                pas = Passenger.objects.create(
                    first_name=p["name"], last_name=p["surname"],
                    personal_id=p["idNumber"], email=email, phone=phone
                )
                Ticket.objects.create(
                    booking=booking, passenger=pas, seat=seat,
                    carriage_number=p.get("vagonName"),
                    seat_number=p.get("seatNumber"), price=p.get("seatPrice", 0)
                )

            Payment.objects.create(booking=booking, amount=total, status="completed")

        ticket_view = {
            "id": code,
            "email": email,
            "phone": phone,
            "date": request.session.get("day"),
            "ticketPrice": total,
            "confirmed": True,
            "status": "Active",
            "train": train_info,
            "persons": [{
                "name": p["name"],
                "surname": p["surname"],
                "idNumber": p["idNumber"],
                "seat": {"number": p["seatNumber"]},
                "vagonName": p["vagonName"],
            } for p in plist],
        }
        request.session["ticket"] = ticket_view

        return render(request, "ticket_result.html", {
            "ticket": ticket_view,
            "train": train_info,
            "from_name": request.session.get("src"),
            "to_name": request.session.get("dst"),
            "date": request.session.get("day"),
            "total": total,
            "passengers": plist
        })
    return redirect("/")

def download_ticket(request):
    tk = request.session.get("ticket") or {}
    tr = request.session.get("train") or {}
    pl = request.session.get("plist") or []

    pdf = FPDF()
    pdf.add_page()

    font_ok = False
    for pth in [r"C:\Windows\Fonts\sylfaen.ttf", r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(pth):
            try:
                pdf.add_font("Ka", fname=pth)
                pdf.set_font("Ka", size=12)
                font_ok = True
                break
            except: pass

    if not font_ok:
        pdf.set_font("Helvetica", size=12)

    def translate(s):
        return str(s) if font_ok else transliterate(s)

    pdf.set_font_size(18)
    pdf.cell(0, 15, "RAILWAY TICKET", ln=True, align="C")
    pdf.ln(3)
    pdf.set_font_size(11)

    pdf.cell(0, 7, f"Ticket ID: {tk.get('id', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Route: {translate(request.session.get('src', ''))} -> {translate(request.session.get('dst', ''))}", ln=True)
    pdf.cell(0, 7, f"Day: {translate(request.session.get('day', ''))}", ln=True)

    if tr:
        pdf.cell(0, 7, f"Train #{tr.get('number', '?')} ({translate(tr.get('name', ''))})", ln=True)
        pdf.cell(0, 7, f"Time: {tr.get('departure', '?')} - {tr.get('arrive', '?')}", ln=True)

    pdf.cell(0, 7, f"Contact: {tk.get('email','')} | {tk.get('phone','')}", ln=True)
    pdf.ln(5)
    pdf.set_font_size(13)
    pdf.cell(0, 8, "PASSENGERS:", ln=True)
    pdf.set_font_size(10)

    for p in (tk.get("persons") or pl):
        pdf.ln(2)
        sn = p["seat"]["number"] if isinstance(p.get("seat"), dict) else p.get("seatNumber", "?")
        pdf.cell(0, 6, f"* {translate(p.get('name', ''))} {translate(p.get('surname', ''))} (ID: {p.get('idNumber', '?')})", ln=True)
        pdf.cell(0, 6, f"  Vagon: {translate(p.get('vagonName', '?'))} | Seat: {sn}", ln=True)

    pdf.ln(5)
    pdf.set_font_size(12)
    pdf.cell(0, 8, f"TOTAL: {request.session.get('total', 0)} GEL", ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    tmp.close()

    with open(tmp.name, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{tk.get("id", "x")}.pdf"'
        return response

def check_ticket(request):
    return render(request, "check_ticket.html")

def verify_ticket(request):
    if request.method == "POST":
        code = request.POST.get("ticket_id", "").strip()

        try:
            booking = Booking.objects.get(ticket_code=code)
        except Booking.DoesNotExist:
            return render(request, "check_ticket.html", {"error": "ბილეთი ვერ მოიძებნა", "searched": True})

        persons = []
        for t in booking.tickets.all():
            pas = t.passenger
            persons.append({
                "name": pas.first_name,
                "surname": pas.last_name,
                "idNumber": pas.personal_id,
                "seat": {"number": t.seat_number},
                "vagonName": t.carriage_number,
            })

        first_ticket = booking.tickets.first()
        email = first_ticket.passenger.email if first_ticket else ""
        phone = first_ticket.passenger.phone if first_ticket else ""

        ticket_view = {
            "id": booking.ticket_code,
            "email": email,
            "phone": phone,
            "date": booking.departure_date,
            "ticketPrice": float(booking.total_price),
            "confirmed": booking.status == "active",
            "status": "Active" if booking.status == "active" else "Cancelled",
            "train": {
                "number": booking.train.train_number,
                "name": f"{booking.departure_city}-{booking.arrival_city}",
                "from": booking.departure_city,
                "to": booking.arrival_city,
                "departure": booking.departure_time,
            },
            "persons": persons,
        }

        return render(request, "check_ticket.html", {"ticket": ticket_view, "searched": True})
    return redirect("/check_ticket")

def cancel_ticket(request, ticket_id):
    if request.method == "POST":
        try:
            booking = Booking.objects.get(ticket_code=ticket_id)
            booking.status = "cancelled"
            booking.save()

            Payment.objects.filter(booking=booking).update(status="refunded")
            return render(request, "check_ticket.html", {"cancelled": True, "ticket_id": ticket_id})
        except Booking.DoesNotExist:
            return render(request, "check_ticket.html", {"error": "ბილეთის გაუქმება ვერ მოხერხდა"})
    return redirect("/check_ticket")
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if User.objects.filter(username=username).exists():
            messages.error(request, "ეს მომხმარებლის სახელი უკვე დაკავებულია.")
            return redirect('register')
            
        if password != confirm:
            messages.error(request, "პაროლები არ ემთხვევა ერთმანეთს.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username", "").strip()
        p = request.POST.get("password", "")
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "არასწორი სახელი ან პაროლი.")
            return redirect('login')
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('index')