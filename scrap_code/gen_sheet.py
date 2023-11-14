import faker
import sys
import csv


def create_csv(file_name, data):
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        for d in data:
            writer.writerow(d)


def main():
    f = faker.Faker()
    file_name = sys.argv[1]
    names = []
    for i in range(100):
        record = []
        lname = f.last_name()
        fname = f.first_name()
        domain = f.domain_name()
        designation = f.job()
        email = f"{fname[:5].lower()}.{lname[:5].lower()}@{domain}"
        phone = f.phone_number()
        record = [lname, fname, designation, email, phone]
        names.append(record)

    create_csv(file_name, names)


if __name__ == "__main__":
    main()
