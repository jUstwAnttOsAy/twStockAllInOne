# import
import pandas as pd
from pymongo import MongoClient

class MongoDB:
    # 建構式，指定連線客戶端以及DB
    def __init__(self, db, col = ''):
        self.__client = MongoClient('mongodb+srv://swdax545:6h987JG7wNYbSpw@twstockallinonecluster.caqnh.mongodb.net/test')
        self.__DB = self.__client[db]
        self.__col = self.__DB[col] if col!='' else ''

    def set(self, col):
        self.__col = self.__DB[col]

    def insert(self, df):
        if self.check() == False:
            return
        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        r = self.__col.insert_many(data_dict)
        return r.inserted_ids

    def query(self, query = {}):
        if self.check() == False:
            return
        data = self.__col.find(query, {"_id": 0})
        df = pd.DataFrame(data)
        return df

    def remove(self, query = {}):
        if self.check() == False:
            return
        r = self.__col.delete_many(query)
        return r.deleted_count

    def drop(self):
        if self.check() == False:
            return
        self.__col.drop()

    def check(self):
        if self.__col == '':
            print('Please Set Collection First!')
            return False
        try:
            self.__col.stats
        except:
            print('Connection Failed!')
            return False

        return True

'''
# import
from pymongo import MongoClient

# connection
client = MongoClient() # 如果你只想連本機端的server你可以忽略

#DB
# lsdb = conn.list_database_names()
dbData = client['data']

#collection
# lscol = dbData.list_collection_names()
colData = dbData['revenue']

# test if connection success
colData.stats  # 如果沒有error，你就連線成功了。


#Insert 
#one
mydict = { "name": "RUNOOB", "alexa": "10000", "url": "https://www.runoob.com" }
x = colData.insert_one(mydict) 
print(x.inserted_id)

#many
mylist = [
  { "name": "Taobao", "alexa": "100", "url": "https://www.taobao.com" },
  { "name": "QQ", "alexa": "101", "url": "https://www.qq.com" },
  { "name": "Facebook", "alexa": "10", "url": "https://www.facebook.com" },
  { "name": "知乎", "alexa": "103", "url": "https://www.zhihu.com" },
  { "name": "Github", "alexa": "109", "url": "https://www.github.com" }
]
x = colData.insert_many(mylist)
print(x.inserted_ids)

#insert with id
mylist = [
  { "_id": 1, "name": "RUNOOB", "cn_name": "菜鸟教程"},
  { "_id": 2, "name": "Google", "address": "Google 搜索"},
  { "_id": 3, "name": "Facebook", "address": "脸书"},
  { "_id": 4, "name": "Taobao", "address": "淘宝"},
  { "_id": 5, "name": "Zhihu", "address": "知乎"}
]
 
x = colData.insert_many(mylist)
print(x.inserted_ids)

#Find
#get first data
x = colData.find_one()
print(x)

#get all
for x in colData.find():
  print(x)

#return selected column
#1 means visible, 0 means invisible
#only _id can set 0,1, other only set 1 or 0 at one time
for x in colData.find({},{ "_id": 0, "name": 1, "alexa": 1 }):
  print(x)

#select by condition
#match
myquery = { "name": "RUNOOB" }
#greater
myquery = { "name": { "$gt": "H" } }
#regx
myquery = { "name": { "$regex": "^R" } }

#all
mydoc = colData.find(myquery)
#top 3
myresult = colData.find().limit(3)
#sort
mydoc = colData.find(myquery).sort("alexa")
#descending
mydoc = colData.find(myquery).sort("alexa", -1)

for x in mydoc:
  print(x)

#update
#query alexa = 10000 and update first row column alexa to 12345
myquery = { "alexa": "10000" }
newvalues = { "$set": { "alexa": "12345" } }
colData.update_one(myquery, newvalues)
 
#query name start F and update all rows column alexa to 123
myquery = { "name": { "$regex": "^F" } }
newvalues = { "$set": { "alexa": "123" } }
 
x = colData.update_many(myquery, newvalues)
#return update row count
print(x.modified_count) 

#Delete
#delete one row name match Taobao
myquery = { "name": "Taobao" }
colData.delete_one(myquery)

#delete all row which name start with F
myquery = { "name": {"$regex": "^F"} }
x = colData.delete_many(myquery)
#return deleted rows count
print(x.deleted_count, "个文档已删除")

#remove all collection
colData.drop()
'''