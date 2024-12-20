# aicomment/api/urls.py
from flask import Blueprint
from aicomment.api.views import handle_user_prompt

api_bp = Blueprint('api', __name__)

api_bp.add_url_rule('/user-prompt', 'user_prompt', handle_user_prompt, methods=['POST'])
