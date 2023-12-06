from flask import Flask, render_template, request, redirect, url_for, flash


import models


app = Flask("hrms")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = models.SQLAlchemy(model_class=models.HRDBBase)


def get_leave_detail(employee_id):
    q = (
        db.select(
            db.func.count(models.Employee.id),
            models.Designation.max_leaves,
        )
        .where(
            models.Employee.id == employee_id,
            models.Employee.id == models.Leave.employee_id,
            models.Employee.title_id == models.Designation.id,
        )
        .group_by(
            models.Employee.id,
            models.Employee.first_name,
            models.Employee.last_name,
            models.Designation.max_leaves,
        )
    )
    leave_detail = db.session.execute(q).fetchall()
    if leave_detail:
        (
            leaves_taken,
            total_leaves,
        ) = leave_detail[0]
        leaves_remaining = total_leaves - leaves_taken
    else:
        q = db.select(models.Designation.max_leaves).where(
            models.Employee.id == employee_id,
            models.Employee.title_id == models.Designation.id,
        )
        leave_detail = db.session.execute(q).fetchall()
        (total_leaves,) = leave_detail[0]
        leaves_taken = 0
        leaves_remaining = total_leaves
    leave_detail = {
        "leaves_taken": leaves_taken,
        "leaves_remaining": leaves_remaining,
        "total_leaves": total_leaves,
    }
    return leave_detail


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    return render_template("userlist.html", users=users)


@app.route("/employee/<int:empid>", methods=("GET", "POST"))
def employee_details(empid):
    if request.method == "POST":
        date = request.form["date"]
        reason = request.form["reason"]
        l = models.Leave(date=date, employee_id=empid, reason=reason)
        db.session.add(l)
        db.session.commit()
        return redirect(url_for("employee_details", empid=empid))
    leave_detail = get_leave_detail(empid)
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    return render_template(
        "userdetails.html", user=user, users=users, leave=leave_detail
    )
