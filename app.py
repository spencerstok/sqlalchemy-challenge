import sqlalchemy
import numpy as np
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func, inspect



#Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
# reflect database into a new model
Base = automap_base()
# reflect tables
Base.prepare(engine, reflect=True)

# Save ref to table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Available api routes"""
    return"""<html>
    <h1>Available Honolulu - API routes</h1>
    <ul>
    <br>
    <li>
        List of precipitations from last year:
        <br>
        <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
        JSON list of stations: 
        <br>
       <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
        JSON list of Temperature Observations for previous year:
        <br>
        <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
        Return a JSON list (tmin, tmax, tavg) for the dates newer than provided date:
        <br>
        <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a>
    </li>
    <br>
    <li>
        Return a JSON list (tmin, tmax, tavg) from start date to end date:
        <br>
        <a href="/api/v1.0/2017-01-01/2017-01-07">/api/v1.0/2017-01-01/2017-01-07</a>
    </li>
    <br>
    </ul>
    </html>
    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Docstring 
    """List of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    # Docstring
    """JSON list of stations"""
    # Query stations
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    # Docstring
    """JSON list of Temperature Observations for previous year"""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    tobs_list = dict(results_tobs)

    return jsonify(tobs_list)



def calc_start_temps(start_date):
    """Return a JSON list (tmin, tmax, tavg) for the dates newer than provided date"""
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

@app.route("/api/v1.0/<start>")
    
def start_date(start):
    calc_start_temp = calc_start_temps(start)
    t_temp= list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'Min temperature': t_min, 'Max temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dict)

def calc_temps(start_date, end_date):
    """Return a JSON list (tmin, tmax, tavg) from start date to end date"""
    return session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    temp_dict = { 'Min temperature': tmin, 'Max temperature': tmax, 'Avg temperature': temp_avg}

    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)

