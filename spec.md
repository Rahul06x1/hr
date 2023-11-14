1. Objective:

Generates visiting cards and their qr codes for a list of employees provided in a CSV
file


2. Input:

Command-Line Arguments:
    csv_file: The path to the CSV file containing contact information.
   

Each row in the csv_file should have the following columns

    Williams,Annette,Psychiatrist,annet.willi@holloway.org,9305709284

This is the last name, first name, designation, email address and
phone number. 

A sample input file `names.csv` is provided in the repo.


3. Output:

    - Will generate one vCard file per row in the csv_file. The filename
will be the concatenation of firstname and lastname seperated by "_" 
in the row (e.g. annette_williams.vcf).
    - Will generate one qr card file per row in the csv_file. The filename
will be the concatenation of firstname and lastname seperated by "_" 
in the row (e.g. annette_williams.qr.png).
    - All the files will be in 
the `vcards` directory.

This is a sample vcard file

    Name: Annette
    Full Name: Annette Williams
    ORG:Authors, Inc.
    TITLE: Psychiatrist
    TEL;WORK;VOICE: 9305709284
    ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
    EMAIL;PREF;INTERNET: annet.willi@holloway.org
    REV:20150922T195243Z


4. Execution:

The script can be executed from the command line using:
 
    `python hr.py <csv_file>`
    