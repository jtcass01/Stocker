from os import getcwd
from os.path import join
from typing import TextIO, Dict

from holdings import Holdings

def generate_stocker_database_scripts(holdings: Holdings,
                                      database_sql_script_location: str = join(getcwd(), "MarketDB.sql"),
                                      database_name: str = "Stocker_Market_Data") -> None:
    with open(database_sql_script_location, "w+") as database_script:
        generate_database(database_script=database_script, database_name=database_name)

        # Generate tables for holdings with prices.
        for holding_dict in [holdings.stocks, holdings.cryptocoins]:
            for holding_name, holding in holding_dict.items():
                holding.generate_database_table(database_script=database_script)
      

def generate_database(database_script: TextIO, database_name: str) -> None:
    """[summary]

    Args:
        database_script (TextIO): [description]
        database_name (str): [description]"""
    database_script.write("CREATE DATABASE {};\n\n".format(database_name))
