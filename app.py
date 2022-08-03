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
client = MongoClient(f"mongodb://{user}:{urllib.parse.quote(password)}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority", connect=False)
db = client.currency

@app.route('/')
def index():
    data = db.currency.find({})
    jsonData = {}
    for x in data:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
    return render_template("index.html", jsonData=jsonData)

@app.route('/currencies', methods=['GET'])
def getAllCurrencies():
    project={
        'rates': 1,
        '_id': 0
        }
    result = client['currency']['currency'].find(
        projection=project
    )
    for x in result:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
        countryNames = ','.join(list(json.loads(jsonData)['rates'].keys()))
    if(request.method == "GET"):
        return render_template('currencies.html',jsonData=jsonData)

@app.route('/conversion', methods=['POST', 'GET'])
def conversion():
    project={
        'rates': 1,
        '_id': 0
        }
    result = client['currency']['currency'].find(
        projection=project
    )
    for x in result:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
        countryNames = ','.join(list(json.loads(jsonData)['rates'].keys()))
    if(request.method == "GET"):
        print(countryNames)
        return render_template('conversion.html', countryNames=countryNames)
    if(request.method == "POST"):
        data = json.loads(jsonData)['rates']
        baseCurrency = request.form['baseCurrency']
        conversionCurrency = request.form['conversionCurrency']
        baseAmount = request.form['baseAmount']
        convertedAmount = (data[conversionCurrency] / data[baseCurrency]) * float(baseAmount)
        return render_template('conversion.html', countryNames=countryNames, baseCurrency=baseCurrency, conversionCurrency=conversionCurrency, baseAmount=baseAmount, convertedAmount=convertedAmount)
if __name__ == "__main__":
    app.run()