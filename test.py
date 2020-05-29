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

    def execute(self, query, autocommit, fetchone, positional_args, named_args):

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

        return query_result, rowcount


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

    named_args = dict(num=1704,
                      last_name='lastName_test',
                      first_name='Name_test',
                      ext='x1250',
                      email='test@classicmodelcars.com',
                      code=5,
                      job='Sales Rep')

    sql_query = "insert into employees (employeeNumber, lastName, firstName, extension," \
                " email, officeCode, jobTitle) VALUES (%(num)s, %(last_name)s, %(first_name)s," \
                " %(ext)s, %(email)s, %(code)s, %(job)s)"

    user = "root"
    password = ""
    socket = "/var/lib/mysql/mysql.sock"

    db_query = Query(host, db_name, user, password, socket)
    sql_result, rowcount = db_query.execute(sql_query,
                                            autocommit,
                                            fetchone,
                                            positional_args,
                                            named_args)

    print sql_result


if __name__ == '__main__':
    main()
