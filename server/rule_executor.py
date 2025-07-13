from flask import Blueprint, jsonify
import sqlite3
import json
import os

rule_executor_bp = Blueprint('rule_executor', __name__, url_prefix='/execute')

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.db')
SQL_SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_script.json')
RESULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result.json')

def load_sql_scripts():
    with open(SQL_SCRIPT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Nếu là dạng text (complete-sql) thì chuyển thành list
        if isinstance(data, str):
            return [data]
        # Nếu là list các dict (dạng /sql/generate) thì lấy từng script
        scripts = []
        for rule_set in data:
            for group in ['value_range_scripts', 'regex_template_scripts', 'continuity_scripts', 'statistical_same_scripts', 'statistical_different_scripts', 'category_scripts']:
                for item in rule_set.get(group, []):
                    scripts.append(item['sql'])
        return scripts

def execute_sql_scripts(scripts):
    results = []
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for idx, script in enumerate(scripts):
        try:
            cursor.execute(script)
            result = cursor.fetchall()
            results.append({
                'script': script,
                'result': result
            })
        except Exception as e:
            results.append({
                'script': script,
                'error': str(e)
            })
    conn.close()
    return results

@rule_executor_bp.route('/run', methods=['GET'])
def run_rule_executor():
    try:
        scripts = load_sql_scripts()
        results = execute_sql_scripts(scripts)
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return jsonify({'message': 'Đã thực thi xong các rule và lưu kết quả vào result.json', 'total': len(results)}), 200
    except Exception as e:
        return jsonify({'message': f'Lỗi: {str(e)}'}), 500

@rule_executor_bp.route('/result', methods=['GET'])
def get_result():
    try:
        with open(RESULT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'result': data}), 200
    except Exception as e:
        return jsonify({'message': f'Lỗi: {str(e)}'}), 500
