from chalice import Chalice, BadRequestError, Response


app = Chalice(app_name='hello-world')

_CITIES_TO_STATE = {
    'Fortaleza': 'Ceará',
    'São Paulo': 'São Paulo',
    'Rio de Janeiro': 'Rio de Janeiro',
    'Salvador': 'Bahia',
    'Belo Horizonte': 'Minas Gerais',
    'Curitiba': 'Paraná',
    'Porto Alegre': 'Rio Grande do Sul',
    'Recife': 'Pernambuco',
    'Manaus': 'Amazonas',
    'Brasília': 'Distrito Federal'
}

#region Multi-CORS setup ------------------------------------------------------
_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://myproductiondomain.com',
]

def custom_cors_headers(current_request) -> dict:
    """ 
    Custom CORS headers function to allow multiple origins.
    This function checks the 'Origin' header of the incoming request
    and sets the 'Access-Control-Allow-Origin' header accordingly if
    the origin is in the allowed list.
    Use:
    @app.route('/your-endpoint', methods=[..., 'OPTIONS'])
    def your_endpoint():
        ...
        multicors_headers = custom_cors_headers(app.current_request)
        if multicors_headers:
            return Response(headers=multicors_headers)
        ...
    """
    if current_request.method != 'OPTIONS': return {}

    headers = {
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '3600',
    }

    origin = current_request.headers.get('origin')
    if origin in _ALLOWED_ORIGINS:
        headers['Access-Control-Allow-Origin'] = origin

    return headers
#endregion Multi-CORS setup ---------------------------------------------------

@app.route('/')
def index():
    return Response(body="""Routes:
                    "/" (GET)
                    "/state/{city}" (GET) - Get state by city
                    "/city/{city}/{state}" (POST, PUT) - Add city with state
                    """,
                    status_code=200,
                    headers={'Content-Type': 'text/plain'}
    )

@app.route('/state/{city}')
def get_state(city):
    try: 
        return {'state': _CITIES_TO_STATE[city]}
    except KeyError:
        raise BadRequestError('City not found - Valid cities are: ' 
                              + ', '.join(_CITIES_TO_STATE.keys()))
    
@app.route('/city/{city}/{state}', methods=['POST', 'PUT'])
def add_city(city, state):
    _CITIES_TO_STATE[city] = state
    return {'message': f'City {city} added with state {state}.'}

@app.route('/help')
def help():
    return {
        "routes": [
            {"path": "/", "method": "GET"},
            {"path": "/state/{city}", "method": "GET"},
            {"path": "/city/{city}/{state}", "method": "POST"},
            {"path": "/city/{city}/{state}", "method": "PUT"},
        ]
    }

@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()

# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
