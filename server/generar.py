from flask import Blueprint, jsonify
import json
import os
import re
from datetime import datetime

generar_bp = Blueprint('generar', __name__, url_prefix='/sql')

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
SQL_SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_script.json')

def load_rules_data():
    """
    Load rules data from data.json
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    return json.loads(content)
        return []
    except Exception as e:
        print(f"Error loading rules data: {e}")
        return []

def generate_value_range_sql(column_name, from_value, to_value):
    """
    Generate SQL for value range validation
    Format: SELECT CASE WHEN {column} BETWEEN {from} AND {to} THEN 'PASS' ELSE 'FAIL' END
    """
    if not from_value and not to_value:
        return None
    
    sql_parts = []
    
    if from_value and to_value:
        sql_parts.append(f"{column_name} BETWEEN {from_value} AND {to_value}")
    elif from_value:
        sql_parts.append(f"{column_name} >= {from_value}")
    elif to_value:
        sql_parts.append(f"{column_name} <= {to_value}")
    
    if sql_parts:
        return f"SELECT CASE WHEN {' AND '.join(sql_parts)} THEN 'PASS' ELSE 'FAIL' END AS validation_result"
    
    return None

def generate_regex_sql(column_name, regex_pattern):
    """
    Generate SQL for regex/template validation
    Format: SELECT CASE WHEN {column} ~ '{regex}' THEN 'PASS' ELSE 'FAIL' END
    """
    if not regex_pattern:
        return None
    
    # Escape single quotes in regex pattern
    escaped_regex = regex_pattern.replace("'", "''")
    
    return f"SELECT CASE WHEN {column_name} ~ '{escaped_regex}' THEN 'PASS' ELSE 'FAIL' END AS validation_result"

def generate_continuity_sql(column_name, start_value=None, end_value=None):
    """
    Generate SQL for continuity validation
    Format: SELECT CASE WHEN LAG({column}) OVER (ORDER BY {column}) = {column}-1 THEN 'PASS' ELSE 'FAIL' END
    """
    if not column_name:
        return None
    
    # For date/time continuity
    if start_value and end_value:
        return f"""
        SELECT CASE 
            WHEN {column_name} BETWEEN '{start_value}' AND '{end_value}' 
            AND LAG({column_name}) OVER (ORDER BY {column_name}) IS NOT NULL
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS validation_result
        """
    else:
        # For general continuity check
        return f"""
        SELECT CASE 
            WHEN LAG({column_name}) OVER (ORDER BY {column_name}) = {column_name} - 1 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS validation_result
        """

def generate_statistical_same_sql(column_name, check_type):
    """
    Generate SQL for statistical same validation (duplicate checks)
    """
    if not column_name:
        return None
    
    return f"""
    SELECT CASE 
        WHEN COUNT(*) OVER (PARTITION BY {column_name}) > 1 
        THEN 'FAIL' 
        ELSE 'PASS' 
    END AS validation_result
    """

def generate_statistical_different_sql(column1, column2, comparison_type):
    """
    Generate SQL for statistical different validation
    """
    if not column1 or not column2:
        return None
    
    if comparison_type == "compare_balance_transaction":
        return f"""
        SELECT CASE 
            WHEN {column1} != {column2} 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS validation_result
        """
    elif comparison_type == "compare_age_account_type":
        return f"""
        SELECT CASE 
            WHEN {column1} IS NOT NULL AND {column2} IS NOT NULL 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS validation_result
        """
    else:
        return f"""
        SELECT CASE 
            WHEN {column1} != {column2} 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS validation_result
        """

def generate_category_sql(column_name, expected_value):
    """
    Generate SQL for category validation
    """
    if not expected_value:
        return None
    
    # Escape single quotes in expected value
    escaped_value = expected_value.replace("'", "''")
    
    return f"SELECT CASE WHEN {column_name} = '{escaped_value}' THEN 'PASS' ELSE 'FAIL' END AS validation_result"

def map_column_names(rule_type, field_name):
    """
    Map field names to actual database column names
    """
    column_mapping = {
        # Value Range mappings
        'age': 'customer_age',
        'balance': 'account_balance',
        'transaction_amount': 'transaction_amount',
        'card_expiry': 'card_expiry_date',
        
        # Regex/Template mappings
        'phone': 'phone_number',
        'email': 'email_address',
        'ssn_format': 'ssn',
        'card_number_format': 'card_number',
        'account_number_format': 'account_number',
        'transaction_id_format': 'transaction_id',
        
        # Continuity mappings
        'transaction_datetime': 'transaction_datetime',
        'account_registration': 'account_registration_date',
        
        # Category mappings
        'account_type': 'account_type',
        'account_status': 'account_status',
        'card_type': 'card_type',
        'card_status': 'card_status',
        'transaction_type': 'transaction_type',
        'transaction_status': 'transaction_status',
        'gender': 'gender'
    }
    
    return column_mapping.get(field_name, field_name)

@generar_bp.route('/generate', methods=['GET'])
def generate_sql():
    """
    Sinh SQL scripts từ rules data và lưu vào sql_script.json (dạng JSON)
    """
    try:
        rules_data = load_rules_data()
        if not rules_data:
            return jsonify({"message": "Không có dữ liệu rules để sinh SQL"}), 404
        sql_scripts = []
        for rule_set in rules_data:
            rule_scripts = {
                "rule_set_id": len(sql_scripts) + 1,
                "value_range_scripts": [],
                "regex_template_scripts": [],
                "continuity_scripts": [],
                "statistical_same_scripts": [],
                "statistical_different_scripts": [],
                "category_scripts": []
            }
            # Generate Value Range SQL scripts
            if 'value_range' in rule_set:
                for field_name, range_data in rule_set['value_range'].items():
                    if range_data.get('from') or range_data.get('to'):
                        column_name = map_column_names('value_range', field_name)
                        sql = generate_value_range_sql(
                            column_name, 
                            range_data.get('from'), 
                            range_data.get('to')
                        )
                        if sql:
                            rule_scripts['value_range_scripts'].append({
                                'field': field_name,
                                'column': column_name,
                                'sql': sql
                            })
            # Generate Regex/Template SQL scripts
            if 'regex_template' in rule_set:
                for field_name, pattern in rule_set['regex_template'].items():
                    if pattern:
                        column_name = map_column_names('regex_template', field_name)
                        sql = generate_regex_sql(column_name, pattern)
                        if sql:
                            rule_scripts['regex_template_scripts'].append({
                                'field': field_name,
                                'column': column_name,
                                'pattern': pattern,
                                'sql': sql
                            })
            # Generate Continuity SQL scripts
            if 'continuity' in rule_set:
                for field_name, continuity_data in rule_set['continuity'].items():
                    if continuity_data:
                        column_name = map_column_names('continuity', field_name)
                        sql = generate_continuity_sql(
                            column_name,
                            continuity_data.get('start'),
                            continuity_data.get('end')
                        )
                        if sql:
                            rule_scripts['continuity_scripts'].append({
                                'field': field_name,
                                'column': column_name,
                                'sql': sql
                            })
            # Generate Statistical Same SQL scripts
            if 'statistical_same' in rule_set:
                for field_name, check_enabled in rule_set['statistical_same'].items():
                    if check_enabled:
                        column_name = map_column_names('statistical_same', field_name)
                        sql = generate_statistical_same_sql(column_name, field_name)
                        if sql:
                            rule_scripts['statistical_same_scripts'].append({
                                'field': field_name,
                                'column': column_name,
                                'sql': sql
                            })
            # Generate Statistical Different SQL scripts
            if 'statistical_different' in rule_set:
                for field_name, check_enabled in rule_set['statistical_different'].items():
                    if check_enabled:
                        # Map comparison fields based on check type
                        if field_name == 'compare_balance_transaction':
                            column1 = 'account_balance'
                            column2 = 'transaction_amount'
                        elif field_name == 'compare_age_account_type':
                            column1 = 'customer_age'
                            column2 = 'account_type'
                        elif field_name == 'compare_branch_customer_city':
                            column1 = 'branch_city'
                            column2 = 'customer_city'
                        elif field_name == 'compare_transaction_type_amount':
                            column1 = 'transaction_type'
                            column2 = 'transaction_amount'
                        else:
                            column1 = field_name + '_1'
                            column2 = field_name + '_2'
                        
                        sql = generate_statistical_different_sql(column1, column2, field_name)
                        if sql:
                            rule_scripts['statistical_different_scripts'].append({
                                'field': field_name,
                                'column1': column1,
                                'column2': column2,
                                'sql': sql
                            })
            # Generate Category SQL scripts
            if 'categories' in rule_set:
                for field_name, expected_value in rule_set['categories'].items():
                    if expected_value:
                        column_name = map_column_names('categories', field_name)
                        sql = generate_category_sql(column_name, expected_value)
                        if sql:
                            rule_scripts['category_scripts'].append({
                                'field': field_name,
                                'column': column_name,
                                'expected_value': expected_value,
                                'sql': sql
                            })
            sql_scripts.append(rule_scripts)
        # Lưu vào file sql_script.json
        try:
            with open(SQL_SCRIPT_FILE, 'w', encoding='utf-8') as f:
                json.dump(sql_scripts, f, ensure_ascii=False, indent=2)
            return jsonify({"message": "Đã sinh và lưu SQL script vào sql_script.json"}), 200
        except Exception as e:
            return jsonify({"message": f"Lỗi khi lưu file: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Lỗi khi sinh SQL: {str(e)}"}), 500

@generar_bp.route('/test', methods=['GET'])
def test_generar():
    """
    Test endpoint for generar blueprint
    """
    return jsonify({
        "message": "Generar blueprint is working",
        "endpoints": {
            "generate_sql": "/sql/generate (GET)",
            "complete_sql": "/sql/complete-sql (GET)",
            "test": "/sql/test (GET)"
        }
    }), 200

@generar_bp.route('/complete-sql', methods=['GET'])
def generate_complete_sql():
    """
    Sinh SQL script hoàn chỉnh (dạng text) và lưu vào sql_script.json
    """
    try:
        rules_data = load_rules_data()
        if not rules_data:
            return jsonify({"message": "Không có dữ liệu rules để sinh SQL"}), 404
        complete_sql = []
        complete_sql.append("-- Data Validation SQL Script")
        complete_sql.append("-- Generated from rule engine")
        complete_sql.append("")
        for rule_set_idx, rule_set in enumerate(rules_data, 1):
            complete_sql.append(f"-- Rule Set {rule_set_idx}")
            complete_sql.append("")
            if 'value_range' in rule_set:
                for field_name, range_data in rule_set['value_range'].items():
                    if range_data.get('from') or range_data.get('to'):
                        column_name = map_column_names('value_range', field_name)
                        sql = generate_value_range_sql(
                            column_name, 
                            range_data.get('from'), 
                            range_data.get('to')
                        )
                        if sql:
                            complete_sql.append(f"-- {field_name} range validation")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
            if 'regex_template' in rule_set:
                for field_name, pattern in rule_set['regex_template'].items():
                    if pattern:
                        column_name = map_column_names('regex_template', field_name)
                        sql = generate_regex_sql(column_name, pattern)
                        if sql:
                            complete_sql.append(f"-- {field_name} format validation")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
            if 'continuity' in rule_set:
                for field_name, continuity_data in rule_set['continuity'].items():
                    if continuity_data:
                        column_name = map_column_names('continuity', field_name)
                        sql = generate_continuity_sql(
                            column_name,
                            continuity_data.get('start'),
                            continuity_data.get('end')
                        )
                        if sql:
                            complete_sql.append(f"-- {field_name} continuity validation")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
            if 'statistical_same' in rule_set:
                for field_name, check_enabled in rule_set['statistical_same'].items():
                    if check_enabled:
                        column_name = map_column_names('statistical_same', field_name)
                        sql = generate_statistical_same_sql(column_name, field_name)
                        if sql:
                            complete_sql.append(f"-- {field_name} duplicate check")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
            if 'statistical_different' in rule_set:
                for field_name, check_enabled in rule_set['statistical_different'].items():
                    if check_enabled:
                        if field_name == 'compare_balance_transaction':
                            column1 = 'account_balance'
                            column2 = 'transaction_amount'
                        elif field_name == 'compare_age_account_type':
                            column1 = 'customer_age'
                            column2 = 'account_type'
                        elif field_name == 'compare_branch_customer_city':
                            column1 = 'branch_city'
                            column2 = 'customer_city'
                        elif field_name == 'compare_transaction_type_amount':
                            column1 = 'transaction_type'
                            column2 = 'transaction_amount'
                        else:
                            column1 = field_name + '_1'
                            column2 = field_name + '_2'
                        sql = generate_statistical_different_sql(column1, column2, field_name)
                        if sql:
                            complete_sql.append(f"-- {field_name} comparison")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
            if 'categories' in rule_set:
                for field_name, expected_value in rule_set['categories'].items():
                    if expected_value:
                        column_name = map_column_names('categories', field_name)
                        sql = generate_category_sql(column_name, expected_value)
                        if sql:
                            complete_sql.append(f"-- {field_name} category validation")
                            complete_sql.append(sql + ";")
                            complete_sql.append("")
        sql_script = "\n".join(complete_sql)
        try:
            with open(SQL_SCRIPT_FILE, 'w', encoding='utf-8') as f:
                f.write(sql_script)
            return jsonify({"message": "Đã sinh và lưu complete SQL script vào sql_script.json"}), 200
        except Exception as e:
            return jsonify({"message": f"Lỗi khi lưu file: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Lỗi khi sinh SQL: {str(e)}"}), 500

@generar_bp.route('/load-sql', methods=['GET'])
def load_sql_from_file():
    """
    Load SQL scripts from sql_script.json file
    """
    try:
        sql_data = load_sql_scripts_from_file()
        
        if not sql_data:
            return jsonify({
                "error": "No SQL scripts found in file",
                "sql_data": []
            }), 404
        
        return jsonify({
            "message": "SQL scripts loaded from file successfully",
            "sql_data": sql_data
        }), 200
        
    except Exception as e:
        print(f"Error loading SQL from file: {e}")
        return jsonify({
            "error": f"Error loading SQL scripts from file: {str(e)}"
        }), 500

def save_sql_scripts_to_file(sql_scripts):
    """
    Save SQL scripts to sql_script.json file
    """
    try:
        with open(SQL_SCRIPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(sql_scripts, f, ensure_ascii=False, indent=2)
        print(f"SQL scripts saved to '{SQL_SCRIPT_FILE}'")
        return True
    except Exception as e:
        print(f"Error saving SQL scripts to file: {e}")
        return False

def load_sql_scripts_from_file():
    """
    Load SQL scripts from sql_script.json file
    """
    try:
        if os.path.exists(SQL_SCRIPT_FILE):
            with open(SQL_SCRIPT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    return json.loads(content)
        return []
    except Exception as e:
        print(f"Error loading SQL scripts from file: {e}")
        return []
