from os import environ
from joblib import load
from flask import abort, Flask, jsonify, make_response, request
import numpy as np
service_name = environ['SERVICE_NAME']
version = environ['API_VERSION']
trans = load('transformer.joblib')
model = load('model.joblib')
print(f'/{service_name}/v{version}/predict')
app = Flask(__name__)
@app.route(f'/{service_name}/v{version}/predict', methods=['POST'])
# @app.route('/carbon/1/predict', methods=['POST'])
def predict():
    try:
        features_trans = trans.transform(np.array(request.json['prediction']).reshape(1,55))
        prediction = model.predict(features_trans).tolist()
        return make_response(jsonify({'prediction': prediction}))
    except ValueError:
        raise RuntimeError('Features are not in the correct format.')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
