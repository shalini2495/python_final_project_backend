from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import urllib
from dotenv import load_dotenv
import json
from bson import json_util
import os

load_dotenv()
app = Flask(__name__, template_folder='templates')

user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASS")
print(user)
client = MongoClient(f"mongodb://{user}:{urllib.parse.quote(password)}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.currency

@app.route('/')
def index():
    data = db.currency.find({})
    jsonData = {}
    for x in data:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
    return render_template("index.html", jsonData=jsonData)


if __name__ == "__main__":
    app.run(debug=True)