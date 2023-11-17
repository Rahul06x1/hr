import argparse
import csv
import logging
import os
import psycopg2
import requests

logger = None


def parse_args():
    parser = argparse.ArgumentParser(
        prog="hr.py",
        description="Generates vcard and qrcode for each employee from csv file",
    )
    parser.add_argument('mode', help="action to perform", choices=['generate', 'initdb', 'load'],nargs="?",default="generate")
    parser.add_argument("-c","--csv_file",action="store",type=str)
    parser.add_argument(
        "-o",
        "--overwrite",
        help="overwrite existing directory",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="print detailed logging",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-q", "--qrcode", help="generates qrcode", action="store_true", default=False
    )
    parser.add_argument(
        "-x",
        "--qrcodedimension",
        help="set custom qr code dimensions",
        type=int,
        choices=range(70, 548),
    )
    parser.add_argument(
        "-r",
        "--range",
        help="generate files inbetween a range of line numbers",
        type=int,
        nargs="+",
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="generate files in custom directory",
        action="store",
        type=str,
        default="vcards",
    )
    parser.add_argument(
        "-a",
        "--address",
        help="set custom address",
        action="store",
        type=str,
        default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="number of records to generate",
        action="store",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    return args


def setup_logging(log_level):
    global logger
    logger = logging.getLogger("HR")
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter(
            "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
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

def check_database_exist():
    conn = psycopg2.connect("dbname=postgres user=hamon")
    cur = conn.cursor()
    conn.autocommit = True
    cur.execute("""
        SELECT EXISTS (
            SELECT datname
            FROM pg_catalog.pg_database
            WHERE lower(datname) = lower('hr')
        );
    """)
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

def check_table_row_exist():
    conn = psycopg2.connect("dbname=hr user=hamon")
    cur = conn.cursor()
    conn.autocommit = True
    cur.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM employees
        );
    """)
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

def initialize_table():
    conn = psycopg2.connect("dbname=hr user=hamon")
    cur = conn.cursor()
    cur.execute(
            "CREATE TABLE employees (id SERIAL PRIMARY KEY, last_name VARCHAR(50) NOT NULL, first_name VARCHAR(50) NOT NULL, designation VARCHAR(50) NOT NULL,email VARCHAR(50) NOT NULL UNIQUE, phone VARCHAR(50) NOT NULL);"
        )
    conn.commit()
    logger.info("Table initialized")
    cur.close()
    conn.close()

def initialize_database():
    conn = psycopg2.connect("dbname=postgres user=hamon")
    cur = conn.cursor()
    conn.autocommit = True
    cur.execute("""
        SELECT EXISTS (
            SELECT datname
            FROM pg_catalog.pg_database
            WHERE lower(datname) = lower('hr')
        );
    """)
    exists = cur.fetchone()[0]
    if exists:
        logger.warning("Database 'hr' already exists")
    else:
        cur.execute(
            "CREATE DATABASE hr;"
        )
        logger.info("Database initialized")
        
    cur.close()
    conn.close()


def insert_data_to_database_table(lname, fname, designation, email, phone):
    conn = psycopg2.connect("dbname=hr user=hamon")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO employees (last_name, first_name, designation, email, phone) VALUES (%s, %s, %s, %s, %s)",
        (lname, fname, designation, email, phone),
    )
    conn.commit()
    cur.close()
    conn.close()

def get_table_data(start=1, end=9223372036854775807):
    offset = start-1
    limit = end - start + 1
    conn = psycopg2.connect("dbname=hr user=hamon")
    cur = conn.cursor()
    cur.execute(
        "SELECT last_name, first_name, designation, email, phone FROM employees LIMIT %s OFFSET %s;",(limit, offset)
    )
    lines = cur.fetchall()
    print(len(lines))
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


def main():
    row_count = 0
    args = parse_args()
    if args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
        
    if args.mode == 'initdb':
        initialize_database()
        initialize_table()
        exit()
    elif args.mode == 'load':
        database_exist = check_database_exist()
        if not database_exist:
            logger.error("""
Database 'hr' does not exist
Use initdb to initialize database
""")
            exit()
        if not args.csv_file:
            logger.error("Provide csv file for loading using -c")
        else:
            if not os.path.isfile(args.csv_file):
                logger.error("%s does not exists", args.csv_file)
                exit()
            lines = get_csv_data(args.csv_file, [])
            for lname, fname, designation, email, phone in lines:
                insert_data_to_database_table(lname, fname, designation, email, phone)
            logger.info("csv file loaded")
        exit()
     
    database_exist = check_database_exist()
    if not database_exist:
        logger.error("""
Database 'hr' does not exist
Use initdb to initialize database
""")
        exit()
    table_row_exist = check_table_row_exist()
    if not table_row_exist:
        logger.warning("""
Table 'employees' does not have any data
Use load to load csv file data to table
""")
        exit()

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
    if args.range:
        if len(args.range) != 2:
            logger.error("Use only 2 arguments")
            exit()
        start, end = args.range
        if start > end:
            logger.error("start should be less than end")
            exit()
        lines = get_table_data(start, end)
    else:
        lines = get_table_data()

    for lname, fname, designation, email, phone in lines:
        row_count += 1
        data = generate_vcf_data(lname, fname, designation, email, phone, args.address)
        if args.qrcodedimension:
            dimension = args.qrcodedimension
            generate_qr_code(email, data, row_count, dimension)
        elif args.qrcode:
            generate_qr_code(email, data, row_count)
        generate_vcard(email, data, row_count)
        if row_count >= args.number and not args.range:
            break
    logger.info("Generated Successfully")


if __name__ == "__main__":
    main()
