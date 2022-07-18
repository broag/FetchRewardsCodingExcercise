import json
import logging
import requests

from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

logger = logging.getLogger(__name__)


class TestResource:

    @staticmethod
    def post_requests(url, data, num_messages: int, max_workers: int):
        message_numbers = list(range(0, num_messages))

        def post_request(message_num: int):
            logger.info(f"Posting {url} Number: {message_num}")
            return requests.post(url, json=json.dumps(data))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(post_request, message_numbers))
            return True

    def test_add_transactions(self, host, port, random_account_id, stress_threads, stress_processes, stress_calls):
        requests.delete(f"http://{host}:{port}/points/{random_account_id}")
        pool = ThreadPool(processes=stress_processes)
        points_added_per_call = 100
        add_args = (
            f"http://{host}:{port}/points/{random_account_id}/add",
            {"payer": "MILLER", "points": points_added_per_call, "timestamp": "2020-11-01T14:00:00Z"},
            stress_calls,
            stress_threads
        )
        async_add_responses = pool.apply_async(self.post_requests, add_args)
        async_add_responses.get()

        response = requests.get(f"http://{host}:{port}/points/{random_account_id}")

        expected_points = points_added_per_call * stress_calls
        assert response.json() == {'MILLER': expected_points}
