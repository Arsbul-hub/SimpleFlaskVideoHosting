from flask import request, jsonify, Blueprint
from app.models import User

blueprint = Blueprint('app_api', __name__, template_folder='templates')


@blueprint.route('/api/user', methods=["GET"])
def get_user():
    user = User.query.get(request.args["id"])
    if not user:
        return jsonify(
            {"error": "User not found"}
        )
    studios = user.studios

    return jsonify(
        {"status": "OK", "data": {"username": user.username, "studios_id": [i.id for i in studios]}})
