import json
import logging
import requests

logger = logging.getLogger(__name__)


class TestResource:

    def test_primary(self, host, port, random_account_id):
        # Remove account if it exists
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        # Add all the transactions
        add = f"http://{host}:{port}/points/{random_account_id}/add"
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"}))
        # Get the points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        logger.info(f'Get Points Response: {response.json()}')
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1100,
            "UNILEVER": 200,
            "MILLER COORS": 10000
        }
        # Spend the points from the account
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 5000}))
        assert response.status_code == 200
        assert response.json() == [
            {"payer": "DANNON", "points": -100},
            {"payer": "UNILEVER", "points": -200},
            {"payer": "MILLER COORS", "points": -4700}
        ]
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1000,
            "UNILEVER": 0,
            "MILLER COORS": 5300
        }

    def test_primary_extended(self, host, port, random_account_id):
        # Remove account if it exists
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        # Add all the transactions
        add = f"http://{host}:{port}/points/{random_account_id}/add"
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}))
        requests.post(add, json=json.dumps({"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"}))
        # Get the points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        logger.info(f'Get Points Response: {response.json()}')
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1100,
            "UNILEVER": 200,
            "MILLER COORS": 10000
        }
        # Spend the points from the account
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 5000}))
        assert response.status_code == 200
        assert response.json() == [
            {"payer": "DANNON", "points": -100},
            {"payer": "UNILEVER", "points": -200},
            {"payer": "MILLER COORS", "points": -4700}
        ]
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1000,
            "UNILEVER": 0,
            "MILLER COORS": 5300
        }
        # Spend the points from the account
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 1000}))
        assert response.status_code == 200
        assert response.json() == [
            {"payer": "MILLER COORS", "points": -1000}
        ]
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1000,
            "UNILEVER": 0,
            "MILLER COORS": 4300
        }
        # Spend the points from the account
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 4300}))
        assert response.status_code == 200
        assert response.json() == [
            {"payer": "MILLER COORS", "points": -4300}
        ]
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1000,
            "UNILEVER": 0,
            "MILLER COORS": 0
        }
        # Attempt Spend more than existing the points from the account
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 1001}))
        assert response.status_code == 400
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 1000,
            "UNILEVER": 0,
            "MILLER COORS": 0
        }
        # Spend all points
        spend = f"http://{host}:{port}/points/{random_account_id}/spend"
        response = requests.post(spend, json=json.dumps({'points': 1000}))
        assert response.status_code == 200
        assert response.json() == [
            {"payer": "DANNON", "points": -1000}
        ]
        # Get points from the account and check they are correct
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {
            "DANNON": 0,
            "UNILEVER": 0,
            "MILLER COORS": 0
        }

