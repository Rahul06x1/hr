SELECT EXISTS (
            SELECT datname
            FROM pg_catalog.pg_database
            WHERE lower(datname) = %s
        );