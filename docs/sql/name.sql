update address set age = 34 
where TENANT_ID = "v123";
-- Adding INSERT statement without WHERE TENANT_ID (should pass validation)
insert into employees (id, name, salary) values (1, 'John Doe', 50000);

-- Adding another INSERT with WHERE clause (not typical, but for testing)
insert into employees (id, name, salary, tenant_id) select id, name, salary, 1234 from temp_employees 
where TENANT_ID = 1234;
