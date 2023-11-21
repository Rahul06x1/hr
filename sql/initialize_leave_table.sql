CREATE TABLE leaves (id SERIAL PRIMARY KEY, date DATE NOT NULL, 
        reason VARCHAR(200) NOT NULL,
        employee_id INTEGER references employees(id) ON DELETE CASCADE,
        UNIQUE(employee_id, date));