import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from hr import generate_vcf_data, get_csv_data


def test_generate_vcf_data():
    line = [
        "Walker",
        "Charlene",
        "Therapist, art",
        "charl.walke@kelly-williams.info",
        "(252)913-2078x96029",
    ]
    assert (
        generate_vcf_data(line)
        == """BEGIN:VCARD
VERSION:2.1
N:Walker;Charlene
FN:Charlene Walker
ORG:Authors, Inc.
TITLE:Therapist, art
TEL;WORK;VOICE:(252)913-2078x96029
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:charl.walke@kelly-williams.info
REV:20150922T195243Z
END:VCARD
"""
    )


def test_get_csv_data():
    file_name = "/tmp/sample_csv"
    lines = []
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Moore",
                "Samuel",
                "Therapist, horticultural",
                "samue.moore@henry.biz",
                "6583391554",
            ]
        )
        writer.writerow(
            [
                "Walker",
                "Charlene",
                "Therapist, art",
                "charl.walke@kelly-williams.info",
                "(252)913-2078x96029",
            ]
        )

    assert get_csv_data(file_name, lines) == [
        [
            "Moore",
            "Samuel",
            "Therapist, horticultural",
            "samue.moore@henry.biz",
            "6583391554",
        ],
        [
            "Walker",
            "Charlene",
            "Therapist, art",
            "charl.walke@kelly-williams.info",
            "(252)913-2078x96029",
        ],
    ]

    os.unlink(file_name)
