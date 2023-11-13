import csv
import os
import sys


def get_csv_data(file_name, lines):
    with open(file_name, mode="r") as file:
        csv_file = csv.reader(file)
        for l in csv_file:
            lines.append(l)
    return lines


def generate_vcard(lines):
    for line in lines:
        data = generate_vcf_data(line)
        with open(f"vcards/{line[1].lower()}_{line[0].lower()}.vcf", "w") as f:
            f.write(data)


def generate_vcf_data(line):
    lname = line[0]
    fname = line[1]
    designation = line[2]
    email = line[3]
    phone = line[4]
    data = f"""VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
"""
    return data


def main():
    if not os.path.exists("vcards"):
        os.makedirs("vcards")
    file_name = sys.argv[1]
    lines = []
    lines = get_csv_data(file_name, lines)
    generate_vcard(lines)


if __name__ == "__main__":
    main()
