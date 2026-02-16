from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from app.email import send_welcome, send_pw_changed

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('todos.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        return redirect(request.args.get('next') or url_for('todos.index'))
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('todos.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data.strip(), email=form.email.data.lower())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            try: send_welcome(user)
            except Exception: pass
            login_user(user)
            flash('Account created — welcome!', 'success')
            return redirect(url_for('todos.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Signed out.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    pf  = ProfileForm(current_user.username, current_user.email, obj=current_user)
    pwf = ChangePasswordForm()
    action = request.form.get('action', '')

    if request.method == 'POST':
        try:
            if action == 'profile' and pf.validate_on_submit():
                current_user.username = pf.username.data.strip()
                current_user.email    = pf.email.data.lower()
                current_user.bio      = pf.bio.data
                db.session.commit()
                flash('Profile updated.', 'success')

            elif action == 'password' and pwf.validate_on_submit():
                if not current_user.check_password(pwf.current.data):
                    flash('Current password is wrong.', 'error')
                else:
                    current_user.set_password(pwf.new.data)
                    db.session.commit()
                    try: send_pw_changed(current_user)
                    except Exception: pass
                    flash('Password updated.', 'success')

            elif action == 'appearance':
                # Appearance preferences saved via localStorage on client-side
                # Could optionally save to database here if you add fields to User model
                flash('Appearance preferences saved.', 'success')

            elif action == 'notifications':
                current_user.notify_reminder = 'notify_reminder' in request.form
                current_user.notify_overdue  = 'notify_overdue'  in request.form
                current_user.notify_digest   = 'notify_digest'   in request.form
                db.session.commit()
                flash('Notification preferences saved.', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')

        return redirect(url_for('auth.settings'))

    return render_template('settings.html', pf=pf, pwf=pwf)


@auth_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted.', 'success')
    return redirect(url_for('main.index'))