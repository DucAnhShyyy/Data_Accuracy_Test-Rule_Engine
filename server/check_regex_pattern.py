from flask import Blueprint, request, jsonify
import re

check_regex = Blueprint('check_regex', __name__, url_prefix = '/validation')

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_REGEX = r"^(?:\+84|0)\s?\d{9,10}$"

@check_regex.route('/check-format', methods = ['POST'])
def validate_format():
    if not request.is_json:
        return jsonify({"Error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    print(f"Validation request received - Email: '{email}', Phone: '{phone}'")

    results = {}

    # Check email format
    if email:
        if re.fullmatch(EMAIL_REGEX, email):
            results['email_valid'] = True
            results['email_message'] = "Email Valid"
        else: 
            results['email_valid'] = False
            results['email_message'] = "Email Invalid"
    else:
        results['email_valid'] = True  # Skip validation if empty
        results['email_message'] = "Email not provided"

    # Check phone number format
    if phone:
        if re.fullmatch(PHONE_REGEX, phone):
            results['phone_number_valid'] = True
            results['phone_number_message'] = "Phone Number Valid"
        else: 
            results['phone_number_valid'] = False
            results['phone_number_message'] = "Phone Number Invalid"
    else:
        results['phone_number_valid'] = True  # Skip validation if empty
        results['phone_number_message'] = "Phone Number not provided"

    print(f"Validation results: {results}")
    return jsonify(results), 200