# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from resource_management.core.logger import Logger
import sys 
current_file_dir = sys.path[0]
lib_dir = current_file_dir + "/../lib"
Logger.info("lib_dir: " + lib_dir)
sys.path.append(lib_dir)
import pymysql as pymysql
from pymysql.cursors import DictCursor

class DorisTool:
    def __init__(self, host, user, password, database, port=9030, charset='utf8mb4'):
        """
        Initialize DorisTool
        :param host: Database host
        :param user: Database user
        :param password: Database password
        :param database: Database name
        :param port: Port number, default 9030
        :param charset: Character set, default utf8mb4
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.connection = None
        self.cursor = None

    def connect(self, max_retries=10, retry_delay=10):
        import time

        for attempt in range(max_retries):
            try:
                self.connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    charset=self.charset,
                    cursorclass=DictCursor  # return results as dictionaries
                )
                self.cursor = self.connection.cursor()
                break  # exit loop if connection is successful
            except pymysql.Error as err:
                Logger.error("Connect to {0} Failed on attempt {1}/{2} !!!".format(self.host, attempt + 1, max_retries))
                Logger.error(str(err))
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")

    def execute_query(self, sql, params=None):
        """
        Execute a query
        :param sql: SQL query
        :param params: SQL parameters (optional)
        :return: Query result (list)
        """
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print("Execute query failed: ".format(e))
            return []

    def execute_update(self, sql, params=None):
        """
        Execute an update statement (insert, update, delete)
        :param sql: SQL update statement
        :param params: SQL parameters (optional)
        :return: Number of affected rows
        """
        try:
            print(sql)
            print(params)
            self.cursor.execute(sql, params)
            self.connection.commit()
            return self.cursor.rowcount
        except pymysql.Error as e:
            self.connection.rollback()
            print("Execute update failed: ".format(e))
            return 0

    def insert(self, table, data):
        """
        Insert data
        :param table: Table name
        :param data: Data to insert (dictionary format, keys are field names, values are field values)
        :return: Number of affected rows
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = "INSERT INTO {table} ({columns}) VALUES ({placeholders})".format(table=table, columns=columns, placeholders=placeholders)
        print(sql)
        print( list(data.values()))
        return self.execute_update(sql, list(data.values()))

    def update(self, table, data, condition):
        """
        Update data
        :param table: Table name
        :param data: Data to update (dictionary format, keys are field names, values are field values)
        :param condition: Update condition (string)
        :return: Number of affected rows
        """
        set_clause = ', '.join(["{0} = %s".format(key) for key in data.keys()])
        sql = "UPDATE {table} SET {set_clause} WHERE {condition}".format(table=table, set_clause=set_clause, condition=condition)
        return self.execute_update(sql, list(data.values()))

    def delete(self, table, condition):
        """
        Delete data
        :param table: Table name
        :param condition: Delete condition (string)
        :return: Number of affected rows
        """
        sql = "DELETE FROM {table} WHERE {condition}".format(table=table, condition=condition)
        return self.execute_update(sql)