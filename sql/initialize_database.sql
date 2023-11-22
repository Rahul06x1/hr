-- CREATE DATABASE %s;

CREATE TABLE employees (id SERIAL PRIMARY KEY, 
        last_name VARCHAR(50) NOT NULL, 
        first_name VARCHAR(50) NOT NULL, designation VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE, phone VARCHAR(50) NOT NULL);

CREATE TABLE leaves (id SERIAL PRIMARY KEY, date DATE NOT NULL, 
        reason VARCHAR(200) NOT NULL,
        employee_id INTEGER references employees(id) ON DELETE CASCADE,
        UNIQUE(employee_id, date));

CREATE TABLE designation (id SERIAL PRIMARY KEY, 
        designation VARCHAR(50) NOT NULL, 
        no_of_leaves INTEGER NOT NULL
        );

INSERT INTO designation (designation, no_of_leaves) 
VALUES  ('Staff Engineer', 20),
        ('Senior Engineer', 18),
        ('Junior Engineer', 12),
        ('Tech. Lead', 12),
        ('Project Manager', 15)