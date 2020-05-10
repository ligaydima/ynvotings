from flask import jsonify, Blueprint, request

from data import db_session
from data.poll import Poll

blueprint = Blueprint('polls_api', __name__, template_folder='templates')


@blueprint.route('/api/polls')
def get_polls():
    session = db_session.create_session()
    polls = session.query(Poll).all()
    return jsonify({'polls': [item.to_dict(
        only=('id', 'description')
    )
        for item in polls]})


@blueprint.route('/api/polls/<int:poll_id>', methods=['GET'])
def get_one_poll(poll_id):
    session = db_session.create_session()
    poll = session.query(Poll).get(poll_id)
    if not poll:
        return jsonify({'error': 'Not found'})
    return jsonify({'poll': poll.to_dict(
        only=('id', 'description')
    )})
