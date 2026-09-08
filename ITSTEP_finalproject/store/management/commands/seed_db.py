from django.core.management.base import BaseCommand
from store.models import Station, Train, Wagon, Seat

DAYS_KA = ["ორშაბათი", "სამშაბათი", "ოთხშაბათი", "ხუთშაბათი", "პარასკევი", "შაბათი", "კვირა"]

class Command(BaseCommand):
    help = 'Seeds initial database data for stations, trains, wagons, and seats'

    def handle(self, *args, **kwargs):
        if Train.objects.exists():
            self.stdout.write('Database already seeded.')
            return

        cities = ["თბილისი", "ბათუმი", "ფოთი", "ქუთაისი", "ზუგდიდი"]
        for c in cities:
            Station.objects.get_or_create(name=c)

        routes = [
            ("თბილისი", "ბათუმი"), ("ბათუმი", "თბილისი"),
            ("თბილისი", "ფოთი"), ("ფოთი", "თბილისი"),
            ("თბილისი", "ქუთაისი"), ("ქუთაისი", "თბილისი"),
            ("თბილისი", "ზუგდიდი"), ("ზუგდიდი", "თბილისი"),
        ]

        schedules = [
            (812, "00:35", "05:47"),
            (808, "10:25", "15:38"),
            (804, "17:05", "22:17"),
        ]

        seat_labels = [f"{row}{col}" for row in range(1, 11) for col in ["A", "B", "C", "D"]]

        for src, dst in routes:
            for day in DAYS_KA:
                for num, dep, arr in schedules:
                    train = Train.objects.create(
                        train_number=num,
                        train_name=f"{src}-{dst}",
                        departure_city=src,
                        arrival_city=dst,
                        weekday=day,
                        departure_time=dep,
                        arrival_time=arr
                    )

                    w1 = Wagon.objects.create(train=train, wagon_number=1, wagon_class="I კლასი")
                    w2 = Wagon.objects.create(train=train, wagon_number=2, wagon_class="II კლასი")

                    for lbl in seat_labels:
                        Seat.objects.create(wagon=w1, seat_label=lbl, price=35.00)
                        Seat.objects.create(wagon=w2, seat_label=lbl, price=25.00)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))