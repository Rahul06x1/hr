# HR

Generates visiting cards and their qr codes for a set of employees from database

## How to run

Go to the hr directory and run
1) ```hr.py initdb``` to initialize database
2) ```hr.py load <employees_file>``` to load csv file to database
3) ```hr.py generate``` to generate vcards
4) ```hr.py leave <employee_id> <date> <reason>``` to add leave to leave record
5) ```hr.py leave_detail <employee_id>``` to get leave detail of an employee
6) ```hr.py export``` to export leave details to csv file