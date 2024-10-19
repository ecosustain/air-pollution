from flask import (
    Flask,
    request,
    make_response,
    jsonify,
)

from controllers import (
    HeatMapController
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.data.utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL

DATABASE_URI = f'mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@localhost/poluicao'
engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
SESSION = Session()

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>MAC 0476<h1/>"
    
@app.route('/heat_map', methods=['GET'])
def heat_map():
    payload = request.get_json()
    response = make_response()

    if request.method == 'GET':
        measure_indicators = HeatMapController(session=SESSION).get_heat_map(payload=payload)
        SESSION.close()
        
        result = [{"idStation": indicator.idStation, "name": indicator.value} for indicator in measure_indicators]
        response = jsonify(result)
        response.status = 200

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=True)