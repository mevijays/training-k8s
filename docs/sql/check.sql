--liquibase formatted sql

--changeset vijay:20240319-001
--comment: Update employee salaries with 10% increase
update employees set salary = salary * 1.1 where tenant_id = 1234;
--rollback update employees set salary = salary / 1.1 where tenant_id = 1234;

--changeset vijay:20240319-002
--comment: Delete employees for specific tenant
delete from employees where tenant_id = 1234;
--rollback INSERT statements would be needed for deleted data

--changeset vijay:20240319-003
--comment: Update employee name
UPDATE employees set name = 'vijay' where tenant_id = 1234;
--rollback update employees set name = 'previous_name' where tenant_id = 1234;

--changeset vijay:20240319-004
--comment: Insert new employee
insert into employees (id, name, salary) values (1, 'John Doe', 50000);
--rollback delete from employees where id = 1;
