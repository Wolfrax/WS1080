#!/usr/local/bin/python

import os
import logging
from logging.handlers import RotatingFileHandler
import json
import time
from datetime import datetime
import util
import ws
from pymongo import MongoClient
import platform

__author__ = 'mm'

WS1080_UPDATE_INTERVAL = 60.0  # According to docs the WS1080 updates current position every 48 sec
ONE_HOUR = 60 * 60 * 1000


def rec_ok(rec):
    ok = 10 <= rec['indoor_humidity'] <= 99
    ok = ok and 10 <= rec['outdoor_humidity'] <= 99
    ok = ok and 0 <= rec['indoor_temp'] <= 60
    ok = ok and -40 <= rec['outdoor_temp'] <= 65
    ok = ok and 0 <= rec['rain'] <= 100
    ok = ok and 0 <= rec['ave_wind_speed'] <= 30
    ok = ok and 0 <= rec['gust_wind_speed'] <= 50
    ok = ok and 918.7 <= rec['abs_pressure'] <= 1079.9
    return ok


def init_rec(rec):
    rec['indoor_humidity_min'] = rec['indoor_humidity']
    rec['indoor_humidity_max'] = rec['indoor_humidity']
    rec['indoor_temp_min'] = rec['indoor_temp']
    rec['indoor_temp_max'] = rec['indoor_temp']
    rec['rain_min'] = rec['rain']
    rec['rain_max'] = rec['rain']
    rec['ave_wind_speed_min'] = rec['ave_wind_speed']
    rec['ave_wind_speed_max'] = rec['ave_wind_speed']
    rec['outdoor_humidity_min'] = rec['outdoor_humidity']
    rec['outdoor_humidity_max'] = rec['outdoor_humidity']
    rec['gust_wind_speed_min'] = rec['gust_wind_speed']
    rec['gust_wind_speed_max'] = rec['gust_wind_speed']
    rec['abs_pressure_min'] = rec['abs_pressure']
    rec['abs_pressure_max'] = rec['abs_pressure']
    rec['outdoor_temp_min'] = rec['outdoor_temp']
    rec['outdoor_temp_max'] = rec['outdoor_temp']

    return rec


def posts_to_sum_post(posts, time_stamp):
    hum_in = []
    hum_out = []
    temp_in = []
    temp_out = []
    rain = []
    rain_total = []
    wind_dir = []
    ave_wind_speed = []
    gust_wind_speed = []
    abs_pressure = []

    for rec in posts:
        hum_in.append(rec['indoor_humidity'])
        hum_out.append(rec['outdoor_humidity'])
        temp_in.append(rec['indoor_temp'])
        temp_out.append(rec['outdoor_temp'])
        rain.append(rec['rain'])
        rain_total.append(rec['rain_total'])
        wind_dir.append(rec['wind_dir'])
        ave_wind_speed.append(rec['ave_wind_speed'])
        gust_wind_speed.append(rec['gust_wind_speed'])
        abs_pressure.append(rec['abs_pressure'])

    return {
        'indoor_humidity': sum(hum_in) / len(hum_in),
        'indoor_humidity_min': min(hum_in),
        'indoor_humidity_max': max(hum_in),

        'outdoor_humidity': sum(hum_out) / len(hum_out),
        'outdoor_humidity_min': min(hum_out),
        'outdoor_humidity_max': max(hum_out),

        'indoor_temp': sum(temp_in) / len(temp_in),
        'indoor_temp_min': min(temp_in),
        'indoor_temp_max': max(temp_in),

        'rain': sum(rain),
        'rain_ave': sum(rain) / len(rain),
        'rain_min': min(rain),
        'rain_max': max(rain),
        'rain_total': rain_total[-1],

        'wind_dir': sum(wind_dir) / len(wind_dir),

        'ave_wind_speed': sum(ave_wind_speed) / len(ave_wind_speed),
        'ave_wind_speed_min': min(ave_wind_speed),
        'ave_wind_speed_max': max(ave_wind_speed),

        'gust_wind_speed': sum(gust_wind_speed) / len(gust_wind_speed),
        'gust_wind_speed_min': min(gust_wind_speed),
        'gust_wind_speed_max': max(gust_wind_speed),

        'abs_pressure': sum(abs_pressure) / len(abs_pressure),
        'abs_pressure_min': min(abs_pressure),
        'abs_pressure_max': max(abs_pressure),

        'time': util.msecs(time_stamp),
        'time_str': time_stamp.isoformat(),
        'latest_update': datetime.now().isoformat(),

        'outdoor_temp': sum(temp_out) / len(temp_out),
        'outdoor_temp_min': min(temp_out),
        'outdoor_temp_max': max(temp_out)
    }


