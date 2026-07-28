from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create table
con = sqlite3.connect("users.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

con.commit()
con.close()

# Create bookings table

con = sqlite3.connect("users.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

con.commit()
con.close()

# Create Contact Messages Table

con = sqlite3.connect("users.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS contact_messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL
)
""")

con.commit()
con.close()


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/save", methods=["POST"])
def save():

    print("SAVE ROUTE CALLED")

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        (name, email, password)
    )

    con.commit()
    con.close()

    return redirect("/")
@app.route("/login", methods=["POST"])
def check_login():

    email = request.form["email"]
    password = request.form["password"]

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cur.fetchone()

    con.close()

    if user:
        return redirect("/home")
    else:
        return render_template(
            "login.html",
            error="Invalid email or password!"
        )


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/vehicles")
def vehicles():
    return render_template("vehicles.html")

@app.route("/booking")
def booking():

    vehicle = request.args.get("vehicle")
    image = request.args.get("image")

    return render_template(
        "booking.html",
        vehicle=vehicle,
        image=image
    )



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

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("""
    INSERT INTO bookings
    (customer_name, email, phone, vehicle,
     pickup_date, return_date,
     pickup_location, return_location, payment)
    VALUES(?,?,?,?,?,?,?,?,?)
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
    con.close()

    return redirect(
    f"/booking_success?"
    f"customer_name={customer_name}"
    f"&vehicle={vehicle}"
    f"&pickup_date={pickup_date}"
    f"&return_date={return_date}"
    f"&payment={payment}"
)


    
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

@app.route("/my_bookings")
def my_bookings():

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()

    con.close()

    return render_template("mybookings.html", bookings=bookings)

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/send_message", methods=["POST"])
def send_message():

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("""
    INSERT INTO contact_messages(name,email,subject,message)
    VALUES(?,?,?,?)
    """,
    (name, email, subject, message))

    con.commit()
    con.close()

    return redirect("/message_success")


@app.route("/message_success")
def message_success():
    return render_template("success.html")


@app.route("/admin")
def admin():

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cur.fetchone()[0]

    con.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_bookings=total_bookings,
        total_messages=total_messages
    )

@app.route("/admin/users")
def admin_users():

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    con.close()

    return render_template(
        "admin_users.html",
        users=users
    )

@app.route("/admin/bookings")
def admin_bookings():

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()

    con.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


@app.route("/admin/messages")
def admin_messages():

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM contact_messages")
    messages = cur.fetchall()

    con.close()

    return render_template(
        "admin_messages.html",
        messages=messages
    )


if __name__ == "__main__":
    app.run(debug=True)