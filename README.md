# mysql_query
This repository includes also a CI/CD pipline using Jenkins for building a test environment to deliver the module

# Synopsis
Ansible module runs arbitrary MySQL queries.

# Requirements
The below requirements are needed on the host that executes this module.

PyMySQL

# Parameters
|Parameter|Choices/Defaults|Comments|
|---------|----------------|--------|
|autocommit<br>boolean|Choices:<br>false ←<br>true|Execute in autocommit mode when the query|
|db<br>string||Name of database to connect to and run queries against|
|login_host<br>`string`|Default:<br>localhost|Host running the database<br>should be execluded if config_file was provided|
|login_password<br>string||The password used to authenticate with<br>should be execluded if config_file was provided|
|login_unix_socket<br>string|Default:<br>/var/lib/mysql/mysql.sock|Path to a Unix domain socket|
|login_user<br>string||The username used to authenticate with|
|named_args<br>dictionary||Dictionary of key-value arguments to pass to the query|
|positional_args<br>list||List of values to be passed as positional arguments to the query|
|query<br>string||SQL query to run|
|fetchone||get only the first result of select SQL query|
|config_file||ini file containing client database credentials<br>If this parameter is specified, login_user and login_password should be excluded|

# Examples
```yaml
- name: Select query to db acme with positional arguments
  mysql_query:
    db: acme
    login_user: django
    login_password: mysecretpass
    query: SELECT * FROM acme WHERE id = %s AND story = %s
    positional_args:
    - 1
    - test

- name: Select query to test_db with named_args
  mysql_query:
    db: acme
    login_user: django
    login_password: mysecretpass
    query: SELECT * FROM test WHERE id = %(id_val)s AND story = %(story_val)s
    named_args:
      id_val: 1
      story_val: test
    
- name: Insert query to test_table in db test_db
  mysql_query:
    db: acme
    login_user: django
    login_password: mysecretpass
    query: INSERT INTO test_table (id, story) VALUES (2, 'my_long_story')

- name: fetch only the first result of select SQL query
  mysql_query:
  	db: test_db
    config_file: '/root/.my.cnf'
    query: select * from test_table
    fetchone: true
```

# Return Values
|key|Returned|Description|
|---|--------|-----------|
|query<br>string|always|Query that was tried to be executed|
|query_result<br>list|changed|List of dictionaries in column:value form representing returned rows|
|rowcount<br>integer|always|Number of affected rows.|

