SELECT  e.first_name, e.last_name,COUNT(e.id) as leaves_taken,
        (d.max_leaves - COUNT(e.id)) as leaves_remaining,
        d.max_leaves
        FROM hr_employees e 
        INNER JOIN hr_leaves l ON e.id = l.employee_id 
        INNER JOIN hr_designations d ON e.title_id = d.id 
        WHERE e.id = %s
        GROUP BY e.id, e.first_name, e.last_name,d.max_leaves;
