# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from flask import Flask, render_template
from flask_cors import CORS

from .v1_routes import rest_api, blueprint,api_blueprint


app = Flask(__name__)

app.register_blueprint(api_blueprint)  # Backend API with '/api/v1' prefix

app.register_blueprint(blueprint)



CORS(app)

# app.config['CACHE_TYPE'] = 'simple'
# app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# cache = Cache(app)

# STATIC_CACHE_TIMEOUT = 3600

# @app.route('/static/react/js/<path:path>')
# @cache.cached(timeout=STATIC_CACHE_TIMEOUT)
# def static_js(path):
#     print("SENDING RSTATIC FILESSSSS", path)
#     return app.send_static_file(f'react/js/{path}')

@app.route('/')
def index():
    return render_template('index.html')



@app.after_request
def after_request(response):
    """
       Sends back a custom error with {"success", "msg"} format
    """
    if int(response.status_code) >= 400:
        if response.mimetype == 'application/json':
            response_data = json.loads(response.get_data())
            if "errors" in response_data:
                response_data = {"success": False,
                                "msg": list(response_data["errors"].items())[0][1]}
                response.set_data(json.dumps(response_data))
            response.headers.add('Content-Type', 'application/json')
        
    return response
