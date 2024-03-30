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
        self.client.put("test_key", "test_value")

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
        self.assertEqual(data["message"], "Key and Value both need to be provided!")
        
        # Missing Key
        data = {"key": "", "value": "test_missing"}
        response = self.app.post("/put", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and Value both need to be provided!")

    def test_get_missing_key(self):
        data = {"key": ""}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "The key has to be provided!")

    def test_get_nonexistent_key(self):
        data = {"key": "non-existent"}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "The key does not exist in persistent store!")

    def test_list_all(self):
        data = self.client.get_all()
        key_arr = []
        val_arr = []

        for k,v in data:
            key_arr.append(v.key.decode())
            val_arr.append(k.decode())

        response = self.app.get("/list")
        data = json.loads(response.data.decode())
        resp_keys = data["keys"]
        resp_vals = data["values"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_keys, key_arr)
        self.assertEqual(resp_vals, val_arr)

    def test_delete_missing_key(self):
        self.client.put("test_key", "test_value")

        data = {"key": ""}
        response = self.app.delete("/delete", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "The key has to be provided!")

    def test_delete_nonexistent_key(self):
        data = {"key": "non-existent"}
        response = self.app.delete("/delete", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "The key does not exist in persistent store!")

    def test_update_missing(self):
        # Missing Value
        self.client.put("update_key", "update_value")
        
        data = {"key": "update_key", "value": ""}
        response = self.app.put("/update", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and New Value both need to be provided!")
        
        # Missing Key
        data = {"key": "", "value": "test_missing"}
        response = self.app.put("/update", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Key and New Value both need to be provided!")

    def test_update_nonexistent_key(self):
        self.client.put("update_key", "update_value")
        
        data = {"key": "non-existent", "value": "some_value"}
        response = self.app.put("/update", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "The key 'non-existent' does not exist in the persistent store!")

    def test_get_correct(self):
        data = {"key": "test_key"}
        response = self.app.post("/get", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["value"], "test_value")

    def test_update_correct(self):
        self.client.put("update_key", "update_value")

        data = {"key": "update_key", "value": "yes_update_value"}
        response = self.app.put("/update", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)

        new_val = self.client.get("update_key")[0]
        self.assertEqual(new_val.decode(), "yes_update_value")

    def test_delete_correct(self):
        self.client.put("test_key", "test_value")

        data = {"key": "test_key"}
        response = self.app.delete("/delete", json=data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Key 'test_key' deleted successfully!")
      
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_App)
    unittest.TextTestRunner(resultclass=CustomTestResult, verbosity=2).run(suite)