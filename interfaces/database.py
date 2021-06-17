import mariadb
from json import load
from os import getcwd, sep
from typing import Union

from StatusLogger import Logger, Message


class Database(object):
    def __init__(self, database_description_file_path: str) -> None:
        with open(file=database_description_file_path) as database_description_file:
            database_description = load(fp=database_description_file)
        self.user = database_description['user']
        self.password = database_description['password']
        self.host = database_description['host']
        self.port = database_description['port']
        self.database = database_description['database']

    def create_connection(self) -> mariadb.connection:
        return mariadb.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    def create_table(self, table_name: str, attribute_dictionary: dict) -> None:
        # Generate SQL Statement
        sql_statement = "CREATE TABLE {}(\n".format((table_name))
        for attribute_enumeration, (attribute_key, attribute_type) in enumerate(attribute_dictionary.items()):
            if attribute_enumeration == 0:
                sql_statement += attribute_key + " " + attribute_type + " PRIMARY KEY,\n"
            elif attribute_enumeration == len(attribute_dictionary.keys()) - 1:
                sql_statement += attribute_key + " " + attribute_type + ");\n"
            else:
                sql_statement += attribute_key + " " + attribute_type + ",\n"

        connection = self.create_connection()
        connection.close()

    def list_tables(self) -> Union[str, None]:
        connection = self.create_connection()

        sql_cursor = connection.cursor()
        result = sql_cursor.execute("SHOW TABLES;")

        connection.close()

        return result

    def connection_test(self) -> bool:
        try:
            test_connection = self.create_connection()
            Logger.console_log(message="Connection test with " + self.database + " located at " + self.host
                                       + " was a success",
                               status=Message.MESSAGE_TYPE.SUCCESS)
            return True
        except mariadb.Error as err:
            Logger.console_log(message="Unable to establish connection with database " + self.database + ". Error ["
                                       + str(err) + "] was returned",
                               status=Message.MESSAGE_TYPE.FAIL)
            return False


if __name__ == "__main__":
    test_db = Database(database_description_file_path=test_file_path)
    test_db.connection_test()
    print(test_db.list_tables())