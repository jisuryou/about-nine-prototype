from flask import request, jsonify

def get_json():
    if not request.is_json:
        return None, jsonify({'success': False, 'message': 'Expected JSON'}), 400
    return request.get_json(), None, None
