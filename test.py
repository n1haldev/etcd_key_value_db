import unittest
import json
from server import app
from etcd3 import client

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"PASS : {test.id()}")
        # print()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"FAIL : {test.id()}")
        # print()

class Test_App(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.client = client(host="localhost", port=2379)

    # def test_index(self):
    #     response = self.app.get("/")
    #     data = json.loads(response.data.decode())
    #     self.assertEqual(data["message"], "Welcome to the demo server!")

    def test_put_correct(self):
        data = {"key": "test_key", "value": "test_val"}
        response = self.app.post("/put", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Inserted Key-value pairs successfully!")

    def test_put_missing(self):
        # Missing Value
        data = {"key": "test_missing", "value": ""}
        response = self.app.post("/put", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and Value both needs to be provided!")
        
        # Missing Key
        data = {"key": "", "value": "test_missing"}
        response = self.app.post("/put", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and Value both needs to be provided!")

    def test_put_typeerror(self):
        data = {"key": 3, "value": 10}
        response = self.app.post("/put", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and Values to be inserted have to be string type!")

    def test_get_correct(self):
        self.client.put("test_key", "test_value")

        data = {"key": "test_key"}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["value"], "test_value")

    def test_get_missing_key(self):
        self.client.put("test_key", "test_value")

        data = {}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "The key has to be provided!")

    def test_get_typeerror(self):
        self.client.put("test_key", "test_value")

        data = {"key": 3}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key should be of string type!")

    def test_get_nonexistent_key(self):
        data = {"key": "non-existent"}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "The key does not exist in persistent store!")
        
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_App)
    unittest.TextTestRunner(resultclass=CustomTestResult, verbosity=2).run(suite)