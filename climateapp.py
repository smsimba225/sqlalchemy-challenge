import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Create the connection engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# Use SQLAlchemy `automap_base()` to reflect your tables into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save a reference to those classes called `Station` and `Measurement`
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create a session for the engine to manipulate data
session = Session(engine)

# Set up flask app
app = Flask(__name__)

@app.route("/")
def welcome():
    return "<center>*********************************************<br/>\
        <b><h1><p>Surf the Weather Routes of Hawaii</p></b></h1><br/>\
            <h3>Here you can check out the precipitation and weather \
                information in Hawaii before your next trip!</h3></br>\
            <h3>Copy and Paste the routes into the end of the URL or click the link!</h3>\
            <b>All Weather Stations</b> | /api/v1.0/stations <a href='http://127.0.0.1:5000/api/v1.0/stations'>click</a><br/>\
            <b>Precipitation for the last year</b> | /api/v1.0/precipitation <a href='http://127.0.0.1:5000/api/v1.0/precipitation'>click</a><br/>\
            <b>Temp Observations for the most active station for the last year </b>| /api/v1.0/tobs <a href='http://127.0.0.1:5000/api/v1.0/tobs'>click</a><br/><br/>\
            ----------------------------------------------------------------------<br/><br/>\
            <b>Search for your desired date ranges!  Allowable dates between : 2010-01-01 and 2017-08-23</b><br/><br/>\
            <b>Temp Info (starting from desired date) </b>| /api/v1.0/YYYY-MM-DD <-- please change YYYY-MM-DD into the date you would like! <br/>\
	        </br><b>Example:</b> http://127.0.0.1:5000/api/v1.0/2016-03-15   <a href='http://127.0.0.1:5000/api/v1.0/2016-03-15'>click</a><br/><br/>\
            <b>Temp Info (from desired start date and end date) </b>| /api/v1.0/YYYY-MM-DD/YYYY-MM-DD <-- please change YYYY-MM-DD into the date range you would like!<br/><br/>\
            <b>Example: </b>http://127.0.0.1:5000/api/v1.0/2016-03-15/2017-04-15   <a href='http://127.0.0.1:5000/api/v1.0/2016-03-15/2017-04-15'>click</a><br/><br/><br/>\
                *********************************************</center>"

# Flask route for Precipitation
@app.route("/api/v1.0/precipitation")

def precipitation():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    current_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    last_year = current_date - dt.timedelta(days=366)
    precip_query = session.query(Measurement.station,Measurement.date, Measurement.prcp).\
							filter(Measurement.date > last_year).order_by(Measurement.date)
    precip_data = []
    for prcp in precip_query:
        precip_dict = {}
        precip_dict["Station"] = prcp.station
        precip_dict[prcp.date] = prcp.prcp
        precip_data.append(precip_dict)
	
# Return the json representation of your dictionary
    return jsonify(precip_data)

# Flask route for stations.
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.station, Station.name).all()

    all_stations = []
    for station in stations_query:
        station_dict = {}
        station_dict['Station'] = station.station
        station_dict['Station Name'] = station.name
        all_stations.append(station_dict)
    return jsonify(all_stations)

# Flask route for TOBS
@app.route("/api/v1.0/tobs")
def tobs():
    active_stations = session.query(Measurement.station, func.count(Measurement.date)).\
    group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).all()
    recent_date = session.query(Measurement.date).filter(Measurement.station == active_stations[0][0]).order_by(Measurement.date.desc()).first()
    current_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    last_year = current_date - dt.timedelta(days=366)
    tobs_query = session.query(Measurement.station,Measurement.date, Measurement.tobs).\
							filter(Measurement.date > last_year, Measurement.station == active_stations[0][0]).order_by(Measurement.date)
    tobs_data = []
    for tobs in tobs_query:
        tobs_dict = {}
        tobs_dict['Station'] = tobs.station
        tobs_dict['Date'] = tobs.date
        tobs_dict['Temperature Observed'] = tobs.tobs
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)

# Flask route for min, max, and avg temps
@app.route("/api/v1.0/<start>")
def daily_temp(start):
    temp_calc_query = session.query(Measurement.tobs).filter(Measurement.date >= start)
    temps = [temp[0] for temp in temp_calc_query]
    
    temp_data = {
        "TMIN": min(temps),
        "TMAX": max(temps),
        "TAVG": round(sum(temps) / len(temps), 2)
    }
    
    return jsonify(temp_data)



# Flask route for date range for min, max, and avg temps
@app.route("/api/v1.0/<start>/<end>")
def daily_temp_range(start,end):
    range_calc_query = session.query(Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end)
    temps1 = [temp[0] for temp in range_calc_query]
    
    temp_data1 = {
        "TMIN": min(temps1),
        "TMAX": max(temps1),
        "TAVG": round(sum(temps1) / len(temps1), 2)
    }
    
    return jsonify(temp_data1)
    
if __name__ == "__main__":
    app.run(debug=True)