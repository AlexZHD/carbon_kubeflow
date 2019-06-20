"""
api.py
~~~~~~
This module defines a simple REST API for a Machine Learning (ML) model.
"""

from os import environ

from joblib import load
from flask import abort, Flask, jsonify, make_response, request
from pandas import DataFrame
import numpy as np


# service_name = environ['SERVICE_NAME']
# version = environ['API_VERSION']

#lines of additional code are required to modify this service to 
# load a SciKit Learn model from disk and pass new data to it’s 
# ‘predict’ method for generating predictions 
# from notebook
trans = load('transformer.joblib')
model = load('model.joblib')

app = Flask(__name__)


#@app.route(f'/{service_name}/v{version}/predict', methods=['POST'])
@app.route('/carbon/1/predict', methods=['POST'])
def predict():
    """TODO"""
    try:
        
        features_trans = trans.transform(np.array(request.json['prediction']).reshape(1,55))
        prediction = model.predict(features_trans).tolist()
        return make_response(jsonify({'prediction': prediction}))
    except ValueError:
        raise RuntimeError('Features are not in the correct format.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