class WS1080:
    def __init__(self):
        self.init = json.load(open("ws.ini", "rw"))
        self.init_logging = self.init["Init"]["Logging"]
        self.init_logfile = self.init["Init"]["Logfile"]
        self.init_rain = self.init["Init"]["Total rain"]
        self.prev_rain = 0

        logging.basicConfig(level=logging.DEBUG) if self.init_logging == "DEBUG" \
            else logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger('WS1080')
        fh = RotatingFileHandler(self.init_logfile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.ws = ws.WS()

        self.timer = util.RepeatTimer(WS1080_UPDATE_INTERVAL, self.sync)
        self.timer.start()

        self.client = MongoClient()
        self.db_weather = self.client.WS
        self.cl_min = self.db_weather.minute
        self.cl_hourly = self.db_weather.hourly
        self.cl_daily = self.db_weather.daily
        self.cl_monthly = self.db_weather.monthly
        self.cl_yearly = self.db_weather.yearly

    def die(self):
        self.timer.cancel()

    def sync(self):
        rec = self.ws.read()

        if rec is None:
            self.logger.warning("Sync, rec is none! Skipping...")
            return

        if rec['rain_total'] < self.init_rain:
            self.logger.warning("Sync, bad rain_total: %d, init_rain: %d", rec['rain_total'], self.init_rain)
            return

        if self.cl_min.count() == 0:
            # Collection is empty, first time usage
            self.logger.info("Update Total rain in ini file: from %.1f to %.1f" % (self.init_rain, rec['rain_total']))

            self.init_rain = rec['rain_total']

            # Update init vector and write for ini-file
            self.init["Init"]["Total rain"] = self.init_rain
            json.dump(self.init, open("ws.ini", "w"), indent=4)

        # init_rain is total accumulated rain since weather station reset, calculate the diff
        rec['rain_total'] = rec['rain_total'] - self.init_rain
        rec['rain'] = rec['rain_total'] - self.prev_rain
        self.prev_rain = rec['rain_total']

        if not rec_ok(rec):
            self.logger.warning("Sync, bad rec! Skipping...")
            self.logger.warning("%s", json.dumps(rec, indent=4, separators=(',', ': ')))
            self.logger.warning("Sync, init_rain: %d prev_rain: %d", self.init_rain, self.prev_rain)
            return

        rec = init_rec(rec)

        self.cl_min.insert_one(rec)

        base_time = datetime.now()

        hour_stamp = base_time.replace(minute=0, second=0, microsecond=0)
        ts = util.msecs(hour_stamp)
        src_posts = self.cl_min.find({'time': {"$gte": ts}})
        sum_post = posts_to_sum_post(src_posts, hour_stamp)
        self.cl_hourly.replace_one({'time': ts}, sum_post, upsert=True)

        day_stamp = base_time.replace(hour=0, minute=0, second=0, microsecond=0)
        ts = util.msecs(day_stamp)
        src_posts = self.cl_hourly.find({'time': {"$gte": ts}})
        sum_post = posts_to_sum_post(src_posts, day_stamp)
        self.cl_daily.replace_one({'time': ts}, sum_post, upsert=True)

        month_stamp = base_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ts = util.msecs(month_stamp)
        src_posts = self.cl_daily.find({'time': {"$gte": ts}})
        sum_post = posts_to_sum_post(src_posts, month_stamp)
        self.cl_monthly.replace_one({'time': ts}, sum_post, upsert=True)

        year_stamp = base_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        ts = util.msecs(year_stamp)
        src_posts = self.cl_monthly.find({'time': {"$gte": ts}})
        sum_post = posts_to_sum_post(src_posts, year_stamp)
        self.cl_yearly.replace_one({'time': ts}, sum_post, upsert=True)

        # Remove old records
        self.cl_min.remove({'time': {"$lt": util.msecs(base_time) - ONE_HOUR}})


def mongo_running():
    if platform.system() == 'Linux':
        # Crude, Linux/POSIX check if mongod is running
        return True if os.popen("ps -Af").read().count('/opt/mongo/bin/mongod') > 0 else False
    else:
        raise NameError('Wrong platform!')


def main():
    while not mongo_running():  # wait for mongod to run
        print("Wait for mongod to start...sleep 5 secs")
        time.sleep(5)  # Wait for 5 secs

    weather_stn = WS1080()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        weather_stn.die()

if __name__ == '__main__':
    main()
