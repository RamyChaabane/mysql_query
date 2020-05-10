import pymysql
from ansible.module_utils.basic import *
import re

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['stableinterface'],
                    'supported_by': 'ATOS'}

DOCUMENTATION = '''
---
module: nova_cell
short_description: manage mysql connections in nova_api database
author: Rami CHAABANE
description:
    - Manage mysql connections in nova_api database.
      If I(split), change connections to point to /etc/puppet/my.cnf.d/account_per_controller.cnf
      Else: rollback change to point to tripleo file
options:
   split:
     description:
       - Whether we would like to update connections or not
     required: true
   mysql_password:
     description:
       - Mysql root password
     required: true
   internal_vip:
     description:
       - Virtual internal ip (required if split is false)
     required: false
   nova_password:
     description:
       - Mysql nova password (required if split is false)
     required: false

requirements:
    - "python >= 2.7"
'''

EXAMPLES = '''
# update mysql connections in nova_api database
nova_cell:
  split: true
  mysql_password: "password_mysql"

# rollback configuration after split
nova_cell:
  split: false
  mysql_password: "password_mysql"
  internal_vip: "{{ ip_internal_api }}"
  nova_password: "password_nova"
'''

RETURN = '''
  True whenever the update was done (either split is true or false)
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

        if re.findall("select.*from", query):

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
