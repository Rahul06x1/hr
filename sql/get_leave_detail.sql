SELECT  COUNT(e.id) as leaves_taken,
        e.first_name, e.last_name,d.no_of_leaves,
        (d.no_of_leaves - COUNT(e.id)) as leaves_remaining
        FROM employees e 
        INNER JOIN leaves l ON e.id = l.employee_id 
        INNER JOIN designation d ON e.designation = d.designation 
        WHERE e.id = %s
        GROUP BY e.id, e.first_name, e.last_name,d.no_of_leaves;
