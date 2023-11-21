# HR

Generates visiting cards and their qr codes for a set of employees from database

## How to run

Go to the hr directory and run
1) ```python hr.py initdb <database_name><postgres_username>``` to initialize database
2) ```python hr.py load <csv_file><database_name><postgres_username>``` to load csv file to database
3) ```python hr.py <database_name><postgres_username>``` to generate vcards