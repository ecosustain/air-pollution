from flask import (
    Flask,
    request,
    make_response,
    jsonify,
)

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>MAC 0476<h1/>"

@app.route('/mapa')
def map():
    return "mapa"

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


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=True)