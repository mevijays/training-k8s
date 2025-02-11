UPDATE address SET age = 34 WHERE TENANT_ID = "v123";
-- Adding INSERT statement without WHERE TENANT_ID (should pass validation)
INSERT INTO employees (id, name, salary) VALUES (1, 'John Doe', 50000);

-- Adding another INSERT with WHERE clause (not typical, but for testing)
INSERT INTO employees (id, name, salary, tenant_id) SELECT id, name, salary, 1234 FROM temp_employees WHERE TENANT_ID = 1234;
