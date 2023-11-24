## Objective:

Generates visiting cards and their qr codes for a list of employees provided in a CSV
file


## Input:

    Usage: 
        hr.py [-h] [-v] [-d] {initdb,load,generate,leave,leave_detail,export}

    Positional Arguments:
        {initdb,load,generate,leave,leave_detail,export}    action to perform
        initdb                                              initialize database
        load                                                load csv file data to database
        generate                                            generate vcards
        leave                                               add leave to database
        leave_detail                                        evavulate leaves remaining of an employee
        export                                              export csv file with employees and leaves

    Options:
        -h, --help                          show this help message and exit
        -v, --verbose                       print detailed logging
        -d <database_name>                  name of custom database


### initdb

    Usage: 
        hr.py initdb [-h]

    Options:
        -h, --help  show this help message and exit

### load

    Usage: 
        hr.py load [-h] employees_file

    Positional arguments:
        employees_file  name of csv file

    Options:
        -h, --help  show this help message and exit


### generate

    Usage: 
        hr.py generate [-h] [-o] [-q] [-x] [-e [EMPLOYEE_ID]] [-d DIRECTORY] [-a ADDRESS]

    Optional Arguments:
        -h, --help                          show this help message and exit
        -o, --overwrite                     overwrite existing directory
        -q, --qrcode                        generates qrcode
        -x <dimension>                      set custom qr code dimension
        -e <employee_id>                    employee id
        -d <custom_directory_name>          generate files in custom directory
        -a, --address <custom_address>      set custom address

### leave

    Usage: 
        hr.py leave [-h] employee_id date reason

    Positional Arguments:
        employee_id  employee id of absentee
        date         date of absence
        reason       reason of absence


    Options:
        -h, --help   show this help message and exit

### leave_detail

    Usage: 
        hr.py leave_detail [-h] employee_id

    Positional Arguments:
        employee_id  employee id

    Options:
        -h, --help   show this help message and exit

### export

    Usage: 
        hr.py export [-h] [-e EMPLOYEE_ID] [-f FILENAME] [-d DIRECTORY]

    Options:
        -h, --help            show this help message and exit
        -e <employee_id>      employee id
        -f <filename>         csv filename
        -d <directory>        generate file in custom directory


Each row in the csv_file should have the following columns

    Williams,Annette,Psychiatrist,annet.willi@holloway.org,9305709284

This is the last name, first name, designation, email address and
phone number. 

A sample input file `names.csv` is provided in the repo.


## Output:

- Will generate one vCard file per row in the csv_file. The filename
will be the concatenation of firstname and lastname seperated by "_" 
in the row (e.g. annette_williams.vcf).
- Will generate one qr card file per row in the csv_file. The filename
will be the concatenation of firstname and lastname seperated by "_" 
in the row (e.g. annette_williams.qr.png).
- All the files will be in the `vcards` directory.

This is a sample vcard file

    BEGIN:VCARD
    VERSION:2.1
    N:Williams;Annette
    FN:Annette Williams
    ORG:Authors, Inc.
    TITLE:Psychiatrist
    TEL;WORK;VOICE:9305709284
    ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
    EMAIL;PREF;INTERNET:annet.willi@holloway.org
    REV:20150922T195243Z
    END:VCARD


## Execution:

The script can be executed from the command line using:
 
 ```python hr.py <csv_file>```
    