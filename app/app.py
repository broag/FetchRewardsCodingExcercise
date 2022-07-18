import logging

from json import JSONEncoder
from flask import Flask
from flask import request
from flask import jsonify
from pydantic import ValidationError

from app.schema import AddPointsRequest, SpendPointsRequest
from app.model import NotEnoughPointsException, AccountDoesntExistException
from app.service import PointsService


# Simple Dict JSON Encoder
class ObjectDictJSONEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
app.json_encoder = ObjectDictJSONEncoder
points_service = PointsService()


# Request/Response Access and Logging
@app.before_request
def before_request():
    logger.info(f'REQUEST: {request.remote_addr} - "{request.method} {request.full_path} {request.scheme}"')


@app.after_request
def after_request(resp):
    logger.info(f'RESPONSE: {request.remote_addr} - "{request.method} {request.full_path} {request.scheme}" '
                f'{resp.status_code} ')
    return resp


# Exception Handling
@app.errorhandler(Exception)
def handle_unexpected_exception(exception):
    logger.error(f"Exception on {request.full_path} [{request.method}] with {exception}", exc_info=True)
    status_code = 500
    response = {"error": f"Unexpected Exception: {repr(exception)}", "status_code": status_code}
    return jsonify(response), status_code


# Application Routes
@app.route('/points', methods=['GET'])
def get_points():
    accounts = []
    for account_id in points_service.get_account_ids():
        points_balances = points_service.get_points_balances(account_id)
        account = {"account_id": account_id, "points": points_balances}
        accounts.append(account)
    response = {"accounts": accounts}
    return jsonify(response), 200


@app.route('/points/<account_id>', methods=['GET'])
def get_points_for_account(account_id: str):
    if points_service.get_account(account_id) is not None:
        response = points_service.get_points_balances(account_id)
        status_code = 200
    else:
        status_code = 404
        response = {"message": f"Account {account_id} not found.", "status_code": status_code}
    return jsonify(response), status_code


@app.route('/points/<account_id>/add', methods=['POST'])
def add_points(account_id: str):
    try:
        add_points_request = AddPointsRequest.from_dict_or_json(request.json)
        logger.debug(f"Add Points Request for '{account_id}': {add_points_request}")
        if add_points_request.points == 0:
            status_code = 400
            response = {
                "message": f"Cannot add a transaction with zero points for account {account_id}: {add_points_request}",
                "status_code": status_code
            }
        else:
            transaction = points_service.add_transaction(account_id,
                                                         add_points_request.payer,
                                                         add_points_request.points,
                                                         add_points_request.timestamp)
            status_code = 200
            response_timestamp = transaction.timestamp.strftime("'%Y-%m-%dT%H:%M:%SZ")
            response = {"payer": transaction.payer, "points": transaction.points, "timestamp": response_timestamp}
    except ValidationError:
        logger.warning(f"Request Validation Error for {AddPointsRequest.__name__}", exc_info=True)
        status_code = 400
        response = {"message": f"Bad Request", "status_code": status_code}
    return jsonify(response), status_code


@app.route('/points/<account_id>/spend', methods=['POST'])
def spend_points(account_id: str):
    points = 0
    try:
        spend_points_request = SpendPointsRequest.from_dict_or_json(request.json)
        logger.debug(f"Spend Points Request for '{account_id}': {spend_points_request}")
        points = spend_points_request.points
        spend_transactions = points_service.spend_points(account_id, points)
        status_code = 200
        response = []
        for spend_transaction in spend_transactions:
            response.append({"payer": spend_transaction.payer, "points": spend_transaction.points})
    except NotEnoughPointsException:
        error_message = f"Account {account_id} did not have enough points to spend {points}."
        logger.error(error_message)
        status_code = 400
        response = {"message": error_message, "status_code": status_code}
    except AccountDoesntExistException:
        error_message = f"Account {account_id} that does not exist. Cannot spend against it."
        logger.error(error_message)
        status_code = 404
        response = {"message": error_message, "status_code": status_code}
    except ValidationError:
        logger.warning(f"Request Validation Error for {SpendPointsRequest.__name__}", exc_info=True)
        status_code = 400
        response = {"message": f"Bad Request", "status_code": status_code}
    return jsonify(response), status_code


# Application Testing Routes
# TODO: The path to these could be changed to be blocked in easily in production,
#  though it is not the only way to accomplish it.
@app.route('/points/<account_id>', methods=['DELETE'])
def remove_account(account_id: str):
    if points_service.get_account(account_id) is not None:
        points_service.remove_account(account_id)
        response = {}
        status_code = 204
    else:
        status_code = 404
        response = {"message": f"Account {account_id} not found.", "status_code": status_code}
    return jsonify(response), status_code


@app.route('/points', methods=['DELETE'])
def remove_accounts():
    accounts_removed = []
    for account_id in points_service.get_account_ids():
        accounts_removed.append(account_id)
        points_service.remove_account(account_id)
    response = {"accounts_removed": accounts_removed}
    return jsonify(response), 200


if __name__ == '__main__':
    app.run()
