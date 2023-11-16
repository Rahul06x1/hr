import argparse
import csv
import logging
import os
import requests

logger = None


def parse_args():
    parser = argparse.ArgumentParser(
        prog="hr.py", description="Generates vcard and qrcode for each employee from csv file"
    )
    parser.add_argument("csv_file", help="name of csv file containing employee details")
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
        choices=range(70, 548)
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


def get_csv_data(file_name, lines, start=0, end=float("inf")):
    line_num = 0
    with open(file_name, mode="r") as file:
        csv_file = csv.reader(file)
        for l in csv_file:
            line_num += 1
            if start <= line_num <= end:
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
    args = parse_args()
    row_count = 0
    if args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    if not os.path.isfile(args.csv_file):
        logger.error("%s does not exists", args.csv_file)
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
        lines = get_csv_data(args.csv_file, [], start, end)
    else:
        lines = get_csv_data(args.csv_file, [])

    for line in lines:
        row_count += 1
        lname, fname, designation, email, phone = line
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
