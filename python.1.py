from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from textblob import TextBlob
import datetime

app = Flask(_name_)

def init_db():
    conn = sqlite3.connect("wellness.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mood
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  mood TEXT,
                  note TEXT,
                  sentiment REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mood = request.form["mood"]
        note = request.form["note"]

        sentiment_score = TextBlob(note).sentiment.polarity

        conn = sqlite3.connect("wellness.db")
        c = conn.cursor()
        c.execute("INSERT INTO mood (date, mood, note, sentiment) VALUES (?, ?, ?, ?)",
                  (datetime.date.today(), mood, note, sentiment_score))
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("wellness.db")
    c = conn.cursor()
    c.execute("SELECT date, mood, sentiment FROM mood")
    data = c.fetchall()
    conn.close()

    recommendations = []
    if data:
        avg_sentiment = sum([d[2] for d in data]) / len(data)
        if avg_sentiment < 0:
            recommendations.append("You seem stressed. Try meditation or deep breathing.")
        elif avg_sentiment < 0.3:
            recommendations.append("Take a short walk or talk to a friend.")
        else:
            recommendations.append("Great job! Keep up your positive mindset.")

    return render_template("dashboard.html", data=data, recommendations=recommendations)

if _name_ == "_main_":
    app.run(debug=True)
