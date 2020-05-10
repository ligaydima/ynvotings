from flask import jsonify, Blueprint, request
from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User

blueprint = Blueprint('users_api', __name__, template_folder='templates')


def set_password(password):
    return generate_password_hash(password)


@blueprint.route('/api/users')
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify({'users': [item.to_dict(
        only=('id', 'nickname')
    )
        for item in users]})


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify({'users': users.to_dict(
        only=('id', 'nickname')
    )})
