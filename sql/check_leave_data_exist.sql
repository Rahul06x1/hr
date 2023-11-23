SELECT EXISTS (
            SELECT 1
            FROM leaves
            WHERE employee_id = %s
            AND date = %s
        );