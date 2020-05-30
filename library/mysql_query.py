import pymysql
from ansible.module_utils.basic import *
import re
import ConfigParser
from ast import literal_eval as make_tuple

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['stableinterface'],
                    'supported_by': 'RAMY'}

DOCUMENTATION = '''
---
module: mysql_query
short_description: run arbitrary MySQL queries
author: Rami CHAABANE
description:
    - run arbitrary MySQL queries
options:
   db:
     description:
       - Name of database to connect to and run queries against
     required: true
   login_host:
     description:
       - Host running the database
     required: true
   login_user:
     description:
       - The username used to authenticate with
     required: true
   login_password:
     description:
       - The password used to authenticate with
     required: true
   query:
     description: 
       - SQL query to run
     required: true
   login_unix_socket:
     description: 
       - Path to a Unix domain socket for local connections
     required: false
     default: "/var/lib/mysql/mysql.sock"
   autocommit:
     description: 
       - Execute in autocommit mode
     required: false
     default: False
   fetchone:
     description: 
       - Fetch only the first result
     required: false
     default: False
   positional_args:
     description:
        - List of values to be passed as positional arguments to the query
     required: False
   named_args:
     description:
        - dict of values to be passed as named arguments to the query
     required: False
     
requirements:
    - "python == 2.7.x"
'''

EXAMPLES = '''
- name: Select query to db acme
  mysql_query:
    db: acme
    login_host: localhost
    login_user: django
    login_password: mysecretpass
    query: SELECT * FROM acme
'''

RETURN = '''
  results:
    description: 
        - dict returning the query that was tried to be executed,
          the query result and the number of affected rows
    type: complex
'''


class Query:

    def __init__(self, db_host, db_name, db_user, db_password, db_socket):

        connection_params = dict(host=db_host,
                                 db=db_name,
                                 user=db_user,
                                 password=db_password,
                                 unix_socket=db_socket,
                                 cursorclass=pymysql.cursors.DictCursor)

        self._db_connect = pymysql.Connect(**connection_params)

    def execute(self, query, **kwargs):

        autocommit = kwargs['autocommit']
        fetchone = kwargs['fetchone']
        positional_args = kwargs['positional_args']
        named_args = kwargs['named_args']

        if autocommit:
            self._db_connect.autocommit(True)

        with self._db_connect.cursor() as cursor:

            query_result = None

            if re.findall("select.*from", query.lower()):

                if positional_args:
                    query = query % tuple(positional_args)

                if named_args:
                    query = query % named_args

                cursor.execute(query)
                query_result = cursor.fetchone() if fetchone else cursor.fetchall()

            elif re.findall("insert into", query.lower()):

                query_to_execute = query
                if positional_args:
                    query_values = tuple(positional_args)
                else:
                    if named_args:
                        query = query % named_args
                        query_to_execute = query

                    values = re.sub("[()]", "", re.search("values.*", query, re.IGNORECASE).group())[7:]
                    query_values = make_tuple(values)

                    for val in values.split(','):
                        query_to_execute = query_to_execute.replace(val, '%s')

                cursor.execute(query_to_execute, query_values)
                if not autocommit:
                    self._db_connect.commit()

            else:

                if positional_args:
                    query = query % tuple(positional_args)

                if named_args:
                    query = query % named_args

                cursor.execute(query)
                if not autocommit:
                    self._db_connect.commit()

            rowcount = cursor.rowcount

        self._db_connect.close()

        return query, query_result, rowcount


class ConfigFile:

    def __init__(self):
        self._config = ConfigParser.ConfigParser()

    def export(self, config_file_path):
        self._config.read(config_file_path)
        user = self._config.get("client", "user").replace('"', '').replace("'", "")
        password = self._config.get("client", "password").replace('"', '').replace("'", "")

        return user, password


def main():

    # module parameters
    fields = {
        "db": {"required": True, "type": "str"},
        "login_host": {"required": False, "default": "localhost", "type": "str"},
        "login_user": {"required": False, "type": "str"},
        "login_password": {"required": False, "type": "str"},
        "query": {"required": True, "type": "str"},
        "login_unix_socket": {"required": False, "default": "/var/lib/mysql/mysql.sock", "type": "str"},
        "config_file": {"required": False, "type": "str"},
        "autocommit": {"required": False, "default": False, "type": "bool"},
        "fetchone": {"required": False, "default": False, "type": "bool"},
        "positional_args": {"required": False, "type": "list"},
        "named_args": {"required": False, "type": "dict"}
    }

    module = AnsibleModule(argument_spec=fields)

    try:

        db_name = module.params["db"]
        host = module.params["login_host"]
        autocommit = module.params["autocommit"]
        fetchone = module.params["fetchone"]
        positional_args = module.params["positional_args"]
        named_args = module.params["named_args"]

        if positional_args and named_args:
            failed_message = (
                "positional_args param was provided but also named_args param "
                "can't specify both, one of them should be excluded"
            )
            module.fail_json(msg=failed_message)

        config_file = module.params["config_file"]

        if isinstance(config_file, str):
            fail_message = (
                "A config file was provided "
                "but also a value was provided for {param} "
                "If a config file is provided, {param} should be excluded."
            )
            for param in (
                    "login_user", "login_password"
            ):
                if module.params[param] is not None:
                    module.fail_json(msg=fail_message.format(param=param))

            user, password = ConfigFile().export(config_file)

        else:
            user = module.params["login_user"]
            password = module.params["login_password"]

            fail_message = (
                "A config file or {db, login_user and login_password}"
                " need to be provided to connect to database"
            )

            if not user or password is None or not db_name:
                module.fail_json(msg=fail_message)

        sql_query = module.params["query"]

        socket = module.params["login_unix_socket"]

        db_query = Query(host, db_name, user, password, socket)

        features = dict(autocommit=autocommit,
                        fetchone=fetchone,
                        positional_args=positional_args,
                        named_args=named_args)

        returned_query, sql_result, rowcount = db_query.execute(sql_query, **features)

        results = dict(query_result=sql_result, query=returned_query, rowcount=rowcount)

        changed = False if sql_result else True

        module.exit_json(changed=changed, module_results=results)

    except Exception as error:
        module.fail_json(msg=error)


if __name__ == '__main__':
    main()
