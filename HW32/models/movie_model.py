import os
from pymongo import MongoClient

# MongoDB კავშირი
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://tornikeodo_db_user:K4U58btMUGN3lE2P@strongcluster.toj2pmh.mongodb.net/?appName=strongcluster"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["shop"]
movies_collection = db["movies"]

INITIAL_MOVIES = [
    {"title": "Inception", "year": 2010, "rating": 8.8, "genre": "Sci-Fi", "duration": 148},
    {"title": "The Matrix", "year": 1999, "rating": 8.7, "genre": "Action", "duration": 136},
    {"title": "Interstellar", "year": 2014, "rating": 8.6, "genre": "Sci-Fi", "duration": 169},
    {"title": "The Godfather", "year": 1972, "rating": 9.2, "genre": "Crime", "duration": 175},
    {"title": "Pulp Fiction", "year": 1994, "rating": 8.9, "genre": "Crime", "duration": 154},
    {"title": "The Dark Knight", "year": 2008, "rating": 9.0, "genre": "Action", "duration": 152},
    {"title": "The Matrix", "year": 1999, "rating": 8.7, "genre": "Sci-Fi", "duration": 136},
    {"title": "Interstellar", "year": 2014, "rating": 8.6, "genre": "Sci-Fi", "duration": 169},
    {"title": "The Dark Knight", "year": 2008, "rating": 9.0, "genre": "Action", "duration": 152},
    {"title": "Fight Club", "year": 1999, "rating": 8.8, "genre": "Drama", "duration": 139},
    {"title": "Forrest Gump", "year": 1994, "rating": 8.8, "genre": "Drama", "duration": 142},
    {"title": "Gladiator", "year": 2000, "rating": 8.5, "genre": "Action", "duration": 155},
    {"title": "The Shawshank Redemption", "year": 1994, "rating": 9.3, "genre": "Drama", "duration": 142},
    {"title": "The Prestige", "year": 2006, "rating": 8.5, "genre": "Drama", "duration": 130},
    {"title": "Avatar", "year": 2009, "rating": 7.8, "genre": "Sci-Fi", "duration": 162},
    {"title": "Whiplash", "year": 2014, "rating": 8.5, "genre": "Drama", "duration": 106},
    {"title": "Joker", "year": 2019, "rating": 8.4, "genre": "Drama", "duration": 122},
    {"title": "Parasite", "year": 2019, "rating": 8.5, "genre": "Thriller", "duration": 132},
    {"title": "The Wolf of Wall Street", "year": 2013, "rating": 8.2, "genre": "Biography", "duration": 180},
    {"title": "Mad Max: Fury Road", "year": 2015, "rating": 8.1, "genre": "Action", "duration": 120},
    {"title": "Django Unchained", "year": 2012, "rating": 8.4, "genre": "Western", "duration": 165}
]


class MovieModel:
    @staticmethod
    def seed_data():
        """თუ კოლექცია ცარიელია, შეაქვს საწყისი ფილმები"""
        if movies_collection.count_documents({}) == 0:
            movies_collection.insert_many(INITIAL_MOVIES)

    @staticmethod
    def get_all_movies():
        """ყველა ფილმის წამოღება"""
        MovieModel.seed_data()
        return list(movies_collection.find({}, {"_id": 0}))

    @staticmethod
    def get_total_count():
        """ფილმების საერთო რაოდენობა"""
        return movies_collection.count_documents({})

    @staticmethod
    def get_average_duration():
        """ფილმების საშუალო ხანგრძლივობის გამოთვლა (წუთებში)"""
        pipeline = [
            {"$group": {"_id": None, "avg_duration": {"$avg": "$duration"}}}
        ]
        result = list(movies_collection.aggregate(pipeline))
        if result and "avg_duration" in result[0]:
            return round(result[0]["avg_duration"], 2)
        return 0.0