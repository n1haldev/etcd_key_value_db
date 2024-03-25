from flask import Flask, jsonify, request
from etcd3 import client

client = client(host="localhost", port=2379)

app = Flask("demo_server")

@app.route("/put", methods=["POST"])
def put_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        val = data.get("value")

        if not isinstance(key, str) or not isinstance(val, str):
            return jsonify({"message": "Key and Values to be inserted have to be string type!"}), 400 

        if key is None or val is None:
            return jsonify({"message": "Key and Value both needs to be provided!"}), 400

        client.put(key, val)
        return jsonify({"message": "Inserted Key-value pairs successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)