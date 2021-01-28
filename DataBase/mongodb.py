from pymongo import MongoClient
import pandas as pd
# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb+srv://swdax545:<password>@twstockallinonecluster.caqnh.mongodb.net/test')

db=client['firstmongo']
collection = db['firstcollect']
emp_rec1 = {
        "name":"Mr.yen",
        "eid":24,
        "location":"delhi"
        }
maxTimeMS=1
rec_id1 = collection.insert_one(emp_rec1)
print("Data inserted with record ids",rec_id1)
# Printing the data inserted
cursor = collection.find()
for record in cursor:
    print(record)




