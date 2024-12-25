# Import the dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta  


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    """List all available routes"""
    return (
        f"Available routes:<br>"
        f"/api/v1.0/precipitation"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Get the most recent date in the database
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    
    # Calculate the date one year prior
    one_yr_prior = recent_date - timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    prcp_scores = session.query(Measurement.date, Measurement.prcp). \
        filter(Measurement.date >= one_yr_prior).order_by(Measurement.date).all()
    
    # Convert the query results to a list of dictionaries
    prcp_list = []
    for date, prcp in prcp_scores:
        prcp_dict = {
            "date": date,
            "prcp": prcp
        }
        prcp_list.append(prcp_dict)
    
    # Return the JSON representation
    return jsonify(prcp_list)


if __name__ == "__main__":
    app.run(debug=True)