from flask import (
    Flask,
    request,
    make_response,
    jsonify,
)
from flask_cors import CORS  # Import flask_cors
from controllers import (
    HeatMapController,
    UpdateController,
    LineGraphController
)

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL
import atexit


def scheduled_update():
    UpdateController().update_data()


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_update, 'cron', hour=3, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


DATABASE_URI = f'mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@localhost/poluicao'
engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
SESSION = Session() 

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return "<h1>MAC 0476<h1/>"


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
    print(payload)
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
