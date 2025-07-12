from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

rule_parsing = Blueprint('rule_parsing', __name__, url_prefix='/api')

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

def validate_form_structure(form_data):
    """
    Validate that form data has the expected structure
    """
    expected_sections = ['value_range', 'regex_template', 'continuity', 'statistical_same', 'statistical_different', 'categories']
    
    for section in expected_sections:
        if section not in form_data:
            print(f"Warning: Missing section '{section}' in form data")
            form_data[section] = {}
    
    return form_data

def process_form_data(form_data):
    """
    Process form data and organize it into value_types structure
    """
    # First validate the structure
    form_data = validate_form_structure(form_data)
    
    value_types = {
        "value_range": {},
        "regex_template": {},
        "continuity": {},
        "statistical_same": {},
        "statistical_different": {},
        "categories": {}
    }
    
    # Process value_range data
    if 'value_range' in form_data:
        value_range = form_data['value_range']
        
        # Age range
        if 'age' in value_range:
            age_data = value_range['age']
            if age_data.get('from') or age_data.get('to'):
                value_types['value_range']['age'] = {
                    "from": age_data.get('from', ''),
                    "to": age_data.get('to', '')
                }
        
        # Balance range
        if 'balance' in value_range:
            balance_data = value_range['balance']
            if balance_data.get('from') or balance_data.get('to'):
                value_types['value_range']['balance'] = {
                    "from": balance_data.get('from', ''),
                    "to": balance_data.get('to', '')
                }
        
        # Transaction amount range
        if 'transaction_amount' in value_range:
            transaction_data = value_range['transaction_amount']
            if transaction_data.get('from') or transaction_data.get('to'):
                value_types['value_range']['transaction_amount'] = {
                    "from": transaction_data.get('from', ''),
                    "to": transaction_data.get('to', '')
                }
        
        # Card expiry range
        if 'card_expiry' in value_range:
            card_expiry_data = value_range['card_expiry']
            if card_expiry_data.get('from') or card_expiry_data.get('to'):
                value_types['value_range']['card_expiry'] = {
                    "from": card_expiry_data.get('from', ''),
                    "to": card_expiry_data.get('to', '')
                }
    
    # Process regex_template data
    if 'regex_template' in form_data:
        regex_data = form_data['regex_template']
        
        # Only include non-empty values
        for key, value in regex_data.items():
            if value and value.strip():
                value_types['regex_template'][key] = value.strip()
    
    # Process continuity data
    if 'continuity' in form_data:
        continuity_data = form_data['continuity']
        
        # Transaction datetime
        if 'transaction_datetime' in continuity_data:
            datetime_data = continuity_data['transaction_datetime']
            if datetime_data.get('start') or datetime_data.get('end'):
                value_types['continuity']['transaction_datetime'] = {
                    "start": datetime_data.get('start', ''),
                    "end": datetime_data.get('end', '')
                }
        
        # Account registration
        if 'account_registration' in continuity_data:
            account_data = continuity_data['account_registration']
            if account_data.get('reg_date') or account_data.get('open_date'):
                value_types['continuity']['account_registration'] = {
                    "reg_date": account_data.get('reg_date', ''),
                    "open_date": account_data.get('open_date', '')
                }
    
    # Process statistical_same data
    if 'statistical_same' in form_data:
        statistical_same_data = form_data['statistical_same']
        
        # Only include True values
        for key, value in statistical_same_data.items():
            if value:
                value_types['statistical_same'][key] = value
    
    # Process statistical_different data
    if 'statistical_different' in form_data:
        statistical_different_data = form_data['statistical_different']
        
        # Only include True values
        for key, value in statistical_different_data.items():
            if value:
                value_types['statistical_different'][key] = value
    
    # Process categories data
    if 'categories' in form_data:
        categories_data = form_data['categories']
        
        # Only include non-empty values
        for key, value in categories_data.items():
            if value and value.strip():
                value_types['categories'][key] = value.strip()
    
    # Print summary of processed data
    print("=== Processed Data Summary ===")
    for section, data in value_types.items():
        if data:  # Only print non-empty sections
            print(f"{section}: {len(data)} items")
            for key, value in data.items():
                print(f"  {key}: {value}")
    print("=============================")
    
    return value_types

@rule_parsing.route('/save-data', methods = ['POST'])
def save_data():
    if not request.is_json:
        return jsonify({"Error": "Request must be JSON"}), 400

    form_data = request.get_json()
    print("Raw data from client:", form_data)

    if not form_data:
        return jsonify({"error": "No data provided"}), 400

    # Process the form data into value_types structure
    processed_data = process_form_data(form_data)
    print("Processed data:", processed_data)

    # Read existing data
    existing_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    existing_data = json.loads(content)
                else:
                    existing_data = []
        except json.JSONDecodeError:
            print(f"Warning: Error format file '{DATA_FILE}', creating new")
            existing_data = []
        except Exception as e:
            print(f"Cannot compile file '{DATA_FILE}': {e}")
            return jsonify({"error": "server cannot read file"}), 500

    # Replace existing data with new processed data
    existing_data = [processed_data]
    
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print(f"Data stored into '{DATA_FILE}'")
        return jsonify({
            "message": "Data is stored successfully",
            "processed_data": processed_data
        }), 200
    except Exception as e:
        print(f"Error when writing file '{DATA_FILE}': {e}")
        return jsonify({"Error": "Server cannot write file"}), 500

@rule_parsing.route('/get-rules', methods=['GET'])
def get_rules():
    """
    Retrieve current rules from data.json
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    data = json.loads(content)
                    return jsonify({
                        "message": "Rules retrieved successfully",
                        "data": data
                    }), 200
                else:
                    return jsonify({
                        "message": "No rules found",
                        "data": []
                    }), 200
        else:
            return jsonify({
                "message": "No rules file found",
                "data": []
            }), 200
    except Exception as e:
        print(f"Error reading rules file: {e}")
        return jsonify({"error": "Server cannot read rules file"}), 500

@rule_parsing.route('/test', methods=['GET'])
def test_endpoint():
    """
    Test endpoint to verify the server is working
    """
    return jsonify({
        "message": "Rule parsing server is working",
        "endpoints": {
            "save_data": "/api/save-data (POST)",
            "get_rules": "/api/get-rules (GET)",
            "test": "/api/test (GET)"
        }
    }), 200