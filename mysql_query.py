import pymysql
from ansible.module_utils.basic import *
import re

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


def main():

    # module parameters
    fields = {
        "db": {"required": True, "type": "str"},
        "login_host": {"required": True, "type": "str"},
        "login_user": {"required": True, "type": "str"},
        "login_password": {"required": True, "type": "str"},
        "query": {"required": True, "type": "str"},
        "login_unix_socket": {"required": False, "default": "/var/lib/mysql/mysql.sock", "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)

    db_name = module.params["db"]
    host = module.params["login_host"]
    user = module.params["login_user"]
    password = module.params["login_password"]
    sql_query = module.params["query"]
    socket = module.params["login_unix_socket"]

    db_query = Query(host,
                     db_name,
                     user,
                     password,
                     socket)

    sql_result = db_query.execute(sql_query)

    module.exit_json(changed=False, results=sql_result)


if __name__ == '__main__':
    main()
