import sqlite3
import os, datetime, time, re
from Settings.Handler import *
# from Handler import *

class DbManager:

    def __init__(self, db_name):
        self.connect = db_name
        self.cursor = db_name.cursor()

    def ClearDatabase(self):
        """Completely Clean the Database\n
        WARNING : This will completely delete all your current data inside this Database"""
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'""")
        tables = [table_name[0] for table_name in self.cursor.fetchall()]
        for table_name in tables:
            self.cursor.execute("""DROP TABLE {};""".format(table_name))
            self.connect.commit()
        return "Database has been Cleaned"

    def CreateTable(self, table_name: str, **column):
        """table_name -> Name of Table\n
        column=type -> Each Column of Table"""
        try:
            col, type, complete_column = [column_name for column_name in column], [column[column_type] for column_type in column], []
            for i in range(len(column)):
                complete_column.append("{} {}".format(col[i], type[i]))
            self.cursor.execute("""CREATE TABLE {} ({});""".format(table_name, ",".join(complete_column)))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Table has been Created"

    def DropTable(self, table_name: str):
        """table_name -> Name of the Existing Table"""
        try:
            self.connect.execute("""DROP TABLE IF EXISTS {};""".format(table_name))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Deleted Successfully"

    def GetTables(self):
        """Get all Table from current Database"""
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'""")
        return [table_name[0] for table_name in self.cursor.fetchall()]

    def SelectTableData(self, table_name: str):
        """table_name -> Name of Existing Table"""
        try:
            self.cursor.execute("""SELECT * FROM {};""".format(table_name))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Data from {} Selected".format(table_name)

    def SelectRowData(self, table_name: str, condition: str):
        """table_name -> Name of Existing Table\n
        condition -> Conditional Statement to select a Specific Data"""
        try:
            self.cursor.execute("""SELECT * FROM {} WHERE {};""".format(table_name, condition))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Row(s) Data Selected"

    def AddColumn(self, table_name: str, column_name: str, type):
        """table_name -> Name of Existing Table\n
        column_name -> Name of New Column\n
        type -> This new Column Data Type"""
        try:
            new_format_column = "{} ".format(column_name) + type
            self.cursor.execute("""ALTER TABLE {} ADD COLUMN {};""".format(table_name, new_format_column))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Column {} Inserted to {}".format(column_name, table_name)
    
    def GetColumnsTable(self, table_name: str):
        """table_name -> Name of Existing Table"""
        self.cursor.execute("""PRAGMA table_info({})""".format(table_name))
        return [column_name[1:3] for column_name in self.cursor.fetchall()]

    def InsertData(self, table_name: str, **column):
        """table_name -> Name of Existing Table\n
        column=value -> Individual Insert Data"""
        try:
            col, val, fixed_value = ",".join([column_name for column_name in column]), [column[column_value] for column_value in column], []
            for new_value in val:
                if type(new_value) != str:
                    if type(new_value) == datetime.datetime:
                        fixed_value.append("\'{}\'".format(str(new_value).split('.')[0]))
                    if type(new_value) == int:
                        fixed_value.append(str(new_value))
                else:
                    fixed_value.append("\"{}\"".format(new_value))
            self.cursor.execute("""INSERT INTO {} ({}) VALUES ({})""".format(table_name, col, ",".join(fixed_value)))
            self.connect.commit()
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Data Inserted Successfully"

    def DeleteRow(self, table_name: str, **condition):
        """table_name -> Name of Existing Table\n
        condition -> Find a Data By Specific Value <column_name=value>"""
        try:
            the_key = [cond for cond in condition]
            self.cursor.execute("""DELETE FROM {} WHERE {};""".format(table_name, "{} = {}".format(the_key[0], condition[the_key[0]])))
            self.connect.commit()
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "A Row Data of {} has been Deleted".format(table_name)
    
    def ClearTable(self, table_name: str):
        """table_name -> Name of Existing Table\n
        This Method will Delete a Specific kind of Data"""
        try:
            self.cursor.execute("""DELETE FROM {};""".format(table_name))
        except Exception as exc:
            print(type(exc), exc)
        else:
            return "Table {} Cleaned".format(table_name)
        
    @classmethod
    def connect_db(cls, db_dir: str):
        """Connect Database File"""
        try:
            if not db_dir.endswith(".db"):
                raise NameError
            if not os.path.isfile(db_dir):
                f = open(db_dir, "w")
                f.write("")
                f.close()
        except Exception as exc:
            if type(exc) == NameError:
                print("Wrong File Type. It must be .db File!")
            else:
                print(type(exc), exc)
        return cls(sqlite3.connect(db_dir))

# if __name__ == '__main__':
#     conn = DbManager.connect_db("./DataPack/member.db")
#     # conn.CreateTable("guilds", id="VARCHAR(255) PRIMARY KEY NOT NULL", name="VARCHAR(255)", created_at="DATETIME NOT NULL", region="VARCHAR(255) NOT NULL", prefix="CHAR(10) NOT NULL")
#     # conn.CreateTable("uno_raw", id="INT(2) PRIMARY KEY NOT NULL", color="CHAR(10) NOT NULL", type="CHAR(10) NOT NULL", name="CHAR(55) NOT NULL", image_url="TEXT", bin="BLOB NOT NULL") + number
#     # conn.CreateTable("ows_results", server_id="VARCHAR(255) NOT NULL", channel_id="VARCHAR(255)", story_title="VARCHAR(255)", story="TEXT NOT NULL")
#     # conn.CreateTable("available_game", server_id="VARCHAR(255) PRIMARY KEY NOT NULL", available="TEXT")
#     # conn.CreateTable("point", id="VARCHAR(255) PRIMARY KEY NOT NULL", coins="INT NOT NULL")
#     conn.cursor.execute("""SELECT * FROM point;""")
#     for i in conn.cursor.fetchall():
#         print(i)
#     conn.cursor.close()