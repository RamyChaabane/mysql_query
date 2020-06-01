import pymysql
import re
import ConfigParser
from ast import literal_eval as make_tuple


class Query:

    def __init__(self, db_host, db_name, db_user, db_password, db_socket):

        self._db_connect = pymysql.Connect(host=db_host,
                                           db=db_name,
                                           user=db_user,
                                           password=db_password,
                                           unix_socket=db_socket,
                                           cursorclass=pymysql.cursors.DictCursor)

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

                    # verify if query has been already executed

                    # get position of "values" in the SQL string
                    position = query.lower().find("values (")

                    # get rows names
                    sub_sql = query[:position - 1]
                    start_of_query = re.sub("[()]", "", re.search("into.*", sub_sql, re.IGNORECASE).group())[5:]
                    table_name = start_of_query.split(" ")[0]
                    rows_name = start_of_query.replace(table_name, "")

                    # build select query

                    where_cond = ("='{}' and ".join(rows_name.split(', ')) + "='{}'").format(*query_values)
                    sql_params = dict(table_name=table_name, where_cond=where_cond)
                    verify_sql = "select * from {table_name} where {where_cond}".format(**sql_params)

                    cursor.execute(verify_sql)

                    if cursor.fetchone():
                        return query_to_execute, [], 0

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

    db_name = "classicmodels"
    host = "localhost"
    autocommit = False
    fetchone = False
    positional_args = None
    named_args = None

    sql_query = "select * from payments where customerNumber='496' and paymentDate='2004-12-31'"

    user = "root"
    password = ""
    socket = "/var/lib/mysql/mysql.sock"

    db_query = Query(host, db_name, user, password, socket)
    features = dict(autocommit=autocommit,
                    fetchone=fetchone,
                    positional_args=positional_args,
                    named_args=named_args)

    returned_query, sql_result, rowcount = db_query.execute(sql_query, **features)

    results = dict(query_result=sql_result, query=returned_query, rowcount=rowcount)

    if rowcount == 0:
        changed = False
    else:
        changed = False if sql_result else True

    print results, changed


if __name__ == '__main__':
    main()