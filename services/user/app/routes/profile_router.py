from flask import Blueprint, request
from flask_login import login_required

from ..controllers import profile_controller

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/me', methods=['GET'])
@login_required
def get_profile():
    return profile_controller.get_profile()

@profile_bp.route('/me', methods=['PUT'])
@login_required
def update_profile():
    return profile_controller.update_profile(request)