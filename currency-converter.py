from flask import Flask, request
from flask_restful import Resource, Api
import requests
from pymongo import MongoClient
import urllib
import json
from bson import json_util
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
api = Api(app)
user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASS")
print(user)
print(password)
print(f"mongodb://{user}:{password}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority")
client = MongoClient(f"mongodb://{user}:{urllib.parse.quote(password)}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.currency
url = 'https://api.exchangerate.host/latest'
class CurrencyConverter(Resource):
    def get(self):
        response = requests.get(url)
        data = response.json()
        db.currency.insert_one(data)
        return {"message": "data entered successfully"}
class CurrencyConverterData(Resource):
    def get(self):
        # return [doc for doc in db.currency.find()]
        data = db.currency.find({})
        for x in data:
            return json.dumps(x, indent=4, default=json_util.default)
        # print(data)

api.add_resource(CurrencyConverter, '/')
api.add_resource(CurrencyConverterData, '/getCurrencies')
if(__name__ == "__main__"):
    app.run(debug=True)