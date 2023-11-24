import argparse
import csv
from datetime import date
import logging
import os
import psycopg2
from psycopg2.extensions import AsIs
import requests
import sys


class HRException(Exception):
    pass


logger = None


def parse_args():
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
        "-d", "--database", type=str, help="name of custom database", default="hr"
    )

    subparsers = parser.add_subparsers(dest="mode", help="action to perform")
    # initdb
    parser_initdb = subparsers.add_parser("initdb", help="initialize database")

    # load
    parser_load = subparsers.add_parser("load", help="load csv file data to database")
    parser_load.add_argument("employees_file", type=str, help="name of csv file")
    # generate vcards
    parser_generate = subparsers.add_parser("generate", help="generate vcards")
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
        help="generate files in custom directory",
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
    parser_leave = subparsers.add_parser("leave", help="add leave to database")
    parser_leave.add_argument("employee_id", type=int, help="employee id of absentee")
    parser_leave.add_argument("date", type=str, help="date of absence")
    parser_leave.add_argument("reason", type=str, help="reason of absence")
    # evavulate leaves remaining
    parser_leave_detail = subparsers.add_parser(
        "leave_detail", help="evavulate leaves remaining of an employee"
    )
    parser_leave_detail.add_argument("employee_id", type=int, help="employee id")
    # export csv file with employees and leaves
    parser_export = subparsers.add_parser(
        "export", help="export csv file with employees and leaves"
    )
    parser_export.add_argument("-e", "--employee_id", type=int, help="employee id")
    parser_export.add_argument(
        "-f", "--filename", type=str, help="csv filename", default="leaves"
    )
    parser_export.add_argument(
        "-d",
        "--directory",
        help="generate file in custom directory",
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


def insert_into_table_leaves(args):
    check_employee_exist(args)
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    # check if employee already taken leave on that date
    with open("sql/check_leave_data_exist.sql", "r") as query:
        query = query.read()
    cur.execute(query, (args.employee_id, args.date))
    conn.commit()
    exists = cur.fetchone()[0]
    if exists:
        logger.error(f"Employee already taken leave on {args.date}")
        exit()

    # check if employee reached the leave limit
    (
        first_name,
        last_name,
        leaves_taken,
        leaves_remaining,
        total_leaves,
    ) = get_leave_detail(args)
    print(leaves_taken)
    print(total_leaves)
    print(leaves_taken >= total_leaves)
    if leaves_taken >= total_leaves:
        logger.error(f"{first_name} {last_name} reached the leave limit {total_leaves}")
        exit()

    # insert leave data into table leaves
    with open("sql/insert_into_table_leaves.sql", "r") as query:
        query = query.read()

    cur.execute(query, (args.employee_id, args.date, args.reason))
    conn.commit()
    cur.close()
    conn.close()


def check_employee_exist(args, employee_id=None):
    if not employee_id:
        print("llllllllsss")
        employee_id = args.employee_id
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    query = "SELECT EXISTS(SELECT 1 FROM employees WHERE id = %s);"
    cur.execute(query, (employee_id,))
    conn.commit()
    exist = cur.fetchall()
    if not exist[0][0]:
        logger.error(f"No employee with id {employee_id}")
        exit()
    cur.close()
    conn.close()


def get_table_data(args):
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    if args.employee_id:
        query = "SELECT id, last_name, first_name, designation, email, phone FROM employees WHERE id IN (%s);"
        cur.execute(query, (args.employee_id,))
    else:
        query = "SELECT id, last_name, first_name, designation, email, phone FROM employees;"
        cur.execute(query)

    conn.commit()
    lines = cur.fetchall()
    cur.close()
    conn.close()
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
    check_employee_exist(args, employee_id)
    if not employee_id:
        employee_id = args.employee_id
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return first_name, last_name, leaves_taken, leaves_remaining, total_leaves


def handle_initdb(args):
    with open("sql/initialize_database.sql") as f:
        sql = f.read()
    try:
        con = psycopg2.connect(dbname=args.database)
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        logger.info("Database initialized")
    except psycopg2.OperationalError as e:
        raise HRException(f"Database '{args.database}' doesn't exist")


def handle_load(args):
    con = psycopg2.connect(dbname=args.database)
    cur = con.cursor()
    with open(args.employees_file) as f:
        reader = csv.reader(f)
        for lname, fname, designation, email, phone in reader:
            logger.debug("Inserting %s", email)
            with open("sql/insert_into_table_employees.sql", "r") as query:
                query = query.read()
            cur.execute(query, (lname, fname, designation, email, phone))
        con.commit()


def handle_generate(args):
    check_employee_exist(args)
    row_count = 0

    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    elif not args.overwrite:
        logger.error(
            """
Directory {args.directory} already exists
Use -o to overwrite
"""
        )
        exit()

    lines = get_table_data(args)

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
    insert_into_table_leaves(args)
    logger.info("Inserted to table leaves")


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
        if args.employee_id:
            row = get_leave_detail(args, id)
            with open(
                os.path.join(
                    "data",
                    f"{args.filename}_{fname.lower()}_{lname.lower()}{date.today()}.csv",
                ),
                "a",
            ) as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
        else:
            row = get_leave_detail(args, id)
            with open(
                os.path.join("data", f"{args.filename}_{date.today()}.csv"), "a"
            ) as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
    logger.info("CSV exported")


def main():
    try:
        args = parse_args()
        setup_logging(args.verbose)

        mode = {
            "initdb": handle_initdb,
            "load": handle_load,
            "generate": handle_generate,
            "leave": handle_leave,
            "leave_detail": handle_leave_detail,
            "export": handle_export,
        }
        mode[args.mode](args)
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)


if __name__ == "__main__":
    main()
