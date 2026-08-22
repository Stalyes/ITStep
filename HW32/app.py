from flask import Flask
from controllers.movie_controler import index_action

app = Flask(__name__)


# მთავარი მარშრუტი (Route -> Controller -> Model & View)
@app.route("/")
def home():
    return index_action()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)