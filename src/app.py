from flask import (
    Flask,
    request,
    make_response,
    jsonify,
)

from controllers import (
    HeatMapController
)

from models import (
    Indicators,
    Stations,
    StationIndicators,
    MeasureIndicator,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'mysql+pymysql://root:root@localhost/poluicao'
engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
SESSION = Session()

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>MAC 0476<h1/>"

@app.route(rule='/mapa/<map_name>',
           methods=['POST', 'GET'])
def map_name(map_name):
    if request.method == 'POST':
        return f"You tried to post"
    if request.method == 'GET':
        return f"{map_name}"

@app.route('/estacoes/<int:n_stations>')
def stations(n_stations):
    response = make_response(f"{n_stations}")
    response.status_code = 200
    
    return response

@app.route('/handle_params')
def handle_params():
    # use url: /handle_params?name=YourName
    name = request.args.get('name')
    return f"Ola, {name}"

@app.route('/login',
           methods=['GET', 'POST'])
def fake_login():
    if request.method == 'POST':
        response = make_response()
        response = jsonify(teste="444")
        response.status_code = 201

        return response
    
    if request.method == 'GET':
        return f""
    
@app.route('/heat_map')
def heat_map():
    # if request.method == 'GET':
    #     response = make_response()
    #     measure_indicators = HeatMapController(SESSION).get_heat_map(date="") 
    #     response = jsonify(data=measure_indicators)

    session = SESSION
    print("Vo tenta")
    indicators = session.query(MeasureIndicator).limit(5).all()
    print("Passei")
    result = [{"idStation": indicator.idStation, "name": indicator.value} for indicator in indicators]
    session.close()
    return jsonify(result), 200

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=True)