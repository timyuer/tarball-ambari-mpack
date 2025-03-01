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

from scripts.doris_tool import DorisTool

if __name__ == "__main__":
    # init DorisTool
    db = DorisTool(
        host="192.168.110.246",
        user="root",
        password="",
        port = 9030,
        database="mysql"
    )

    # connect to database
    db.connect()

    # sql = format("ALTER SYSTEM ADD BACKEND 'bdp09:9050'")
    # print("add_be: " + sql)
    # db.execute_update(sql)

    # query data
    result = db.execute_query("SHOW FRONTENDS")
    print("query result:", result)
    for row in result:
        print(row)
        import json
        print(json.dumps(row, indent=4))
        json_dict = json.loads(json.dumps(row))
        IsMaster = json_dict['IsMaster']
        if IsMaster == "true":
            print("Master: " + json_dict['Host'])
            fe_master_host = json_dict['Host']

    # # insert data
    # insert_data = {
    #     'username': 'test_user',
    #     'email': 'test@example.com',
    #     'age': 25
    # }
    # insert_count = db.insert("user", insert_data)
    # print("insert {insert_count} data".format(insert_count=insert_count))

    # # update data
    # update_data = {
    #     'email': 'new_email@example.com',
    #     'age': 30
    # }
    # update_count = db.update("user", update_data, "username = 'test_user'")
    # print("update {update_count} data".format(update_count=update_count))

    # # delete data
    # delete_count = db.delete("user", "username = 'test_user'")
    # print("delete {delete_count} data".format(delete_count=delete_count))

    # close database connection
    db.close()