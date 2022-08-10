from xml.etree.ElementInclude import include
from flask import Flask, jsonify, request, render_template
from pkg_resources import require
from pymongo import MongoClient
import urllib
import requests
import schedule
from dotenv import load_dotenv
import json
from bson import json_util
import os
from datetime import date, datetime, timedelta

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

load_dotenv()
app = Flask(__name__, template_folder='templates')

user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASS")
client = MongoClient(f"mongodb://{user}:{urllib.parse.quote(password)}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority", connect=False)
db = client.currency
def getData():
    countries = os.path.join(SITE_ROOT, "static/data", "countries.json")
    data = json.load(open(countries))
    stringData = ",".join(data)
    
    r = requests.get(f'https://api.exchangerate.host/latest?base=USD&symbols={stringData})')
    if r.status_code == 200:
        ExchangeRateData = r.json()
        db.currency.insert_one({
            "rates": ExchangeRateData["rates"],
            "date": ExchangeRateData["date"],
            "base": ExchangeRateData["base"]
        })
# schedule.every().day.at("01:00").do(getData)
# getData()


@app.route('/')
def index():
    currentDate = date.today()
    formatedDate = currentDate.strftime("%Y-%m-%d")
    formatedDateBeforeOneWeek = (currentDate - timedelta(weeks=1)).strftime("%Y-%m-%d")
    findQuery = {
    '$and': [
        {
            'date': {
                '$lte': formatedDate
            }
        }, {
            'date': {
                '$gte': formatedDateBeforeOneWeek
            }
        }
    ]
}
    data = db.currency.find(findQuery)
    dataForCurrentDay = db.currency.find({"date": formatedDate})
    jsonDataForCurrentDate = {}
    jsonDataForRange = []
    for x in data:
        jsonDataForRange.append(json.dumps(x, indent=4, default=json_util.default))
    for x in dataForCurrentDay:
        jsonDataForCurrentDate = json.dumps(x, indent=4, default=json_util.default)
    return render_template("index.html", jsonData=jsonDataForCurrentDate, jsonDataForRange=jsonDataForRange)


@app.route('/currencies')
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
        return render_template('conversion.html', countryNames=countryNames)
    if(request.method == "POST"):
        data = json.loads(jsonData)['rates']
        baseCurrency = request.form['baseCurrency']
        conversionCurrency = request.form['conversionCurrency']
        baseAmount = request.form['baseAmount']
        convertedAmount = (data[conversionCurrency] / data[baseCurrency]) * float(baseAmount)
        return render_template('conversion.html', countryNames=countryNames, baseCurrency=baseCurrency, conversionCurrency=conversionCurrency, baseAmount=baseAmount, convertedAmount=convertedAmount)
if __name__ == "__main__":
    app.run(debug=False)