/**
 * Created by mm on 16/01/16.
 */

function Plotter() {
    Highcharts.setOptions({global: {useUTC: false}});

    this.tempOut = function (averages, ranges) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphTempOutHourly
            },
            title: {
                text: 'Outside temperature'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                labels: {
                    format: '{value} C'
                },
                title: {
                    text: 'Outside temperature'
                }
            }],
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' C'
            },
            legend: {},
            series: [{
                name: 'Outside temperature',
                data: averages,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }, {
                name: 'Range',
                data: ranges,
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[1],
                fillOpacity: 0.3,
                zIndex: 0
            }]
        });
    };

    this.tempIn = function (averages, ranges) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphTempInHourly
            },
            title: {
                text: 'Inside temperature'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                labels: {
                    format: '{value} C'
                },
                title: {
                    text: 'Inside temperature'
                }
            }],
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' C'
            },
            legend: {},
            series: [{
                name: 'Inside temperature',
                data: averages,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }, {
                name: 'Range',
                data: ranges,
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[1],
                fillOpacity: 0.3,
                zIndex: 0
            }]
        });
    };

    this.rain = function (rain, rain_acc) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphRainHourly
            },
            xAxis: {
                type: 'datetime'
            },
            labels: {
                format: '{value} mm',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: 'Rain',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' mm'
            },
            series: [{
                name: 'Rain',
                data: rain,
                type: 'spline',
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[0]
                }}, {
                name: 'Accumulated',
                data: rain_acc,
                type: 'spline',
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }]
        });
    };

    this.abs_pressure = function (averages, ranges) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphAbsPresHourly
            },
            title: {
                text: 'Abs pressure'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                labels: {
                    format: '{value} hPa'
                },
                title: {
                    text: 'Abs pressure'
                }
            }],
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' hPa'
            },
            legend: {},
            series: [{
                name: 'Abs pressure',
                data: averages,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }, {
                name: 'Range',
                data: ranges,
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[1],
                fillOpacity: 0.3,
                zIndex: 0
            }]
        });
    };

    this.humidity = function (out_hum, in_hum) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphHumidityHourly
            },
            title: {
                text: 'Humidity'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                labels: {
                    format: '{value} %'
                },
                title: {
                    text: 'Humidity'
                }
            }],
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' %'
            },
            legend: {},
            series: [{
                name: 'Outdoor humidity',
                data: out_hum,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }, {
                name: 'Indoor humidity',
                data: in_hum,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }]
        });
    };

    this.wind_speed = function (ave_speed, gust_speed) {
        new Highcharts.Chart({
            chart: {
                renderTo: graphWindSpeedHourly
            },
            title: {
                text: 'Wind speed'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                labels: {
                    format: '{value} m/s'
                },
                title: {
                    text: 'Wind speed'
                }
            }],
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' m/s'
            },
            legend: {},
            series: [{
                name: 'Average wind speed',
                data: ave_speed,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }, {
                name: 'Gust wind speed',
                data: gust_speed,
                zIndex: 1,
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                }
            }]
        });
    };

    this.wind_dir = function (wind_data) {
        var categories = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        var wind_05 = [];
        var wind_05_2 = [];
        var wind_2_4 = [];
        var wind_4_6 = [];
        var wind_6_8 = [];
        var wind_8_10 = [];
        var wind_10 = [];
        var i;
        var ind;

        for (i = 0; i < categories.length; i++) {
            wind_05.push([categories[i], 0.0]);
            wind_05_2.push([categories[i], 0.0]);
            wind_2_4.push([categories[i], 0.0]);
            wind_4_6.push([categories[i], 0.0]);
            wind_6_8.push([categories[i], 0.0]);
            wind_8_10.push([categories[i], 0.0]);
            wind_10.push([categories[i], 0.0]);
        }

        for (i = 0; i < wind_data.length; i++) {
           ind = Math.floor(wind_data[i][0] / 22.5) % 16;

            if (wind_data[i][1] < 0.5) {
                wind_05[ind][1]++;
            }
            else if (wind_data[i][1] <= 2) {
                wind_05_2[ind][1]++;
            }
            else if (wind_data[i][1] <= 4) {
                wind_2_4[ind][1]++;
            }
            else if (wind_data[i][1] <= 6) {
                wind_4_6[ind][1]++;
            }
            else if (wind_data[i][1] <= 8) {
                wind_6_8[ind][1]++;
            }
            else if (wind_data[i][1] <= 10) {
                wind_8_10[ind][1]++;
            }
            else {
                wind_10[ind][1]++;
            }
        }

        for (i = 0; i < categories.length; i++) {
            wind_05[i][1] = Math.round(wind_05[i][1] / wind_data.length * 100 * 10) / 10;
            wind_05_2[i][1] = Math.round(wind_05_2[i][1] / wind_data.length * 100 * 10) / 10;
            wind_2_4[i][1] = Math.round(wind_2_4[i][1] / wind_data.length * 100 * 10) / 10;
            wind_4_6[i][1] = Math.round(wind_4_6[i][1] / wind_data.length * 100 * 10) / 10;
            wind_6_8[i][1] = Math.round(wind_6_8[i][1] / wind_data.length * 100 * 10) / 10;
            wind_8_10[i][1] = Math.round(wind_8_10[i][1] / wind_data.length * 100 * 10) / 10;
            wind_10[i][1] = Math.round(wind_10[i][1] / wind_data.length * 100 * 10) / 10;
        }

        new Highcharts.Chart({
            chart: {
                renderTo: graphWindDirHourly,
                polar: true,
                type: 'column'
            },
            title: {
                text: 'Wind direction'
            },
            xAxis: {
                labels: {
                    formatter: function () {
                        return categories[this.value]; // return text for label
                    }
                },
                crosshair: true,
                tickmarkPlacement: 'on'
            },
            yAxis: {
                min: 0,
                endOnTick: false,
                showLastLabel: true,
                title: {
                    text: 'Frequency (%)'
                },
                labels: {
                    formatter: function () {
                        return this.value + '%';
                    }
                },
                reversedStacks: false
            },
            tooltip: {
                valueSuffix: '%',
                followPointer: true
            },
            plotOptions: {
                series: {
                    stacking: 'normal',
                    shadow: false,
                    groupPadding: 0,
                    pointPlacement: 'on'
                }
            },
            legend: {
                reversed: true,
                align: 'right',
                verticalAlign: 'top',
                y: 100,
                layout: 'vertical'
            },
            series: [{
                name: '&lt; 0.5 m/s',
                data: wind_05,
                _colorindex: 0
            }, {
                name: '0.5 - 2 m/s',
                data: wind_05_2,
                _colorindex: 1
            }, {
                name: '2 - 4 m/s',
                data: wind_2_4,
                _colorindex: 2
            }, {
                name: '4 - 6 m/s',
                data: wind_4_6,
                _colorindex: 3
            }, {
                name: '6 - 8 m/s',
                data: wind_6_8,
                _colorindex: 4
            }, {
                name: '8 - 10 m/s',
                data: wind_8_10,
                _colorindex: 5
            }, {
                name: '&gt; 10 m/s',
                data: wind_10,
                _colorindex: 6
            }]
        });
    };
}