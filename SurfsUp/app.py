# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available routes"""
    return(
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br/>"
    )


# 2.Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def prcp():
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    one_yr_prior = recent_date - dt.timedelta(days=365)
    prcp_scores = session.query(Measurement.date, Measurement.prcp). \
            filter(Measurement.date >= one_yr_prior).order_by(Measurement.date).all()
    # Convert the query results to a list of dictionaries
    prcp_list = []
    for date,prcp in prcp_scores:
        prcp_dict={
            "date": date,
            "prcp": prcp
        }
        prcp_list.append(prcp_dict)
    
    # Return the JSON representation   
    return jsonify(prcp_list)

# 3.Return a list of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    results=session.query(Measurement.station).group_by(Measurement.station).all()
    stations = [station[0] for station in results]
    return jsonify(stations)

# 4. Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def temperatures():
    # Get the most recent date in the dataset
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    one_yr_prior = recent_date - dt.timedelta(days=365)
    # Query the dates and temperature observations for the most-active station
    active_station_results = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.date >= one_yr_prior). \
        filter(Measurement.station == 'USC00519281'). \
        order_by(Measurement.date).all()
    # Create a list of dictionaries to hold the results
    active_station_temp_list = []
    for date, tobs in active_station_results:
        active_station_dict = {
            "date": date,
            "temp": tobs
        }
        active_station_temp_list.append(active_station_dict)
        
    # Return the JSON representation   
    return jsonify(active_station_temp_list)
# 5. Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """
    Return a JSON list of TMIN, TAVG, and TMAX for a given start or start-end range.
    If no end date is provided, the end date is set to the most recent date in the database.
    """
    try:
        # Validate the start date format
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

        # If no end date is provided, use the most recent date in the database
        if not end:
            recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
            end_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
        else:
            # Validate the end date format
            end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

        # Define the query for TMIN, TAVG, and TMAX
        sel = [
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ]

        # Query for the specified date range
        results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

        # Handle empty results
        if not results or results[0][0] is None:
            return jsonify({"error": "No data found for the given date range."}), 404

        # Convert query results to a dictionary
        temp_stats = {
            "Start Date": start_date,
            "End Date": end_date,
            "TMIN": results[0][0],
            "TAVG": results[0][1],
            "TMAX": results[0][2]
        }

        # Return JSON response
        return jsonify(temp_stats)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

        
if __name__ == "__main__":
    app.run(debug=True)