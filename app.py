import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wtm.db")


# Ensure that the responses from your Flask application are not cached by the client's browser
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # display homepage
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # user reached route via GET
    if request.method == "GET":
        return render_template("add.html")

    # user reached route via POST
    else:
        # retrieve and validate name
        name = request.form.get("name")
        if not name:
            return apology("Please input name", 400)
        rows = db.execute("SELECT * FROM events WHERE name = :name", name=name)
        if len(rows) > 0:
            return apology("Name already taken", 400)

        # retrieve and validate city
        city = request.form.get("city")
        if not city:
            return apology("Please input city", 400)

        # retrieve and validate state
        state = request.form.get("state")
        if len(state) > 2:
            return apology("Please input state abbreviation", 400)
        if not state:
            return apology("Please input state", 400)

        # retrieve and validate address
        address = request.form.get("address")
        if not address:
            return apology("Please input address", 400)

        # retrieve and validate month
        try:
            month = int(request.form.get("month"))
        except ValueError:
            return apology("Please input valid month", 400)
        if not month:
            return apology("Please input month", 400)
        if month < 1 or month > 12:
            return apology("Please input valid month", 400)

        # retrieve and validate date
        try:
            date = int(request.form.get("date"))
        except ValueError:
            return apology("Please input valid date", 400)
        if not date:
            return apology("Please input date", 400)
        if date < 1 or date > 31:
            return apology("Please input valid date", 400)

        # retrieve additional comments
        comments = request.form.get("comments")
        if not comments:
            return apology("Please input comments", 400)

        # insert row into events column
        if not comments:
            db.execute(
                "INSERT INTO events (name, city, state, address, month, date, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                name,
                city,
                state,
                address,
                month,
                date,
                session["user_id"],
            )
        else:
            db.execute(
                "INSERT INTO events (name, city, state, address, comments, month, date, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                name,
                city,
                state,
                address,
                comments,
                month,
                date,
                session["user_id"],
            )

        # retrieve and validate description
        description = request.form.getlist("description")
        if not description:
            return apology("Please select at least one event descriptor", 400)

        # insert a row for each adjective into descriptions
        rows = db.execute("SELECT event_id FROM events WHERE name = ?", name)
        event_id = rows[0]["event_id"]
        for adjective in description:
            db.execute(
                "INSERT INTO descriptions (event_id, adjective) VALUES (?, ?)",
                event_id,
                adjective,
            )

        # create a row in attendance for the event for each user
        total_users = db.execute("SELECT id FROM users")
        for user in total_users:
            db.execute(
                "INSERT INTO attendance (user_id, event_id) VALUES (?, ?)",
                user["id"],
                event_id,
            )

        # return to index
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("please provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("please provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    # if user reached route via GET
    if request.method == "GET":
        # pass existing preferences and adjectives and display page
        adjectives = [
            "Sporting Events",
            "Social Events",
            "Live Shows",
            "Food",
            "Arts",
            "Big Crowd",
            "Small Crowd",
            "Intimate",
            "Family Friendly",
            "21+",
            "$",
            "$$",
            "$$$",
        ]
        preferences = db.execute(
            "SELECT adjective FROM preferences WHERE user_id = ?", session["user_id"]
        )
        preferences = [adjective["adjective"] for adjective in preferences]
        return render_template(
            "preferences.html", adjectives=adjectives, preferences=preferences
        )

    # if user reached route via POST
    else:
        # delete all the preexisting preferences
        db.execute("DELETE FROM preferences")

        # insert a row into preferences table for each adjective
        new_preferences = request.form.getlist("preferences")
        for new_preference in new_preferences:
            db.execute(
                "INSERT INTO preferences (user_id, adjective) VALUES (?, ?)",
                session["user_id"],
                new_preference,
            )

        # show the updated preferences page
        return redirect("/")


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    # retrieve users
    rows = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = rows[0]["username"]

    # retrieve events the user has created
    events_created = db.execute(
        "SELECT * FROM events WHERE user_id = ?", session["user_id"]
    )

    # retrieve events the user has attended
    events_attended = db.execute(
        "SELECT name, city, comments, month, date FROM events JOIN attendance ON events.event_id = attendance.event_id WHERE attendance.user_id = ? AND attended = 1",
        session["user_id"],
    )

    # retrieve event info
    event_info = db.execute(
        "SELECT events.name, ratings.rating FROM events JOIN ratings ON events.event_id = ratings.event_id"
    )

    # retrieve ratings the user has inputted
    ratings = db.execute(
        "SELECT ratings.rating, events.name FROM ratings JOIN events ON ratings.event_id = events.event_id WHERE ratings.user_id = ?",
        session["user_id"],
    )

    # retrieve user preferences
    preferences = db.execute("SELECT * FROM preferences")

    # display profile page
    return render_template(
        "profile.html",
        username=username,
        events_created=events_created,
        events_attended=events_attended,
        ratings=ratings,
        preferences=preferences,
        event_info=event_info,
    )


@app.route("/ratings", methods=["GET", "POST"])
@login_required
def ratings():
    # if user reached route via GET
    if request.method == "GET":
        # retrieve events attended
        events = db.execute(
            "SELECT events.event_id, events.name FROM events JOIN attendance on events.event_id = attendance.event_id WHERE attendance.user_id = ? AND attendance.attended = 1",
            session["user_id"],
        )
        if events == []:
            return apology("You have not attended any events", 400)

        # display events attended
        return render_template("ratings.html", events=events)

    # if user reached route via POST
    else:
        # retrieve and validate rating
        try:
            rating = int(request.form.get("rating"))
        except ValueError:
            return apology("Please input a valid rating", 400)
        if not rating:
            return apology("Please input a rating", 400)
        if rating < 0 or rating > 10:
            return apology("Please input a rating from 0 to 10", 400)

        # retrieve comments
        comments = request.form.get("comment")

        # insert rating into new row in ratings
        event_id = request.form.get("event_id")
        if not comments:
            db.execute(
                "INSERT INTO ratings (event_id, user_id, rating) VALUES (?, ?, ?)",
                event_id,
                session["user_id"],
                rating,
            )
        else:
            db.execute(
                "INSERT INTO ratings (event_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
                event_id,
                session["user_id"],
                rating,
                comments,
            )

        # return to index
        return redirect("/")


@app.route("/recommendations", methods=["GET", "POST"])
@login_required
def recommendations():
    # retrieve list of all events and preferences
    events = db.execute("SELECT * FROM events")
    preferences = db.execute("SELECT * FROM preferences")

    # determine how many matches there are for each event between the user's preferences and the event's descriptions
    count_dict = {}
    for event in events:
        c = 0
        descriptions = db.execute(
            "SELECT * FROM descriptions WHERE event_id = ?", event["event_id"]
        )
        for description in descriptions:
            for preference in preferences:
                if preference["adjective"] in description["adjective"]:
                    c += 1
        count_dict[event["event_id"]] = c

    # sort the dictionary by value in descending order
    sorted_dict = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)

    # take the first five items
    five_events = sorted_dict[:5]

    # make a list of the event information for the top five recommended events
    recommendations = []
    for event in five_events:
        recommendations += db.execute(
            "SELECT * FROM events WHERE event_id = ?", event[0]
        )

    # retrieve attendance
    attendance = []
    for event in five_events:
        result = db.execute(
            "SELECT attended FROM attendance WHERE user_id = ? AND event_id = ?",
            session["user_id"],
            event[0],
        )
        attendance.append(result[0])

    # if user reached route via GET
    if request.method == "GET":
        # pass zip function
        zipped_lists = zip(recommendations, attendance)

        # display recommendations page
        return render_template("recommendations.html", zipped_lists=zipped_lists)

    # if user reached route via POST
    else:
        db.execute(
            "UPDATE attendance SET attended = 1 WHERE event_id = ?",
            request.form.get("event_id"),
        )
        return redirect("/recommendations")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # user reached route via POST
    if request.method == "POST":
        # retrieve username
        username = request.form.get("username")

        # validate username
        # if username not inputted
        if not username:
            return apology("please input username", 400)
        # if username already exists
        result = db.execute(
            "SELECT username FROM users WHERE username = :username", username=username
        )
        if len(result) != 0:
            return apology("username already exists", 400)

        # retrieve password
        password = request.form.get("password")

        # validate password
        # if password not inputted
        if not password:
            return apology("please input password", 400)

        # retrieve password confirmation
        confirm_password = request.form.get("confirmation")

        # validate password confirmation
        # if password confirmation not inputted
        if not confirm_password:
            return apology("please confirm password", 400)
        # if password and password confirmation do not match
        if password != confirm_password:
            return apology("passwords do not match", 400)

        # hash password
        hash = generate_password_hash(password)

        # store username and password hash
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # keep track of user logged in
        user_id = db.execute(
            "SELECT id FROM users WHERE username = :username", username=username
        )
        session["user_id"] = user_id[0]["id"]

        # create attendance row for this user for each event
        events = db.execute("SELECT event_id FROM events")
        for event in events:
            db.execute(
                "INSERT INTO attendance (user_id, event_id) VALUES (?, ?)",
                session["user_id"],
                event["event_id"],
            )

        # redirect user to homepage
        return redirect("/preferences")

    # user reached route via GET
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    # if user reached route via GET
    if request.method == "GET":
        # display search page
        return render_template("search.html")

    # if user reached route via POST
    else:
        # retrieve name
        name = request.form.get("name")

        # retrieve city
        city = request.form.get("city")

        # retrieve state
        state = request.form.get("state")

        # retrieve and validate month
        month = request.form.get("month")
        if month:
            try:
                month = int(request.form.get("month"))
            except ValueError:
                return apology("Please input valid month", 400)
            if month < 1 or month > 12:
                return apology("Please input valid month", 400)

        # retrieve and validate date
        date = request.form.get("date")
        if date:
            try:
                date = int(request.form.get("date"))
            except ValueError:
                return apology("Please input valid date", 400)
            if date < 1 or date > 31:
                return apology("Please input valid date", 400)

        # retrieve descriptors
        descriptions = request.form.getlist("description")

        # create and modify a string to be executed in sql and a list of values to be inputted into the table
        base_query = "SELECT * FROM events JOIN descriptions ON events.event_id = descriptions.event_id WHERE 1=1"
        values = []
        if name:
            base_query += " AND name LIKE ?"
            values.append("%" + name + "%")
        if city:
            base_query += " AND city = ?"
            values.append(city)
        if state:
            base_query += " AND state = ?"
            values.append(state)
        if month:
            base_query += " AND month = ?"
            values.append(month)
        if date:
            base_query += " AND date = ?"
            values.append(date)
        if descriptions:
            description_conditions = " OR ".join(
                ["descriptions.adjective = ?" for _ in descriptions]
            )
            base_query += f" AND ({description_conditions})"
            values.extend(descriptions)

        # store results in session
        results = db.execute(base_query + " GROUP BY events.event_id", *values)

        # retrieve attendance for all the events
        attendance = []
        for event in results:
            result = db.execute(
                "SELECT attended FROM attendance WHERE user_id = ? AND event_id = ?",
                session["user_id"],
                event["event_id"],
            )
            attendance.append(result[0])

        # zip attendance and search results
        session["zipped_lists"] = list(zip(results, attendance))
        session.modified = True

        # display results screen
        return render_template("searched.html", zipped_lists=session["zipped_lists"])


@app.route("/searched", methods=["GET", "POST"])
@login_required
def searched():
    # if user reached route via GET
    if request.method == "GET":
        # display search results screen
        return render_template("searched.html", zipped_lists=session["zipped_lists"])

    # if user reached route via POST
    else:
        # change the event to attended
        db.execute(
            "UPDATE attendance SET attended = 1 WHERE event_id = ?",
            request.form.get("event_id"),
        )

        # update session['zipped_lists']
        i = 0
        while i < len(session["zipped_lists"]):
            if str(session["zipped_lists"][i][0]["event_id"]) == request.form.get(
                "event_id"
            ):
                session["zipped_lists"][i][1]["attended"] = 1
            i += 1
        session.modified = True

        # display updated search results
        return render_template("searched.html", zipped_lists=session["zipped_lists"])
