SELECT EXISTS (
            SELECT 1
            FROM hr_leaves
            WHERE employee_id = %s
            AND date = %s
        );