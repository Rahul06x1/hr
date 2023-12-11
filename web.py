from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.sql import func


import models


app = Flask("hrms")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = models.SQLAlchemy(model_class=models.HRDBBase)
cache = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.id)
    users = db.session.execute(query).scalars()
    return render_template("userlist.html", users=users)


@app.route("/employees/<int:empid>")
def employee_details(empid):
    user_query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(user_query).scalar()
    if "user_list" in cache:
        user_list = cache["user_list"]
    else:
        users_id_query = db.select(models.Employee.id).order_by(models.Employee.id)
        ids = db.session.execute(users_id_query).fetchall()
        user_list = [id for id, in ids]
        cache["user_list"] = user_list
    leave_query = db.select(func.count(models.Leave.id)).where(
        models.Leave.employee_id == empid
    )
    leave = db.session.execute(leave_query).scalar()
    ret = {
        "id": user.id,
        "fname": user.first_name,
        "lname": user.last_name,
        "title": user.title.title,
        "email": user.email,
        "phone": user.phone,
        "leaves_taken": leave,
        "leaves_remaining": user.title.max_leaves - leave,
        "total_leaves": user.title.max_leaves,
        "user_list": user_list,
    }
    return jsonify(ret)


@app.route("/leave/<int:empid>", methods=("GET", "POST"))
def add_leave(empid):
    if request.method == "POST":
        user_query = db.select(models.Employee).where(models.Employee.id == empid)
        user = db.session.execute(user_query).scalar()
        leave_query = db.select(func.count(models.Leave.id)).where(
        models.Leave.employee_id == empid
    )
        leave = db.session.execute(leave_query).scalar()
        if user.title.max_leaves <= leave:
            flash(f"Employee reached leave limit  {user.title.max_leaves}")
            return redirect(url_for("employees"))
        try:
            date = request.form["date"]
            reason = request.form["reason"]
            l = models.Leave(date=date, employee_id=empid, reason=reason)
            db.session.add(l)
            db.session.commit()
            flash("Leave added successfully")
            return redirect(url_for("employees"))
        except:
            flash(f"Employee already taken leave on {date}")
            return redirect(url_for("employees"))
