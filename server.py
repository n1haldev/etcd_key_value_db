# Import necessary modules
from flask import Flask, jsonify, request, render_template
from etcd3 import client

# Initialize the etcd client
client = client(host="localhost", port=2379)

# Create a Flask app
app = Flask("demo_server")

# Route for the main page, returns the frontend HTML template
@app.route("/", methods=["GET"])
def index():
    return render_template("frontend.html")

# Route to insert a key-value pair into etcd
@app.route("/put", methods=["POST"])
def put_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        val = data.get("value")

        # Check if key or value is empty
        if key == "" or val == "":
            return jsonify({"message": "Key and Value both need to be provided!"}), 400
        
        # Check if key and value are strings
        if not isinstance(key, str) or not isinstance(val, str):
            return jsonify({"message": "Key and Values to be inserted have to be string type!"}), 400 

        # Insert key-value pair into etcd
        client.put(key, val)
        return jsonify({"message": "Inserted Key-value pairs successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
    
# Route to get the value for a given key from etcd
@app.route("/get", methods=["POST"])
def get_key_val():
    try:
        data = request.get_json()
        key = data.get("key")

        # Check if key is empty
        if key == "":
            return jsonify({"message": "The key has to be provided!"}), 400
        
        # Check if key is a string
        if not isinstance(key, str):
            return jsonify({"message": "Key should be of string type!"}), 400

        # Get the value for the given key from etcd
        val = client.get(key)[0]

        # Check if the key exists in the persistent store
        if val is None:
            return jsonify({"message": "The key does not exist in persistent store!"}), 404

        return jsonify({"value": f"{val.decode()}"}), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
    
# Route to list all key-value pairs in etcd
@app.route("/list", methods=["GET"])
def get_all_vals():
    try:
        data = client.get_all()
        key_arr = []
        val_arr = []

        # Extract keys and values from etcd response
        for k, v in data:
            key_arr.append(v.key.decode())
            val_arr.append(k.decode())
        
        response = {"keys": key_arr, "values": val_arr}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500

# Route to delete a key from etcd
@app.route("/delete", methods=["DELETE"])
def delete_key():
    try:
        data = request.get_json()
        key = data.get("key")

        # Check if key is empty
        if key == "":
            return jsonify({"message": "The key has to be provided!"}), 400

        # Check if key is a string
        if not isinstance(key, str):
            return jsonify({"message": "Key should be of string type!"}), 400
        
        #Check if key exists in the database
        val = client.get(key)[0]
        if val is None:
            return jsonify({"message": "The key does not exist in persistent store!"}), 404
        
        # Delete the key from etcd
        client.delete(key)
        return jsonify({"message": f"Key '{key}' deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Route to update the value for a given key in etcd
@app.route("/update", methods=["PUT"])
def update_key_val():
    try:
        data = request.get_json()
        key = data.get("key")
        new_value = data.get("value")

        # Check if key or new_value is empty
        if key == "" or new_value == "":
            return jsonify({"message": "Key and New Value both need to be provided!"}), 400
        
        # Check if key and new_value are strings
        if not isinstance(key, str) or not isinstance(new_value, str):
            return jsonify({"message": "Key and New Value to be updated have to be of string type!"}), 400 

        # Check if the key exists in the persistent store
        existing_value, _ = client.get(key)
        if existing_value is None:
            return jsonify({"message": f"The key '{key}' does not exist in the persistent store!"}), 404

        # Update the value for the given key in etcd
        client.put(key, new_value)
        return jsonify({"message": f"Key '{key}' updated successfully with value '{new_value}'!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
