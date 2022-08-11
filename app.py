from flask import Flask, request, render_template
from pymongo import MongoClient
import urllib
import pytz
import requests
from dotenv import load_dotenv
import json
from bson import json_util
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

import atexit

# Creating flask framework

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# env file storing mongo atlas credentials
load_dotenv()
app = Flask(__name__, template_folder='templates')

user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASS")
# Establishing connection with mongo db
client = MongoClient(f"mongodb://{user}:{urllib.parse.quote(password)}@ac-qcg93v9-shard-00-00.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-01.wjt7sxv.mongodb.net:27017,ac-qcg93v9-shard-00-02.wjt7sxv.mongodb.net:27017/?ssl=true&replicaSet=atlas-lqwqhj-shard-0&authSource=admin&retryWrites=true&w=majority", connect=False)
db = client.currency

# Getting data from an open currency api using requests library
def getData():
    countries = os.path.join(SITE_ROOT, "static/data", "countries.json")
    data = json.load(open(countries))
    stringData = ",".join(data)
    print("inside the code")
    r = requests.get(f'https://api.exchangerate.host/latest?base=USD&symbols={stringData})')
    if r.status_code == 200:
        ExchangeRateData = r.json()
        db.currency.update_one(
            {"date": ExchangeRateData["date"]},
            {"$setOnInsert": {
            "rates": ExchangeRateData["rates"],
            "date": ExchangeRateData["date"],
            "base": ExchangeRateData["base"]
            }},
            upsert=True
        )
# Batch job that runs ebery 24 hours as per Canada/Eastern timezone    
current_timezone = pytz.timezone("Canada/Eastern")
now = datetime.now().astimezone(current_timezone)


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=getData, trigger="interval", minutes=2, next_run_time=datetime.now().astimezone(current_timezone), timezone=current_timezone)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())



# creating api to post data to our index.html page
@app.route('/', methods=['POST', 'GET'])
def index():
    now = datetime.now().astimezone(current_timezone)
    formatedDate = now.strftime("%Y-%m-%d")
    if (request.method == "GET"):
        deltaWeeks = 1
    if(request.method == "POST"):
        deltaWeeks = request.form['week']
    formatedDateBeforeOneWeek = (now - timedelta(weeks=int(deltaWeeks))).strftime("%Y-%m-%d")
    
    # Getting data by range of date
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
        jsonDataForRange.append(json.dumps(
            x, indent=4, default=json_util.default))
    for x in dataForCurrentDay:
        jsonDataForCurrentDate = json.dumps(
            x, indent=4, default=json_util.default)
    return render_template("index.html", jsonData=jsonDataForCurrentDate, jsonDataForRange=jsonDataForRange, deltaWeeks=deltaWeeks)
# creating api to post data to our currencies.html page
@app.route('/currencies')

# getting all the data from mongodb
def getAllCurrencies():
    now = datetime.now().astimezone(current_timezone)
    project={
        'rates': 1,
        '_id': 0
        }
    formatedDate = now.strftime("%Y-%m-%d")
    result = client['currency']['currency'].find(
        {"date": formatedDate},
        projection=project
    )
    for x in result:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
    return render_template('currencies.html',jsonData=jsonData)

 # creating api to post data to our conversion.html page   
@app.route('/conversion', methods=['POST', 'GET'])
def conversion():
    now = datetime.now().astimezone(current_timezone)
    project={
        'rates': 1,
        '_id': 0
        }
    formatedDate = now.strftime("%Y-%m-%d")
    result = client['currency']['currency'].find(
        {"date": formatedDate},
        projection=project
    )
    for x in result:
        jsonData = json.dumps(x, indent=4, default=json_util.default)
        countryNames = ','.join(list(json.loads(jsonData)['rates'].keys()))
    if(request.method == "GET"):
        return render_template('conversion.html', countryNames=countryNames)
    if(request.method == "POST"):
        # getting data by id from mongo db
        data = json.loads(jsonData)['rates']
        baseCurrency = request.form['baseCurrency']
        conversionCurrency = request.form['conversionCurrency']
        baseAmount = request.form['baseAmount']

        # Formula to get currency conversion
        convertedAmount = (data[conversionCurrency] / data[baseCurrency]) * float(baseAmount)
        return render_template('conversion.html', countryNames=countryNames, baseCurrency=baseCurrency, conversionCurrency=conversionCurrency, baseAmount=baseAmount, convertedAmount=convertedAmount)
if __name__ == "__main__":
    app.run(debug=True)