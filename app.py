from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)


# ---------------- DATABASE CONNECTION ----------------

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


# ---------------- CREATE TABLES ----------------

def create_tables():

    con = get_db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        id SERIAL PRIMARY KEY,
        customer_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        vehicle TEXT NOT NULL,
        pickup_date TEXT NOT NULL,
        return_date TEXT NOT NULL,
        pickup_location TEXT NOT NULL,
        return_location TEXT NOT NULL,
        payment TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)

    con.commit()
    cur.close()
    con.close()


# ---------------- LOGIN ----------------

@app.route("/")
def login():
    return render_template("login.html")


# ---------------- REGISTER PAGE ----------------

@app.route("/register")
def register():
    return render_template("register.html")


# ---------------- SAVE USER ----------------

@app.route("/save", methods=["POST"])
def save():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    con = get_db()
    cur = con.cursor()

    try:
        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )

        con.commit()

    except psycopg2.errors.UniqueViolation:
        con.rollback()
        cur.close()
        con.close()

        return render_template(
            "register.html",
            error="Email already registered!"
        )

    cur.close()
    con.close()

    return redirect("/")


# ---------------- LOGIN CHECK ----------------

@app.route("/login", methods=["POST"])
def check_login():

    email = request.form["email"]
    password = request.form["password"]

    con = get_db()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cur.fetchone()

    cur.close()
    con.close()

    if user:
        return redirect("/home")

    return render_template(
        "login.html",
        error="Invalid email or password!"
    )


# ---------------- HOME ----------------

@app.route("/home")
def home():
    return render_template("home.html")


# ---------------- VEHICLES ----------------

@app.route("/vehicles")
def vehicles():
    return render_template("vehicles.html")


# ---------------- BOOKING PAGE ----------------

@app.route("/booking")
def booking():

    vehicle = request.args.get("vehicle")
    image = request.args.get("image")

    return render_template(
        "booking.html",
        vehicle=vehicle,
        image=image
    )


# ---------------- CONFIRM BOOKING ----------------

@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():

    customer_name = request.form["customer_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    vehicle = request.form["vehicle"]
    pickup_date = request.form["pickup_date"]
    return_date = request.form["return_date"]
    pickup_location = request.form["pickup_location"]
    return_location = request.form["return_location"]
    payment = request.form["payment"]

    con = get_db()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO bookings
    (customer_name, email, phone, vehicle,
     pickup_date, return_date,
     pickup_location, return_location, payment)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        customer_name,
        email,
        phone,
        vehicle,
        pickup_date,
        return_date,
        pickup_location,
        return_location,
        payment
    ))

    con.commit()

    cur.close()
    con.close()

    return redirect(
        f"/booking_success?"
        f"customer_name={customer_name}"
        f"&vehicle={vehicle}"
        f"&pickup_date={pickup_date}"
        f"&return_date={return_date}"
        f"&payment={payment}"
    )


# ---------------- BOOKING SUCCESS ----------------

@app.route("/booking_success")
def booking_success():

    customer_name = request.args.get("customer_name")
    vehicle = request.args.get("vehicle")
    pickup_date = request.args.get("pickup_date")
    return_date = request.args.get("return_date")
    payment = request.args.get("payment")

    return render_template(
        "booking_success.html",
        customer_name=customer_name,
        vehicle=vehicle,
        pickup_date=pickup_date,
        return_date=return_date,
        payment=payment
    )


# ---------------- MY BOOKINGS ----------------

@app.route("/my_bookings")
def my_bookings():

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "mybookings.html",
        bookings=bookings
    )


# ---------------- CONTACT ----------------

@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------- SEND MESSAGE ----------------

@app.route("/send_message", methods=["POST"])
def send_message():

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    con = get_db()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO contact_messages
    (name,email,subject,message)
    VALUES(%s,%s,%s,%s)
    """,
    (name, email, subject, message))

    con.commit()

    cur.close()
    con.close()

    return redirect("/message_success")


# ---------------- MESSAGE SUCCESS ----------------

@app.route("/message_success")
def message_success():
    return render_template("success.html")


# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cur.fetchone()[0]

    cur.close()
    con.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_bookings=total_bookings,
        total_messages=total_messages
    )


# ---------------- ADMIN USERS ----------------

@app.route("/admin/users")
def admin_users():

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM users ORDER BY id DESC")
    users = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# ---------------- ADMIN BOOKINGS ----------------

@app.route("/admin/bookings")
def admin_bookings():

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


# ---------------- ADMIN MESSAGES ----------------

@app.route("/admin/messages")
def admin_messages():

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM contact_messages ORDER BY id DESC")
    messages = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "admin_messages.html",
        messages=messages
    )


# ---------------- START APP ----------------

if __name__ == "__main__":
    create_tables()
    app.run()