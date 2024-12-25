# sqlalchemy-challenge
You've decided to treat yourself to a long holiday vacation in Honolulu, Hawaii. To help with your trip planning, you decide to do a climate analysis about the area.

## Part 1: Analyze and Explore the Climate Data

In this section, you’ll use Python and SQLAlchemy to do a basic climate analysis and data exploration of your climate database. Specifically, you’ll use SQLAlchemy ORM queries, Pandas, and Matplotlib

#### Precipitation Analysis
- Find the most recent date in the dataset.
- Using that date, get the previous 12 months of precipitation data by querying the previous 12 months of data.
- Select only the "date" and "prcp" values.
- Load the query results into a Pandas DataFrame. Explicitly set the column names.
- Sort the DataFrame values by "date".
- Plot the results by using the DataFrame plot method, as the following image shows
- Use Pandas to print the summary statistics for the precipitation data.

#### Station Analysis
- Design a query to calculate the total number of stations in the dataset
- Design a query to find the most-active stations (that is, the stations that have the most rows). To do so, complete the following steps:
    - List the stations and observation counts in descending order.
    - Which station id has the greatest number of observations?
- Design a query that calculates the lowest, highest, and average temperatures that filters on the most-active station id found in the previous query.
- Design a query to get the previous 12 months of temperature observation (TOBS) data. To do so, complete the following steps:
    - Filter by the station that has the greatest number of observations.
    - Query the previous 12 months of TOBS data for that station.
    - Plot the results as a histogram

## Part 2: Design Your Climate App
Design a Flask API based on the queries that you just developed

#### 1. /

- Start at the homepage.

- List all the available routes.

#### 2. /api/v1.0/precipitation

- Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

- Return the JSON representation of your dictionary.

#### 3./api/v1.0/stations

- Return a JSON list of stations from the dataset.

#### 4. /api/v1.0/tobs

- Query the dates and temperature observations of the most-active station for the previous year of data.

- Return a JSON list of temperature observations for the previous year.

#### 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>

- Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

- For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

- For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

## References
#### chatgpt: Retrieve the last 12 months of precipitation data
recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
one_yr_prior = recent_date - dt.timedelta(days=365)

#### chatgpt: Counting the stations and listing them in descending order
station_counts = (
    session.query(Measurement.station, func.count(Measurement.station).label('count'))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc())
    .all()
)
#### chatGPT: TMIN,TAVG,TMAX based on start and end dates 
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
