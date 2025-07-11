from flask import Flask, jsonify
from flask_cors import CORS

from check_regex_pattern import check_regex 
from rule_parsing import rule_parsing
from generar import generar_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(check_regex)
app.register_blueprint(rule_parsing)
app.register_blueprint(generar_bp)

@app.route('/')
def home():
    return jsonify({"Message:" "Welcome to main Data Rule Engine Server"})

if __name__ == '__main__':
    app.run(debug = True, port = 5000)