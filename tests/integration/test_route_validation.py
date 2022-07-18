import json
import logging
import requests

logger = logging.getLogger(__name__)


class TestResource:

    def test_add_points_date_validation_error(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z0"})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        assert response.status_code == 400

    def test_add_points_payer_validation_error(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": {}, "points": 1000, "timestamp": "2020-11-02T14:00:00Z"})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        assert response.status_code == 400

    def test_add_points_points_validation_error(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": "DANNON", "timestamp": "2020-11-02T14:00:00Z"})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        assert response.status_code == 400

    def test_spend_points_points_validation_error(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"points": "f1000"})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/spend", json=json_data)
        assert response.status_code == 400


