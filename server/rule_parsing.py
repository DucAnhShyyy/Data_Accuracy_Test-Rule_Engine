from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data.json'

@app.route('/api/save-data', methods=['POST'])
def save_data():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    new_data = request.get_json()
    print("Data from client:", new_data)

    if not new_data:
        return jsonify({"error": "No data provided"}), 400

    existing_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding = 'utf-8') as f:
                content = f.read()
                if content:
                    existing_data = json.loads(content)
                else:
                    existing_data = []
        except json.JSONDecodeError:
            print(f"Warning: File '{DATA_FILE}' has a JSON format error, create new")
            existing_data = []
        except Exception as e:
            print(f"Error when reading file '{DATA_FILE}': {e}")
            return jsonify({"error": "server cannot  read file"}), 500

    existing_data = [new_data]

    try:
        with open(DATA_FILE, 'w', encoding  = 'utf-8') as f:
            json.dump(existing_data, f, ensure_ascii = False, indent = 2)
        print(f"Data is stored into {DATA_FILE}")
        return jsonify({"messege": "Storing success!"}), 200
    except Exception as e:
        print(f"Error when writing file '{DATA_FILE}': {e}")
        return jsonify({"error": "server cannot compile data"}), 500

if __name__ == '__main__':
    app.run(debug = True, port = 5000)