import pymongo

def Insert():
    client=pymongo.MongoClient('mongodb://localhost:27017')
    mydb=client['Employee']
    information = mydb.table1