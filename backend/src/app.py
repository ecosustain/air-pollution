from flask import (
    Flask,
    request,
    make_response,
    jsonify,
)
from flask_cors import CORS
from controllers import (
    HeatMapController,
    UpdateController,
    LineGraphController
)

import json
from sqlalchemy import create_engine, inspect, Table, MetaData
from sqlalchemy.orm import sessionmaker
# from apscheduler.schedulers.background import BackgroundScheduler
from utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL
from database.create_tables import create_tables
from database.populate_tables import populate_tables
# import atexit


# def scheduled_update():
#    UpdateController().update_data()


# scheduler = BackgroundScheduler()
# scheduler.add_job(scheduled_update, 'cron', hour=3, minute=0)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())


DATABASE_URI = f'mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@db/poluicao'
engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
SESSION = Session()


try:
    measure_indicator = Table('measure_indicator', MetaData(), autoload_with=engine, schema='poluicao')
    row_count = SESSION.query(measure_indicator).count()
    if row_count == 0:
        populate_tables()
except Exception as e:
    print(e)
    create_tables()
    populate_tables()


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return f"<h1>MAC 0476<h1/>"


@app.route('/update_data', methods=['PUT'])
def update_data():
    response = make_response()

    if request.method == 'PUT':
        response = UpdateController().update_data()

        response = jsonify(response)
        response.status = 200

    return response


@app.route('/heatmap/<string:payload>', methods=['GET'])
def heatmap(payload):
    """
    API endpoint to generate heatmaps based on the provided payload.

    Args:
        payload (str): A JSON string containing the request data, which should include:
            - "indicator": The name of the environmental indicator.
            - "interpolator": A dictionary with "method" (interpolation type) and "params" (parameters for the method).
            - "interval": The time interval for the heatmap (e.g., "daily", "monthly").
            - Additional time references based on the interval.

    Returns:
        Response: A JSON response containing the generated heatmaps with HTTP status 200.
    """
    payload = json.loads(payload)
    response = make_response()

    if request.method == 'GET':
        heatmaps = HeatMapController(session=SESSION).get_heatmap(payload=payload)
        SESSION.close()

        response = jsonify(heatmaps)
        response.status = 200

    return response


@app.route('/linegraph/<string:payload>', methods=['GET'])
def linegraph(payload):
    """
    API endpoint to generate line plots based on the provided payload.

    Args:
        payload (str): A JSON string containing the request data, which should include:
            - "indicators": List with the name of each environmental indicator.
            - "interval": The time interval for the lineplot (e.g., "daily", "monthly", "yearly", "hourly").
            - Additional time references based on the interval.

    Returns:
        Response: A JSON response containing the data necessary to plot the lines with HTTP status 200.
    """
    payload = json.loads(payload)
    response = make_response()

    if request.method == 'GET':
        linegraph_ = LineGraphController(session=SESSION).get_line_graph(payload=payload)
        SESSION.close()

        response = jsonify({"line_graph": linegraph_})
        response.status = 200

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
