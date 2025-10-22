
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g
import sqlite3
from datetime import datetime, date
import csv
import io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devsecret123")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        branch_name TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT,
        date TEXT,
        am_sales REAL,
        am_rooms INTEGER,
        pm_sales REAL,
        pm_rooms INTEGER,
        total_sales REAL,
        created_at TEXT
    )
    """)
    conn.commit()
    # Seed admin and branches if not exist
    users = [
        ("admin", "admin123", "admin", None),
        ("Jacob Main".lower().replace(" ", "_"), "pass123", "branch", "Jacob Main"),
        ("Jacob Annex".lower().replace(" ", "_"), "pass123", "branch", "Jacob Annex"),
        ("Concepcion".lower().replace(" ", "_"), "pass123", "branch", "Concepcion"),
        ("Legazpi".lower().replace(" ", "_"), "pass123", "branch", "Legazpi"),
        ("Daet".lower().replace(" ", "_"), "pass123", "branch", "Daet"),
        ("Pili Main".lower().replace(" ", "_"), "pass123", "branch", "Pili Main"),
        ("Pili Annex".lower().replace(" ", "_"), "pass123", "branch", "Pili Annex"),
        ("Diversion".lower().replace(" ", "_"), "pass123", "branch", "Diversion"),
        ("Tabuc Main".lower().replace(" ", "_"), "pass123", "branch", "Tabuc Main"),
        ("Tabuc Annex".lower().replace(" ", "_"), "pass123", "branch", "Tabuc Annex"),
    ]
    # Insert if not exists
    for u, p, r, b in users:
        cur.execute("SELECT id FROM users WHERE username=?", (u,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO users (username, password, role, branch_name) VALUES (?, ?, ?, ?)", (u, p, r, b))
    conn.commit()
    conn.close()

# Initialize DB on first run
if not os.path.exists(DB_PATH):
    init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["branch_name"] = user["branch_name"]
            flash("Logged in successfully.", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("branch_form"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/branch", methods=["GET", "POST"])
def branch_form():
    if session.get("role") != "branch":
        return redirect(url_for("login"))
    branch = session.get("branch_name")
    if request.method == "POST":
        date_str = request.form.get("date") or date.today().isoformat()
        try:
            am_sales = float(request.form.get("am_sales") or 0)
        except:
            am_sales = 0.0
        try:
            pm_sales = float(request.form.get("pm_sales") or 0)
        except:
            pm_sales = 0.0
        try:
            am_rooms = int(request.form.get("am_rooms") or 0)
        except:
            am_rooms = 0
        try:
            pm_rooms = int(request.form.get("pm_rooms") or 0)
        except:
            pm_rooms = 0
        total = am_sales + pm_sales
        db = get_db()
        db.execute("""INSERT INTO sales (branch_name, date, am_sales, am_rooms, pm_sales, pm_rooms, total_sales, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (branch, date_str, am_sales, am_rooms, pm_sales, pm_rooms, total, datetime.now().isoformat()))
        db.commit()
        flash("Daily sales submitted.", "success")
        return redirect(url_for("branch_form"))
    # show recent entries for this branch
    db = get_db()
    cur = db.execute("SELECT * FROM sales WHERE branch_name=? ORDER BY date DESC LIMIT 50", (branch,))
    rows = cur.fetchall()
    return render_template("branch_form.html", branch=branch, rows=rows)

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    db = get_db()
    cur = db.execute("SELECT * FROM sales ORDER BY date DESC")
    rows = cur.fetchall()
    # totals per branch
    cur2 = db.execute("SELECT branch_name, SUM(total_sales) as total, SUM(am_rooms+pm_rooms) as total_rooms FROM sales GROUP BY branch_name")
    totals = cur2.fetchall()
    return render_template("admin_view.html", rows=rows, totals=totals)

@app.route("/export_csv")
def export_csv():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    db = get_db()
    cur = db.execute("SELECT * FROM sales ORDER BY date DESC")
    rows = cur.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","branch_name","date","am_sales","am_rooms","pm_sales","pm_rooms","total_sales","created_at"])
    for r in rows:
        writer.writerow([r["id"], r["branch_name"], r["date"], r["am_sales"], r["am_rooms"], r["pm_sales"], r["pm_rooms"], r["total_sales"], r["created_at"]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype="text/csv", as_attachment=True, download_name="sales_export.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
