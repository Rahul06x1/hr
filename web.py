from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.sql import func


import models


app = Flask("hrms")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = models.SQLAlchemy(model_class=models.HRDBBase)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(
        models.Employee.first_name, models.Employee.last_name
    )
    users = db.session.execute(query).scalars()
    return render_template("userlist.html", users=users)


@app.route("/employees/<int:empid>")
def employee_details(empid):
    user_query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(user_query).scalar()
    users_id_query = db.select(models.Employee.id).order_by(
        models.Employee.first_name, models.Employee.last_name
    )
    ids = db.session.execute(users_id_query).fetchall()
    user_list = [id for id, in ids]

    index = user_list.index(empid)
    prev = user_list[index - 1]
    try:
        next = user_list[index + 1]
    except:
        next = user_list[0]
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
        "total_leaves": user.title.max_leaves,
        "prev": prev,
        "next": next,
    }
    return jsonify(ret)


@app.route("/leave/<int:empid>", methods=["POST"])
def add_leave(empid):
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


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
