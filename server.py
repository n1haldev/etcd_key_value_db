# This is a test
from flask import Flask, jsonify, request, render_template
from etcd3 import client

client = client(host="localhost", port=2379)

app = Flask("demo_server")

@app.route("/", methods=["GET"])
def index():
    #return jsonify({"message": "Welcome to the demo server!"}), 200
    #return app.send_static_file("frontend.html")
    return render_template("frontend.html")
@app.route("/put", methods=["POST"])
def put_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        val = data.get("value")

        if key=="" or val=="":
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

        if key=="":
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
        key_arr = []
        val_arr = []

        for k,v in data:
            key_arr.append(v.key.decode())
            val_arr.append(k.decode())
        
        response = {"keys": key_arr, "values": val_arr}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500

@app.route("/delete", methods=["DELETE"])
def delete_key():
    try:
        data = request.get_json()
        key = data.get("key")

        if key=="":
            return jsonify({"message": "The key has to be provided!"}), 400
        
        if not isinstance(key, str):
            return jsonify({"message": "Key should be of string type!"}), 400

        client.delete(key)
        return jsonify({"message": f"Key '{key}' deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/update", methods=["PUT"])
def update_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        new_value = data.get("value")

        if key=="" or new_value=="":
            return jsonify({"message": "Key and New Value both need to be provided!"}), 400
        
        if not isinstance(key, str) or not isinstance(new_value, str):
            return jsonify({"message": "Key and New Value to be updated have to be of string type!"}), 400 

        existing_value, _ = client.get(key)
        if existing_value is None:
            return jsonify({"message": f"The key '{key}' does not exist in the persistent store!"}), 404

        client.put(key, new_value)
        return jsonify({"message": f"Key '{key}' updated successfully with value '{new_value}'!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
