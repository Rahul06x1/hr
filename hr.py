import argparse
import configparser
import csv
from datetime import date
import logging
import os
import shutil
import sys

import psycopg2
import requests
import sqlalchemy as sa

import db


class HRException(Exception):
    pass


logger = None


def update_config(args):
    config["DATABASE"]["dbname"] = args.database
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def parse_args():
    global config
    config = configparser.ConfigParser()
    config.read("config.ini")

    parser = argparse.ArgumentParser(
        prog="hr.py",
        description="Generates vcard and qrcode for each employee from csv file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="print detailed logging",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="name of custom database (Default : %(default)s)",
        default=config.get("DATABASE", "dbname"),
    )

    subparsers = parser.add_subparsers(dest="mode", help="action to perform")
    # initdb
    parser_initdb = subparsers.add_parser(
        "initdb", help="Initialize database", description="Initialize database"
    )

    # import csv file data to database
    parser_import = subparsers.add_parser(
        "import",
        help="Import csv file data to database",
        description="Import csv file data to database",
    )
    parser_import.add_argument("employees_file", type=str, help="name of csv file")

    # generate vcards
    parser_generate = subparsers.add_parser(
        "generate", help="Generate vCards", description="Generate vCards"
    )
    parser_generate.add_argument(
        "-o",
        "--overwrite",
        help="overwrite existing directory",
        action="store_true",
        default=False,
    )
    parser_generate.add_argument(
        "-q", "--qrcode", help="generates qrcode", action="store_true", default=False
    )
    parser_generate.add_argument(
        "-x",
        "--qrcodedimension",
        help="set custom qr code dimensions",
        type=int,
        choices=range(70, 548),
    )
    parser_generate.add_argument(
        "-e",
        "--employee_id",
        help="employee id",
        type=int,
        nargs="?",
    )
    parser_generate.add_argument(
        "-d",
        "--directory",
        help="generate files in custom directory (Default : %(default)s)",
        action="store",
        type=str,
        default="vcards",
    )
    parser_generate.add_argument(
        "-a",
        "--address",
        help="set custom address",
        action="store",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )

    # create leave
    parser_leave = subparsers.add_parser(
        "leave", help="Add leave to database", description="Add leave to database"
    )
    parser_leave.add_argument("employee_id", type=int, help="employee id of absentee")
    parser_leave.add_argument(
        "date", type=str, help="Specify date of absence (YYYY-MM-DD)"
    )
    parser_leave.add_argument("reason", type=str, help="reason of absence")

    # evavulate leaves remaining
    parser_leave_detail = subparsers.add_parser(
        "leave_detail",
        help="Display leave details of an employee",
        description="Display leave details of an employee",
    )
    parser_leave_detail.add_argument("employee_id", type=int, help="employee id")

    # export csv file with employees and leaves
    parser_export = subparsers.add_parser(
        "export",
        help="Export csv file with employees and their leaves details",
        description="Export csv file with employees and their leaves details",
    )
    parser_export.add_argument("-e", "--employee_id", type=int, help="employee id")
    parser_export.add_argument("-f", "--filename", type=str, help="csv filename")
    parser_export.add_argument(
        "-d",
        "--directory",
        help="generate file in custom directory (Default : %(default)s)",
        action="store",
        type=str,
        default="data",
    )

    args = parser.parse_args()
    return args


def setup_logging(is_verbose):
    global logger
    if is_verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger = logging.getLogger("HR")
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter("[%(levelname)s] | %(filename)s:%(lineno)d | %(message)s")
    )
    fhandler.setFormatter(
        logging.Formatter(
            "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
        )
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)


def add_leaves(args):
    # check if employee already taken leave on that date
    with open("sql/check_leave_data_exist.sql", "r") as query:
        query = query.read()
    cur.execute(query, (args.employee_id, args.date))
    conn.commit()
    exists = cur.fetchone()[0]
    if exists:
        logger.error("Employee already taken leave on %s", args.date)
        exit()

    # check if employee reached the leave limit
    (
        first_name,
        last_name,
        leaves_taken,
        leaves_remaining,
        total_leaves,
    ) = get_leave_detail(args)
    if leaves_taken >= total_leaves:
        logger.error(
            "%s %s reached the leave limit %s", first_name, last_name, total_leaves
        )
        exit()

    # add leave to database
    with open("sql/add_leaves.sql", "r") as query:
        query = query.read()

    cur.execute(query, (args.employee_id, args.date, args.reason))
    conn.commit()
    cur.close()
    conn.close()


def get_table_data(args):
    if args.employee_id:
        query = "SELECT id, last_name, first_name, designation, email, phone FROM employees WHERE id = %s;"
        cur.execute(query, (args.employee_id,))
    else:
        query = "SELECT id, last_name, first_name, designation, email, phone FROM employees;"
        cur.execute(query)

    conn.commit()
    lines = cur.fetchall()
    if not lines:
        logger.error("No employee with id %s", args.employee_id)
        sys.exit(-1)
    return lines


def get_csv_data(file_name, lines):
    line_num = 0
    with open(file_name, mode="r") as file:
        csv_file = csv.reader(file)
        for l in csv_file:
            line_num += 1
            if len(l) == 5:
                lines.append(l)
            else:
                logger.warning(
                    "Insufficient data provided in line %d of file %s",
                    line_num,
                    file_name,
                )
    return lines


