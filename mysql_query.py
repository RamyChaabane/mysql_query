import pymysql
from ansible.module_utils.basic import *
import re
import ConfigParser

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

requirements:
    - "python >= 2.7"
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
    description: list of dicts, each dict contains a mapping between the row and its value
    type: complex
'''


class Query:

    def __init__(self,
                 db_host,
                 db_name,
                 db_user,
                 db_password,
                 db_socket):

        self._db_connect = pymysql.Connect(host=db_host,
                                           db=db_name,
                                           user=db_user,
                                           password=db_password,
                                           unix_socket=db_socket,
                                           cursorclass=pymysql.cursors.DictCursor)

    def execute(self, query):

        if re.findall("select.*from", query.lower()):

            with self._db_connect.cursor() as cursor:
                cursor.execute(query)
                query_result = cursor.fetchall()
            self._db_connect.commit()
            self._db_connect.close()

            return query_result
        else:
            sys.exit("only select sql query is supported for now")


class ConfigFile:

    def __init__(self):
        self._config = ConfigParser.ConfigParser()

    def export(self, config_file_path):
        self._config.read(config_file_path)
        user = self._config.get("client", "user")
        password = self._config.get("client", "password")

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
        "config_file": {"required": False, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)

    try:

        db_name = module.params["db"]
        host = module.params["login_host"]

        config_file = module.params["config_file"]

        if isinstance(config_file, str):
            fail_message = (
                "A config file was provided"
                "but also a value was provided for {param}"
                "If a config file is provided, {param} should be excluded."
            )
            for param in (
                    "user", "password"
            ):
                if module.params[param] is not None:
                    module.fail_json(msg=fail_message.format(param=param))

            user, password = ConfigFile().export(config_file)

        else:
            user = module.params["login_user"]
            password = module.params["login_password"]

            fail_message = (
                "A config file or db, login_user, login_password"
                "need to be provided to connect to database"
            )

            if not user or not password or not db_name:
                module.fail_json(msg=fail_message)

        sql_query = module.params["query"]

        if not sql_query:
            module.fail_json(msg="No sql query was provided")

        socket = module.params["login_unix_socket"]

        db_query = Query(host,
                         db_name,
                         user,
                         password,
                         socket)

        sql_result = db_query.execute(sql_query)

        module.exit_json(changed=False, results=sql_result)

    except Exception as error:
        module.fail_json(msg=error)


if __name__ == '__main__':
    main()

