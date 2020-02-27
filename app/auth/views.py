from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from . import auth
from .forms import LoginForm
from ..models import User


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# @auth.route('/admin', methods=['GET', 'POST'])
# @login_required
# def admin():
    # button = ParseButton()
    # if button.validate_on_submit():
        ### parse_func
    # return render_template('admin.html', form=button)