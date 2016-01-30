#!/usr/bin/env python

from pymongo import MongoClient
from flask import Flask, request
import json
from datetime import datetime
import time
import pprint

__author__ = 'mm'
app = Flask(__name__)


@app.route("/ws/minute")
def ws_min():
    start_time = time.mktime(datetime.now().timetuple()) - int(request.args.get('StartTime'))
    stop_time = int(request.args.get('StopTime'))

    posts = MongoClient().WS.minute.find({"time": {"$gte": start_time, "$lte": stop_time}},
                                         projection={"_id": False}).sort("time")
    return json.dumps([post for post in posts])


@app.route("/ws/hourly")
def emc_db():
    start_time = int(request.args.get('StartTime'))
    stop_time = int(request.args.get('StopTime'))

    posts = MongoClient().WS.hourly.find({"time": {"$gte": start_time, "$lte": stop_time}},
                                         projection={"_id": False}).sort("time")

    return json.dumps([post for post in posts])


@app.route("/ws/daily")
def ws_daily():
    start_time = int(request.args.get('StartTime'))
    stop_time = int(request.args.get('StopTime'))

    posts = MongoClient().WS.daily.find({"time": {"$gte": start_time, "$lte": stop_time}},
                                         projection={"_id": False}).sort("time")
    return json.dumps([post for post in posts])


@app.route("/ws/monthly")
def ws_monthly():
    start_time = int(request.args.get('StartTime'))
    stop_time = int(request.args.get('StopTime'))

    posts = MongoClient().WS.monthly.find({"time": {"$gte": start_time, "$lte": stop_time}},
                                           projection={"_id": False}).sort("time")
    return json.dumps([post for post in posts])


@app.route("/ws/yearly")
def ws_yearly():
    posts = MongoClient().WS.yearly.find(projection={"_id": False}).sort("time")
    return json.dumps([post for post in posts])


@app.route("/ws/logfile")
def ws_log():
    with open('ws.err', 'r') as f:
        log = f.read()
    return log

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
