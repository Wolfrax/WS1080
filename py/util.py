from datetime import datetime, timedelta
from threading import Event, Thread
import time

__author__ = 'mm'


def ceil(dt):
    # returns the date time to the nearest minute
    if dt.second % 60:
        return dt + timedelta(seconds=60 - dt.second % 60, microseconds=0 - dt.microsecond)
    else:
        return dt


class RepeatTimer(Thread):
    def __init__(self, interval, function, iterations=0, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.iterations = iterations
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def run(self):
        count = 0
        offset = 0
        while not self.finished.is_set() and (self.iterations <= 0 or count < self.iterations):
            if count == 0:
                dt = datetime.now()
                secs = (ceil(dt) - dt).total_seconds()
            else:
                secs = self.interval - offset
            self.finished.wait(secs)
            if not self.finished.is_set():
                t = time.time()
                self.function(*self.args, **self.kwargs)
                offset = time.time() - t
                count += 1

    def cancel(self):
        self.finished.set()


def msecs(dt):
    return time.mktime(dt.timetuple()) * 1000


def bit_is_set(b, bit):
    return bool(b & 2**bit)


def from_bcd(bcd):
    return [(bcd[i] >> 4) * 10 + (bcd[i] & 0x0F) for i in range(len(bcd))]


def to_bcd(bcd):
    return [(bcd[i] / 10) << 4 | (bcd[i] % 10) for i in range(len(bcd))]


def time_to_bcd_str(t):
    buf = ''
    for elem in list(datetime.timetuple(t))[0:5]:
        buf = buf + '0' + str(elem) if elem <= 9 else buf + str(elem)
    return buf


def to_signed_short(byte_high, byte_low):
    sign = -1 if (byte_high & 0x80) else +1
    return sign * (((byte_high & 0x7F) << 3) | byte_low)


def to_unsigned_short_str(n):
    s = hex(n)[2:]  # Skip '0x' prefix

    s = s + '0' if len(s) < 4 else s  # Pad with extra zero if needed
    return s[2:4] + s[0:2]  # Reverse byte order


def parse_ws_record(byte_str):
    if len(byte_str) != 16:
        return None

    return {'delay': byte_str[0],
            'indoor_humidity': byte_str[1],
            'indoor_temp': to_signed_short(byte_str[3], byte_str[2]) * 0.1,
            'outdoor_humidity': byte_str[4],
            'outdoor_temp': to_signed_short(byte_str[6], byte_str[5]) * 0.1,
            'abs_pressure': (byte_str[8] << 8 | byte_str[7]) * 0.1,
            'ave_wind_speed': (((byte_str[11] & 0x0F) << 8) | byte_str[9]) * 0.1,
            'gust_wind_speed': (((byte_str[11] & 0xF0) << 8) | byte_str[10]) * 0.1,
            'wind_dir': byte_str[12] * 22.5,
            'rain_total': (byte_str[14] << 8 | byte_str[13]) * 0.3,
            'status_LOC': (byte_str[15] & 0x40) != 0,
            'status_RCO': (byte_str[15] & 0x80) != 0}


def parse_data_def(byte_str):
    if len(byte_str) != 256 or byte_str[0] != 0x55 or byte_str[1] != 0xaa:
        return None

    return {
        'state': {
            'read_Period': byte_str[16],  # Read period in minutes
            'time_zone': byte_str[24],  # Normally zero unless radio controlled device
            'no_of_readings': (byte_str[28] << 8 | byte_str[27]),  # No of readings, 1 to 4080 (max)

            # Address of the stored reading currently being created.
            # Starts at 256, rises to 65520 in steps of 16 then loops back to 256.
            # The data at this address is updated every 48 seconds or so, until the read period is reached.
            # Then the address is incremented and the next record becomes current.

            # Marker for current writing position
            'current_pos': (byte_str[31] << 8 | byte_str[30]),

            # times 0.1 for hPa
            'relative_pressure': (byte_str[33] << 8 | byte_str[32]) * 0.1,
            'absolute_pressure': (byte_str[35] << 8 | byte_str[34]) * 0.1,

            'current_date_time': from_bcd(byte_str[43:48])  # YY-MM-DD-HH-MM
        },
        'unit_setting': {
            # bit 0: indoor temp: 0 = C, 1 = F
            # bit 1: outdoor temperature: 0 = C, 1 = F
            # bit 2: rain: 0 = mm, 1 = inch
            # bit 5: pressure: 1 = hPa
            # bit 6: pressure: 1 = inHg
            # bit 7: pressure: 1 = mmHg
            'indoor_Temp_F': bit_is_set(byte_str[17], 0),
            'outdoor_Temp_F': bit_is_set(byte_str[17], 1),
            'rain_inch': bit_is_set(byte_str[17], 2),
            'pressure_hPa': bit_is_set(byte_str[17], 5),
            'pressure_inHg': bit_is_set(byte_str[17], 6),
            'pressure_mmHg': bit_is_set(byte_str[17], 7),

            # bit 0: wind speed: 1 = m/s
            # bit 1: wind speed: 1 = km/h
            # bit 2: wind speed: 1 = knot
            # bit 3: wind speed: 1 = m/h
            # bit 4: wind speed: 1 = bft
            'windspeed_ms': bit_is_set(byte_str[18], 0),
            'windspeed_kmh': bit_is_set(byte_str[18], 1),
            'windspeed_knot': bit_is_set(byte_str[18], 2),
            'windspeed_mh': bit_is_set(byte_str[18], 3),
            'windspeed_bft': bit_is_set(byte_str[18], 4)
        },
        'display_option': {
            # bit 0: pressure: 0 = absolute, 1 = relative
            # bit 1: wind speed: 0 = average, 1 = gust
            # bit 2: time: 0 = 24 hour, 1 = 12 hour
            # bit 3: date: 0 = day-month-year, 1 = month-day-year
            # bit 4: time scale(?): 0 = 12 hour, 1 = 24 hour
            # bit 5: date: 1 = show year year
            # bit 6: date: 1 = show day name
            # bit 7: date: 1 = alarm time
            'pressure_relative': bit_is_set(byte_str[19], 0),
            'wind_speed_gust': bit_is_set(byte_str[19], 1),
            'time_12': bit_is_set(byte_str[19], 2),
            'date_month-day-year': bit_is_set(byte_str[19], 3),
            'time_scale_24_hour': bit_is_set(byte_str[19], 4),
            'date_show_year': bit_is_set(byte_str[19], 5),
            'date_show_day_name': bit_is_set(byte_str[19], 6),
            'date_alarm_time': bit_is_set(byte_str[19], 7),

            # bit 0: outdoor temperature: 1 = temperature
            # bit 1: outdoor temperature: 1 = wind chill
            # bit 2: outdoor temperature: 1 = dew point
            # bit 3: rain: 1 = hour
            # bit 4: rain: 1 = day
            # bit 5: rain: 1 = week
            # bit 6: rain: 1 = month
            # bit 7: rain: 1 = total
            'show_outdoor_temp': bit_is_set(byte_str[20], 0),
            'show_outdoor_chill': bit_is_set(byte_str[20], 1),
            'show_outdoor_dew': bit_is_set(byte_str[20], 2),
            'show_rain_hour': bit_is_set(byte_str[20], 3),
            'show_rain_day': bit_is_set(byte_str[20], 4),
            'show_rain_week': bit_is_set(byte_str[20], 5),
            'show_rain_month': bit_is_set(byte_str[20], 6),
            'show_rain_total': bit_is_set(byte_str[20], 7)
        },
        'alarm_enable': {
            # bit 1: time
            # bit 2: wind direction
            # bit 4: indoor humidity low
            # bit 5: indoor humidity high
            # bit 6: outdoor humidity low
            # bit 7: outdoor humidity high
            'time': bit_is_set(byte_str[21], 1),
            'wind_direction': bit_is_set(byte_str[21], 2),
            'indoor_humidity_low': bit_is_set(byte_str[21], 4),
            'indoor_humidity_high': bit_is_set(byte_str[21], 5),
            'outdoor_humidity_low': bit_is_set(byte_str[21], 6),
            'outdoor_humidity_high': bit_is_set(byte_str[21], 7),

            # bit 0: wind average
            # bit 1: wind gust
            # bit 2: rain hourly
            # bit 3: rain daily
            # bit 4: absolute pressure low
            # bit 5: absolute pressure high
            # bit 6: relative pressure low
            # bit 7: relative pressure high
            'wind_average': bit_is_set(byte_str[22], 0),
            'wind_gust': bit_is_set(byte_str[22], 1),
            'rain_hourly': bit_is_set(byte_str[22], 2),
            'rain_daily': bit_is_set(byte_str[22], 3),
            'abs_pressure_low': bit_is_set(byte_str[22], 4),
            'abs_pressure_high': bit_is_set(byte_str[22], 5),
            'rel_pressure_low': bit_is_set(byte_str[22], 6),
            'rel_pressure_high': bit_is_set(byte_str[22], 7),

            # bit 0: indoor temperature low
            # bit 1: indoor temperature high
            # bit 2: outdoor temperature low
            # bit 3: outdoor temperature high
            # bit 4: wind chill low
            # bit 5: wind chill high
            # bit 6: dew point low
            # bit 7: dew point high
            'indoor_temp_low': bit_is_set(byte_str[23], 0),
            'indoor_temp_high': bit_is_set(byte_str[23], 1),
            'outdoor_temp_low': bit_is_set(byte_str[23], 2),
            'outdoor_temp_high': bit_is_set(byte_str[23], 3),
            'wind_chill_low': bit_is_set(byte_str[23], 4),
            'wind_chill_high': bit_is_set(byte_str[23], 5),
            'dew_point_low': bit_is_set(byte_str[23], 6),
            'dew_point_high': bit_is_set(byte_str[23], 7)
        },
        'alarm': {
            'indoor_humidity_high': byte_str[48],  # indoor humidity high
            'indoor_humidity_low': byte_str[49],  # indoor humidity low

            # times 0.1 for C degrees
            'indoor_temp_high': to_signed_short(byte_str[51], byte_str[50]) * 0.1,
            'indoor_temp_low': to_signed_short(byte_str[53], byte_str[52]) * 0.1,

            'outdoor_humidity_high': byte_str[54],  # outdoor humidity high
            'outdoor_humidity_low': byte_str[55],  # outdoor humidity low

            # times 0.1 for C degrees
            'outdoor_temp_high': to_signed_short(byte_str[57], byte_str[56]) * 0.1,
            'outdoor_temp_low': to_signed_short(byte_str[59], byte_str[58]) * 0.1,

            'windchill_high': to_signed_short(byte_str[61], byte_str[60]) * 0.1,
            'windchill_low': to_signed_short(byte_str[63], byte_str[61]) * 0.1,

            'dewpoint_high': to_signed_short(byte_str[65], byte_str[64]) * 0.1,
            'dewpoint_low': to_signed_short(byte_str[67], byte_str[66]) * 0.1,

            # times 0.1 for hPa
            'absolute_pressure_high': (byte_str[69] << 8 | byte_str[68]) * 0.1,
            'absolute_pressure_low': (byte_str[71] << 8 | byte_str[70]) * 0.1,

            'relative_pressure_high': (byte_str[73] << 8 | byte_str[72]) * 0.1,
            'relative_pressure_low': (byte_str[75] << 8 | byte_str[74]) * 0.1,

            'average_wind_speed_bft': byte_str[76],  # average wind speed in beaufort
            'average_wind_speed_ms': (byte_str[78] << 8 | byte_str[77]) * 0.1,  # times 0.1 for m/s

            'gust_wind_speed_bft': byte_str[79],  # gust wind speed in beaufort
            'gust_wind_speed_ms': (byte_str[81] << 8 | byte_str[80]) * 0.1,  # times 0.1 for m/s

            'wind_direction': byte_str[82] * 22.5,  # times 22.5 for degrees from north

            'rain_hourly': (byte_str[84] << 8 | byte_str[83]) * 0.1,  # times 0.1 for mm
            'rain_daily': (byte_str[86] << 8 | byte_str[85]) * 0.1,  # times 0.1 for mm

            'time': from_bcd(byte_str[87:89])  # Hour & Minute
        },
        'minmax': {
            'max_indoor_humidity': byte_str[98],
            'min_indoor_humidity': byte_str[99],

            'max_outdoor_humidity': byte_str[100],
            'min_outdoor_humidity': byte_str[101],

            # times 0.1 for C degrees
            'max_indoor_temp': to_signed_short(byte_str[103], byte_str[102]) * 0.1,
            'min_indoor_temp': to_signed_short(byte_str[105], byte_str[104]) * 0.1,

            'max_outdoor_temp': to_signed_short(byte_str[107], byte_str[106]) * 0.1,
            'min_outdoor_temp': to_signed_short(byte_str[109], byte_str[108]) * 0.1,

            'max_wind_chill': to_signed_short(byte_str[111], byte_str[110]) * 0.1,
            'min_wind_chill': to_signed_short(byte_str[113], byte_str[112]) * 0.1,

            'max_dew_point': to_signed_short(byte_str[115], byte_str[114]) * 0.1,
            'min_dew_point': to_signed_short(byte_str[117], byte_str[116]) * 0.1,

            # times 0.1 for hPa
            'max_abs_pressure': (byte_str[119] << 8 | byte_str[118]) * 0.1,
            'min_abs_pressure': (byte_str[121] << 8 | byte_str[120]) * 0.1,

            'max_rel_pressure': (byte_str[123] << 8 | byte_str[122]) * 0.1,
            'min_rel_pressure': (byte_str[125] << 8 | byte_str[124]) * 0.1,

            # times 0.1 for m/s
            'max_average_wind_speed': (byte_str[127] << 8 | byte_str[126]) * 0.1,
            'max_gust_wind_speed': (byte_str[129] << 8 | byte_str[128]) * 0.1,

            # times 0.1 for mm
            'max_rain_hourly': (byte_str[131] << 8 | byte_str[130]) * 0.1,
            'max_rain_daily': (byte_str[133] << 8 | byte_str[132]) * 0.1,
            'max_rain_weekly': (byte_str[135] << 8 | byte_str[134]) * 0.1,
            'max_rain_monthly': (byte_str[137] << 8 | byte_str[136]) * 0.1,
            'max_rain_total': (byte_str[139] << 8 | byte_str[138]) * 0.1,

            'max_rain_month_nibble': (byte_str[140] >> 4),
            'max_rain_total_nibble': (byte_str[140] & 0x0F),

            'max_indoor_humidity_date': from_bcd(byte_str[141:146]),  # YY-MM-DD-HH-MM
            'min_indoor_humidity_date': from_bcd(byte_str[146:151]),

            'max_outdoor_humidity_date': from_bcd(byte_str[151:156]),
            'min_outdoor_humidity_date': from_bcd(byte_str[156:161]),

            'max_indoor_temp_date': from_bcd(byte_str[161:166]),
            'min_indoor_temp_date': from_bcd(byte_str[166:171]),

            'max_outdoor_temp_date': from_bcd(byte_str[171:176]),
            'min_outdoor_temp_date': from_bcd(byte_str[176:181]),

            'max_wind_chill_date': from_bcd(byte_str[181:186]),
            'min_wind_chill_date': from_bcd(byte_str[186:191]),

            'max_dew_point_date': from_bcd(byte_str[191:196]),
            'min_dew_point_date': from_bcd(byte_str[196:201]),

            'max_abs_pressure_date': from_bcd(byte_str[201:206]),
            'min_abs_pressure_date': from_bcd(byte_str[206:211]),

            'max_rel_pressure_date': from_bcd(byte_str[211:216]),
            'min_rel_pressure_date': from_bcd(byte_str[216:221]),

            'max_ave_wind_speed_date': from_bcd(byte_str[221:226]),
            'max_gust_wind_speed_date': from_bcd(byte_str[226:231]),

            'max_rain_hourly_date': from_bcd(byte_str[231:236]),
            'max_rain_daily_date': from_bcd(byte_str[236:241]),

            'max_rain_weekly_date': from_bcd(byte_str[241:246]),
            'max_rain_monthly_date': from_bcd(byte_str[246:251]),
            'max_rain_total_date': from_bcd(byte_str[251:256])
        }
    }
