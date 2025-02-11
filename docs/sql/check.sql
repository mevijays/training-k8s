UPDATE employees
SET salary = salary * 1.1
WHERE TENANT_ID = 1234;

DELETE FROM employees
WHERE TENANT_ID = 1234;

UPDATE employees
SET NAME = "vijay";
WHERE TENANT_ID = 1234;
