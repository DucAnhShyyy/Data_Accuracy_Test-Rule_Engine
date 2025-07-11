from flask import Blueprint, request, jsonify
import json
import os

rule_parsing = Blueprint('rule_parsing', __name__, url_prefix='/api')

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

@rule_parsing.route('/save-data', methods = ['POST'])
def save_data():
    if not request.is_json:
        return jsonify({"Error": "Request must be JSON"}), 400

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
            print(f"Warning: Error format file '{DATA_FILE}', creat new")
            existing_data = []
        except Exception as e:
            print(f"Cannot compile file '{DATA_FILE}': {e}")
            return jsonify({"error": "server cannot read file"}), 500

    existing_data = [new_data]
    
    try:
        with open(DATA_FILE, 'w', encoding = 'utf-8') as f:
            json.dump(existing_data, f, ensure_ascii = False, indent = 2)
        print(f"Data is storing into '{DATA_FILE}")
        return jsonify({"message": "Data is stored"}), 200
    except Exception as e:
        print(f"Error when writing file '{DATA_FILE}: {e}")
        return jsonify({"Error": "Server cannot write file"}), 500