import os

from flask import Flask, render_template, redirect, make_response, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort

from data import db_session, polls_api, users_api
from data.add_poll import AddPollForm
from data.login_form import LoginForm
from data.poll import Poll
from data.register import RegisterForm
from data.users import User
from data.vote import Vote

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


DB_PATH = "db/voting.sqlite"

db_session.global_init(DB_PATH)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
@app.route("/index")
def index():
    session = db_session.create_session()
    polls = session.query(Poll).all()
    votes_by_poll = dict()
    for i in polls:
        votes_by_poll[i.id] = []
        votes_by_poll[i.id].append(len(session.query(Vote).filter(Vote.poll_id == i.id, Vote.flag == 1).all()))
        votes_by_poll[i.id].append(len(session.query(Vote).filter(Vote.poll_id == i.id, Vote.flag == 0).all()))

    last_vote_by_poll = dict()
    if current_user.is_authenticated:
        for i in polls:
            vot = session.query(Vote).filter(Vote.user_id == current_user.id, Vote.poll_id == i.id).first()
            if vot:
                last_vote_by_poll[i.id] = vot.flag
    return render_template("index.html", polls=polls, votes_by_poll=votes_by_poll, last_vote_by_poll=last_vote_by_poll,
                           title='Work log')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/vote/<int:poll_id>")
@login_required
def vote(poll_id):
    flag = int(request.args.get("flag"))

    session = db_session.create_session()
    prev_vote = session.query(Vote).filter(Vote.poll_id == poll_id, Vote.user_id == current_user.id).first()
    if prev_vote:
        session.delete(prev_vote)
        session.commit()
    new_vote = Vote(
        user_id=current_user.id,
        flag=flag,
        poll_id=poll_id
    )
    session.add(new_vote)
    session.commit()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            nickname=form.nickname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/add_poll', methods=['GET', 'POST'])
@login_required
def add_poll():
    add_form = AddPollForm()
    if add_form.validate_on_submit():
        session = db_session.create_session()
        poll = Poll(
            description=add_form.description.data,
            user_id=current_user.id
        )
        session.add(poll)
        session.commit()
        return redirect('/')
    return render_template('add_poll.html', title='Adding a poll', form=add_form)


@app.route('/polls/<int:id>', methods=['GET', 'POST'])
@login_required
def poll_edit(id):
    form = AddPollForm()
    if request.method == "GET":
        session = db_session.create_session()
        poll = session.query(Poll).filter(Poll.id == id,
                                          (Poll.user_id == current_user.id) | (current_user.id == 1)).first()
        if poll:
            form.description.data = poll.description
        else:
            abort(404)
    elif form.validate_on_submit():
        session = db_session.create_session()
        poll = session.query(Poll).filter(Poll.id == id,
                                          (Poll.user_id == current_user.id) | (current_user.id == 1)).first()
        if poll:
            poll.description = form.description.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_poll.html', title='Poll Edit', form=form)


@app.route('/poll_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_poll(id):
    session = db_session.create_session()
    poll = session.query(Poll).filter(Poll.id == id,
                                      (Poll.user_id == current_user.id) | (current_user.id == 1)).first()

    if poll:
        votes = session.query(Vote).filter(Vote.poll_id == id).all()
        session.delete(poll)
        for v in votes:
            session.delete(v)

        session.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init(DB_PATH)
    app.register_blueprint(polls_api.blueprint)
    app.register_blueprint(users_api.blueprint)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
