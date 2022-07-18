# Fetch Rewards Coding Exercise
* Interviewer: Jonathan Hoag - jonathan.c.hoag@gmail.com

## Development

### Setup
1. Install Python 3
   * https://www.python.org/downloads/
2. Install pip
   * https://pip.pypa.io/en/stable/installation/
3. Install Python Modules
   * ```shell
     python3 -m pip install -r requirements.txt 
     ```

### Testing
* Start Flask Server
```shell
FLASK_APP=app.app python3 -m flask run --with-threads
```

* Run Primary Test
    * Python
      ```shell
      python3 -m pytest -k 'test_primary'
      ```
    * Curl
      ```shell
      curl -X "DELETE" http://127.0.0.1:5000/points/test_account
      curl -X "POST" http://127.0.0.1:5000/points/test_account/add -H 'Content-Type: application/json' \
          -d '{"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"}'
      curl -X "POST" http://127.0.0.1:5000/points/test_account/add -H 'Content-Type: application/json' \
          -d '{"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"}'
      curl -X "POST" http://127.0.0.1:5000/points/test_account/add -H 'Content-Type: application/json' \
          -d '{"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"}'
      curl -X "POST" http://127.0.0.1:5000/points/test_account/add -H 'Content-Type: application/json' \
          -d '{"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}'
      curl -X "POST" http://127.0.0.1:5000/points/test_account/add -H 'Content-Type: application/json' \
          -d '{"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"}'
      curl -X "POST" http://127.0.0.1:5000/points/test_account/spend -H 'Content-Type: application/json' \
          -d '{"points": 5000}'
      curl http://127.0.0.1:5000/points/test_account
      ```
      ```shell
      {"message":"Account test_account not found.","status_code":404}
      {"payer":"DANNON","points":1000,"timestamp":"'2020-11-02T14:00:00Z"}
      {"payer":"UNILEVER","points":200,"timestamp":"'2020-10-31T11:00:00Z"}
      {"payer":"DANNON","points":-200,"timestamp":"'2020-10-31T15:00:00Z"}
      {"payer":"MILLER COORS","points":10000,"timestamp":"'2020-11-01T14:00:00Z"}
      {"payer":"DANNON","points":300,"timestamp":"'2020-10-31T10:00:00Z"}
      [{"payer":"DANNON","points":-100},{"payer":"UNILEVER","points":-200},{"payer":"MILLER COORS","points":-4700}]
      {"DANNON":1000,"MILLER COORS":5300,"UNILEVER":0}
      ```

* Run All Tests
```shell
python3 -m pytest
```

## Questions and Comments
* What is the intended behavior when an `/add` of negative points causes the payer to go negative temporarily?
  * We can either log an error that is monitored (<-chosen) or throw an error that causes the transaction to fail.
  * It's possible to perform a bulk load of add transactions that include transactions with negative points reducing
    the payer points below zero before doing an add transaction that corrects it, this seems like something that
    we don't want to prohibit without good reason, but is not a recommended pattern.
* What are the Idempotency requirements?
  * Not implemented for POST requests Add/Spend Points
  * GET Requests for POINT values are inherently idempotent 
  * Idempotency for the POST requests be easily addressed with request GUIDs from the client
* Input Validation
  * Provided through Pydantic integration
* Output Encoding
  * Not implemented
* Telemetry
  * No Telemetry was added, but OpenTelemetry would be easy to integrate with the existing code.
* Logging
  * Only basic python logging has been added
  * Production logging configuration should include generated request ids, thread ids, and/or composite trace/span ids 
  * Recommend Filebeat -> Logstash -> Amazon OpenSearch or Elastic
* Container
  * No Docker or other Container though this would simplify development environments significantly.
* Api Specification/Documentation
  * Swagger integration and API Specs that are automatically generated would increase development speed.
