SELECT EXISTS (
            SELECT id
            FROM leaves
            WHERE employee_id = %s
            AND date = %s
        );