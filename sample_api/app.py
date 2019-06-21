#####################
# works
#####################
import datetime
import os

from flask import Flask, jsonify, make_response, request

# from models import Items
# from database import db_session

app = Flask(__name__)

@app.route('/', methods=['POST'])
def score():
    features = request.json['Check']
    # item = Items(name=features, status="", date_added=datetime.datetime.now())
    # db_session.add(item)
    # db_session.commit()
    return make_response(jsonify({'checkxml': features}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)