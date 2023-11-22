import argparse
import csv
import logging
import os
import psycopg2
from psycopg2.extensions import AsIs
import requests
import sys

class HRException(Exception): pass

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
    parser.add_argument("--database", type=str, help="name of database", default="hr")

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
        "--employee",
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
    parser_leave_detail.add_argument("employee_id", type=int, help="id of employee")

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
        logging.Formatter(
            "[%(levelname)s] | %(filename)s:%(lineno)d | %(message)s"
        )
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
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    with open("sql/check_leave_data_exist.sql", "r") as query:
        query = query.read()
    cur.execute(query, (args.employee_id, args.date))
    conn.commit()
    exists = cur.fetchone()[0]
    if exists:
        logger.error(f"Employee already taken leave on {args.date}")
        exit()
    with open("sql/insert_into_table_leaves.sql", "r") as query:
        query = query.read()
    
    cur.execute(query, (args.employee_id, args.date, args.reason))
    conn.commit()
    cur.close()
    conn.close()


def get_table_data(args):
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    if args.employee:
        query = "SELECT last_name, first_name, designation, email, phone FROM employees WHERE id IN (%s);"
        cur.execute(query, (args.employee,))
    else:
        query = "SELECT last_name, first_name, designation, email, phone FROM employees;"
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


def get_leave_detail(args):
    conn = psycopg2.connect(f"dbname={args.database}")
    cur = conn.cursor()
    with open("sql/get_leave_detail.sql", "r") as query:
        query = query.read()
    cur.execute(query, (args.employee_id,))
    conn.commit()
    leaves_taken, first_name, last_name, total_leaves, leaves_remaining = cur.fetchall()[0]
    cur.close()
    conn.close()
    return leaves_taken, first_name, last_name, total_leaves, leaves_remaining


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
    row_count = 0

    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    elif not args.overwrite:
        logger.error(
            """
Directory already exists
Use -o to overwrite
"""
        )
        exit()
    
    lines = get_table_data(args)

    for lname, fname, designation, email, phone in lines:
        row_count += 1
        data = generate_vcf_data(
            lname, fname, designation, email, phone, args.address
        )
        if args.qrcodedimension:
            dimension = args.qrcodedimension
            generate_qr_code(email, data, row_count, dimension)
        elif args.qrcode:
            generate_qr_code(email, data, row_count)
        generate_vcard(email, data, row_count)
    logger.info("Generated Successfully")   

def handle_leave(args):
    insert_into_table_leaves(args)
    logger.info("inserted to table leaves")

def handle_leave_detail(args):
    leaves_taken, first_name, last_name, total_leaves, leaves_remaining = get_leave_detail(args)
    print(f"""
Name            : {first_name} {last_name}
Leaves taken    : {leaves_taken}
Leaves remaining: {leaves_remaining}
Total leaves    : {total_leaves}
"""
    )

def main():
    try:
        args = parse_args()
        setup_logging(args.verbose)

        ops = {"initdb" : handle_initdb,
               "load" : handle_load,
               "generate" : handle_generate,
               "leave" : handle_leave,
               "leave_detail" : handle_leave_detail}
        ops[args.mode](args)
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)


if __name__ == "__main__":
    main()
