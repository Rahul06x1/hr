CREATE TABLE employees (id SERIAL PRIMARY KEY, 
        last_name VARCHAR(50) NOT NULL, 
        first_name VARCHAR(50) NOT NULL, designation VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE, phone VARCHAR(50) NOT NULL);