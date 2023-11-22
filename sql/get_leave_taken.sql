SELECT COUNT(*) FROM employees e 
        INNER JOIN leaves l ON e.id = l.employee_id WHERE e.id=%s