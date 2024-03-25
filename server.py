from flask import Flask, jsonify, request
from etcd3 import client
import types

client = client(host="localhost", port=2379)

app = Flask("demo_server")

@app.route("/put", methods=["POST"])
def put_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        val = data.get("value")

        if key is None or val is None:
            return jsonify({"message": "Key and Value both needs to be provided!"}), 400
        
        if not isinstance(key, str) or not isinstance(val, str):
            return jsonify({"message": "Key and Values to be inserted have to be string type!"}), 400 

        client.put(key, val)
        return jsonify({"message": "Inserted Key-value pairs successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
    
@app.route("/get", methods=["POST"])
def get_key_val():
    try:
        data = request.get_json()
        key = data.get("key")

        if key is None:
            return jsonify({"message": "The key has to be provided!"}), 400
        
        if not isinstance(key, str):
            return jsonify({"message": "Key should be of string type!"}), 400

        val = client.get(key)[0]

        if val is None:
            return jsonify({"message": "The key does not exist in persistent store!"}), 404

        return jsonify({"value": f"{val.decode()}"}), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
    
@app.route("/list", methods=["GET"])
def get_all_vals():
    try:
        data = client.get_all()
        val_arr = []

        for k,_ in data:
            val_arr.append(k.decode())
        
        response = {"values": val_arr}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)