import json
import logging
import requests

logger = logging.getLogger(__name__)


class TestResource:

    def test_get_points(self, host, port):
        requests.delete(f"http://{host}:{port}/points")
        response = requests.get(f"http://{host}:{port}/points")
        assert response.status_code == 200
        assert response.json() == {'accounts': []}

    def test_get_account_points(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"})
        requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 200
        assert response.json() == {"DANNON": 1000}

    def test_get_account_points_account_doesnt_exist(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")
        assert response.status_code == 404

    def test_add_points(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        assert response.status_code == 200
        assert response.json() == {'payer': 'DANNON', 'points': 1000, 'timestamp': "'2020-11-02T14:00:00Z"}

    def test_spend_points(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"})
        requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        json_data = json.dumps({"points": 1000})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/spend", json=json_data)
        assert response.status_code == 200
        assert response.json() == [{'payer': 'DANNON', 'points': -1000}]

    def test_spend_points_not_enough(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"})
        requests.post(f"http://{host}:{port}/points/{random_account_id}/add", json=json_data)
        json_data = json.dumps({"points": 2000})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/spend", json=json_data)
        assert response.status_code == 400
        assert "did not have enough points to spend 2000" in response.json()["message"]

    def test_spend_points_account_doesnt_exist(self, host, port, random_account_id):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        json_data = json.dumps({"points": 2000})
        response = requests.post(f"http://{host}:{port}/points/{random_account_id}/spend", json=json_data)
        assert response.status_code == 404
        assert 'does not exist' in response.json()["message"]
