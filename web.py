from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_cors import CORS
from sqlalchemy.sql import func
from datetime import datetime

import models


app = Flask("hrms")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)
db = models.SQLAlchemy(model_class=models.HRDBBase)


@app.route("/")
def index():
    return "<h1>HR API</h1>"


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(
        models.Employee.first_name, models.Employee.last_name
    )
    users = db.session.execute(query).scalars()
    ret = []
    for u in users:
        ret.append(
            {
                "id": u.id,
                "lname": u.last_name,
                "fname": u.first_name,
            }
        )
    return jsonify(ret)


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
    leave_request = request.get_json()
    date = datetime.strptime(leave_request["date"], "%Y-%m-%d").date()
    reason = leave_request["reason"]
    user_query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(user_query).scalar()
    leave_query = db.select(func.count(models.Leave.id)).where(
        models.Leave.employee_id == empid
    )
    leave = db.session.execute(leave_query).scalar()
    if user.title.max_leaves <= leave:
        ret = {
            "status": False,
            "message": f"Employee reached leave limit  {user.title.max_leaves}",
        }
        return jsonify(ret)
    try:
        l = models.Leave(date=date, employee_id=empid, reason=reason)
        db.session.add(l)
        db.session.commit()
        ret = {"status": True, "message": "Leave added successfully"}
        return jsonify(ret)
    except:
        ret = {"status": False, "message": f"Employee already taken leave on {date}"}
        return jsonify(ret)


@app.route("/vcard/<int:empid>")
def generate_vcard(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    ret = {
        "vcard": f"""BEGIN:VCARD
VERSION:2.1
N:{user.last_name};{user.first_name}
FN:{user.first_name} {user.last_name}
ORG:Authors, Inc.
TITLE:{user.title.title}
TEL;WORK;VOICE:{user.phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{user.email}
REV:20150922T195243Z
END:VCARD
"""
    }
    return jsonify(ret)
