from flask import render_template
from models.movie_model import MovieModel


def index_action():
    # 1. წამოვიღოთ ყველა ფილმი ბაზიდან
    movies = MovieModel.get_all_movies()

    # 2. დინამიურად დავთვალოთ რაოდენობა და საშუალო ხანგრძლივობა
    total_movies = MovieModel.get_total_count()
    avg_duration = MovieModel.get_average_duration()

    # 3. გადავცეთ View-ს (HTML შაბლონს)
    return render_template(
        "index.html",
        movies=movies,
        total_movies=total_movies,
        avg_duration=avg_duration,
    )