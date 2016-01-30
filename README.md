# WS1080

This is a implementation of reading and displaying data from a weather station such as WH1080.

There is some python scripts that recurrently read from the weather station over USB and store the retrieved
information into a Mongo database. The information is retrieved  by a REST compliant interface at a server, using
some javascript on a web-client.

As WH1080 is a cheap device, the sensors have limited accuracy and the weather station as such is not very reliable.
Therefore there are some error checking of the data before it is being stored into the database.

This is currently executed on a raspberry pi, available here <http://www.viltstigen.se/ws>

An alternative implementation (more extensive) of vs the same type of weather station is available
[here](https://github.com/jim-easterbrook/pywws).

## Overview

The python scripts are as follows

* dev.py, this is the lowest level script, reading the weather station through pyusb
* ws.py, this is the script that implements the WS object using the dev-script
* collector.py, this is the daemon application script using the ws-script. It reads data and stores into Mongo recurrently
* util.py, various parsing of weather station data and other housekeeping
* emitter.py, the REST server implementation using flask, responds to javascript client

The javascripts implements the front-end, available as:

* ws.js, library for plotting of retrieved data, using [highcharts](http://www.highcharts.com/) for nice presentations
* ws.css, css layout of graphical objects
* index.html, the root html page using ws.js and ws.css
* log.html, to read the ws.log on the server

So, collector.py is executed as a daemon, controlled by `supervisor` (see link below), reading data every minute from
the weather station. Refer to `ws_collector.conf` for parameters.

Data is stored into a Mongo database, named `WS`.

There are 5 Mongo collections of data with different granularity:

* `minute`, data read from the weather station, maximum 1 hour of data is stored here
* `hourly`, hourly data averaged from `minute` collection, never erased
* `daily`, daily data averaged from `hourly` collection, never erased
* `monthly`, monthly data averaged from `daily` collection, never erased
* `yearly`, yearly data averaged fomr `monthly` collection, never erased

[nginx](https://www.nginx.com/) is used as a web and proxy server. Use `sudo apt-get install nginx` if needed.
(Throw away the Apache server by doing `sudo update-rc.d -f apache2 remove`)

nginx sends HTTP requests upstream as configured, towards a gunicorn WSGI HTTP server using flask. This respond to
requests by returning JSON encoded data that is unpacked by the client javascript and presented in graphs.
Refer to nginx how to configure it as a proxy, essential lines follows below

    upstream ws {
        server 127.0.0.1:8092; # mm: this points to the gunicorn python app server listening at port 8092 (ws)
    }
    location /ws/ {
        try_files $uri $uri/ $uri/index.html $uri.html @ws;
    }

    location @ws {
        proxy_pass         http://ws;
        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
    }

Above instructs nginx to send any request to the ws-subdomain upstream on the localhost using port 8092.
The gunicorn server listen on this port and respond back to the request, works great.

## Documentation

Have a look into the `docs` directory of this project.

`Weather station memory map` provides detailed information of the data read from the station.
Copied from [Weather station memory map](http://www.jim-easterbrook.me.uk/weather/mm/)

The `ws_1080_2080_protocol` sub directory is additional information on the data format including a c-implementation
for reference.

## Dependencies

Installations below valid for raspbian.

* [pyusb](https://github.com/walac/pyusb), install with `pip install pyusb`
* [libusb-1.0.0](http://www.libusb.org/), install with `sudo apt-get install python libusb-1.0.0`
* [pymongo](https://api.mongodb.org/python/current/), install with `pip install pymongo`
* [flask](http://flask.pocoo.org/), install with `pip install flask`
* [gunicorn](http://gunicorn.org/), install with `pip install gunicorn`

To monitor the collector daemon and gunicorn, the python [supervisroctl](http://supervisord.org/) is used.
Examples of commands:

    $ sudo supervisorctl status
    $ sudo supervisorctl reread
    $ sudo supervisorctl update
    $ sudo supervisorctl start ws_collector
    $ sudo supervisorctl start ws_gunicorn

Configuration files for supervisor is available in the py-subdirectory. Softlinks to these files available in
`/etc/supervisor/conf.d`.

To access a simple web interface for supervisord <http://rpi1.local:9001>, add this to `/etc/supervisor/supervisord.conf`

    [inet_http_server]
    port = *:9001

For installation of Mongo to raspian, see
[https://emersonveenstra.net/mongodb-raspberry-pi/](MongoDB). Essentially

    $ git clone https://github.com/svvitale/mongo4pi
    $ cd mongo4pi
    $ sudo sh install.sh

To fix the weather station device name in the `/dev` directory, a udev rule is available in the `rpi` directory.
Refer to the udev documentation, for exmple <https://wiki.archlinux.org/index.php/Udev>

## Testing

    $ python dev.py

Lists attached USB devices and produces a sequences of hex codes that comes from the weather station if everything works

    $ python ws.py

Dumps a weather station record

