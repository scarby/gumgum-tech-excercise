import os

from flask import Flask, jsonify, request
from redis import Redis
from redis import ConnectionError

REDIS_URL=os.getenv("REDIS_URL")
app = Flask(__name__)
redis = Redis.from_url(REDIS_URL)
app.logger.debug(REDIS_URL)

##################
### Error handling
##################
class ApiException(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
@app.errorhandler(ApiException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
################
### Api endpoint
################
@app.route('/')
def health():
    try:
        redis_status = redis.ping()
        status = "up"
    except ConnectionError as e:
        redis_status = str(e)
        status = "down"
    return jsonify(status=status, redis=redis_status)
@app.route('/get/<key>')
def get(key):
    val = redis.get(key)
    if val is not None:
        val = val.decode('utf-8')
        app.logger.debug(val)
        return jsonify(value=val)
    else:
        raise ApiException(
            message="Could not find key '{}' in cache".format(key),
            status_code=404)
@app.route('/set/<key>', methods=['POST'])
def set(key):
    try:
        payload = request.get_json(force=True)
        if 'value' in payload:
            redis.set(key, payload['value'])
            app.logger.debug(payload['value'])
            return jsonify(code=200)
        else:
            raise ApiException("'value' key not found in JSON payload")
    except ApiException as e:
        raise e
    except Exception as e:
        raise ApiException(str(e))
########
### Main
########
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("SERVER_PORT", 5000))