def generate_vcard(email, data, row_count):
    with open(os.path.join("vcards", f"{email}.vcf"), "w") as f:
        f.write(data)
    logger.debug("%d Generated vCard for %s", row_count, email)


def generate_qr_code(email, data, row_count, dimension=500):
    qr_code = requests.get(
        f"https://chart.googleapis.com/chart?cht=qr&chs={dimension}x{dimension}&chl={data}"
    )
    with open(os.path.join("vcards", f"{email}.qr.png"), "wb") as f:
        f.write(qr_code.content)
    logger.debug("%d Generated qr code for %s", row_count, email)


def generate_vcf_data(lname, fname, designation, email, phone, address):
    data = f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;{address}
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
    return data


def get_leave_detail(args, employee_id=None):
    try:
        if not employee_id:
            employee_id = args.employee_id
        with open("sql/get_leave_detail.sql", "r") as query:
            query = query.read()
        cur.execute(query, (employee_id,))
        conn.commit()
        leave_data = cur.fetchall()
        if leave_data:
            (
                first_name,
                last_name,
                leaves_taken,
                leaves_remaining,
                total_leaves,
            ) = leave_data[0]
        else:
            query = """SELECT e.first_name, e.last_name,d.no_of_leaves,
            d.no_of_leaves as leaves_remaining
            FROM employees e 
            INNER JOIN designation d ON e.designation = d.designation 
            WHERE e.id = %s
            GROUP BY e.id, e.first_name, e.last_name,d.no_of_leaves;"""
            cur.execute(query, (employee_id,))
            conn.commit()
            first_name, last_name, total_leaves, leaves_remaining = cur.fetchall()[0]
            leaves_taken = 0
        return first_name, last_name, leaves_taken, leaves_remaining, total_leaves
    except Exception as e:
        logger.error("No employee with id %s", employee_id)
        sys.exit(-1)


def handle_initdb(args):
    db_uri = f"postgresql:///{args.database}"
    db.create_all(db_uri)
    session = db.get_session(db_uri)
    d1 = db.Designation(title="Staff Engineer", max_leaves=20)
    d2 = db.Designation(title="Senior Engineer", max_leaves=18)
    d3 = db.Designation(title="Junior Engineer", max_leaves=12)
    d4 = db.Designation(title="Tech. Lead", max_leaves=12)
    d5 = db.Designation(title="Project Manager", max_leaves=15)
    session.add(d1)
    session.add(d2)
    session.add(d3)
    session.add(d4)
    session.add(d5)
    session.commit()
    logger.info("Initialized database")


def handle_import(args):
    db_uri = f"postgresql:///{args.database}"
    session = db.get_session(db_uri)
    with open(args.employees_file) as f:
        reader = csv.reader(f)
        for lname, fname, title, email, phone in reader:
            q = sa.select(db.Designation).where(db.Designation.title==title)
            designation = session.execute(q).scalar_one()
            logger.debug("Inserting %s", email)
            employee = db.Employee(
                last_name = lname,
                first_name = fname,
                email = email,
                phone = phone,
                title = designation
            )
            session.add(employee)
        session.commit()
    logger.info("csv file imported")


def handle_generate(args):
    row_count = 0
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    elif args.overwrite:
        shutil.rmtree(args.directory)
        os.makedirs(args.directory)
    else:
        logger.error(
            """
Directory %s already exists
Use -o to overwrite
""",
            args.directory,
        )
        exit()

    lines = get_table_data(args)

    if args.qrcodedimension or args.qrcode:
        logger.info("Generating qrcode. Please wait a while...")

    for id, lname, fname, designation, email, phone in lines:
        row_count += 1
        data = generate_vcf_data(lname, fname, designation, email, phone, args.address)
        if args.qrcodedimension:
            dimension = args.qrcodedimension
            generate_qr_code(email, data, row_count, dimension)
        elif args.qrcode:
            generate_qr_code(email, data, row_count)
        generate_vcard(email, data, row_count)
    logger.info("Generated Successfully")


def handle_leave(args):
    add_leaves(args)
    logger.info("Leave added")


def handle_leave_detail(args):
    (
        first_name,
        last_name,
        leaves_taken,
        leaves_remaining,
        total_leaves,
    ) = get_leave_detail(args)
    print(
        f"""
Name            : {first_name} {last_name}
Leaves taken    : {leaves_taken}
Leaves remaining: {leaves_remaining}
Total leaves    : {total_leaves}
"""
    )
    logger.info("Leave detail generated")


def handle_export(args):
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    lines = get_table_data(args)
    for id, lname, fname, designation, email, phone in lines:
        row = get_leave_detail(args, id)
        if args.filename:
            filename = f"{args.filename}.csv"
        elif args.employee_id:
            filename = f"leave_{fname.lower()}_{lname.lower()}_{date.today()}.csv"
        else:
            filename = f"leave_{date.today()}.csv"
        with open(os.path.join("data", filename), "a") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row)
    logger.info("CSV exported as %s", filename)


def main():
    try:
        global conn, cur
        args = parse_args()
        setup_logging(args.verbose)
        update_config(args)

        mode = {
            "initdb": handle_initdb,
            "import": handle_import,
            "generate": handle_generate,
            "leave": handle_leave,
            "leave_detail": handle_leave_detail,
            "export": handle_export,
        }
        conn = psycopg2.connect(dbname=args.database)
        cur = conn.cursor()
        mode[args.mode](args)
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Program aborted - %s", error)
        sys.exit(-1)


if __name__ == "__main__":
    main()
