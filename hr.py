import csv
import os
import sys
import requests


def get_csv_data(file_name, lines):
    with open(file_name, mode="r") as file:
        csv_file = csv.reader(file)
        for l in csv_file:
            lines.append(l)
    return lines


def generate_vcard(line, data):
    with open(f"vcards/{line[1].lower()}_{line[0].lower()}.vcf", "w") as f:
        f.write(data)


def generate_qr_code(line, data):
    qr_code = requests.get(
        f"https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl={data}"
    )
    with open(f"vcards/{line[1].lower()}_{line[0].lower()}.qr.png", "wb") as f:
        f.write(qr_code.content)


def generate_vcf_data(line):
    lname, fname, designation, email, phone = line
    data = f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
    return data


def main():
    if not os.path.exists("vcards"):
        os.makedirs("vcards")
    file_name = sys.argv[1]
    lines = []
    lines = get_csv_data(file_name, lines)
    for line in lines:
        data = generate_vcf_data(line)
        generate_vcard(line, data)
        generate_qr_code(line, data)


if __name__ == "__main__":
    main()
