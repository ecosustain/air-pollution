from controllers import HeatMapController, UpdateController
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL


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


@app.route('/heat_map/<string:payload>', methods=['GET'])
def heat_map(payload):
    print(payload)
    payload = json.loads(payload)
    print(payload)
    response = make_response()

    if request.method == 'GET':
        heat_map = HeatMapController(session=SESSION).get_heat_map(payload=payload)
        SESSION.close()

        response = jsonify({"heat_map": heat_map})
        response.status = 200

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)