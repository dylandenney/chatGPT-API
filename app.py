import os
import openai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sessions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)


db.create_all()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if "session_name" not in data or "content" not in data:
        return jsonify({"error": "Please provide session_name and content"}), 400

    session_name = data["session_name"]
    content = data["content"]

    prompt = f"[{session_name}]\n{content}\nResponse:"
    payload = {
        "prompt": prompt,
        "max_tokens": 150,
        "n": 1,
        "stop": "\n",
        "temperature": 0.8,
    }

    response = openai.Completion.create(engine="davinci-codex", **payload)

    response_text = response.choices[0].text.strip()

    session = Session(session_name=session_name, content=content, response=response_text)
    db.session.add(session)
    db.session.commit()

    return jsonify({"response": response_text})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

