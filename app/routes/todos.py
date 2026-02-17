from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Todo
from app.forms import TodoForm

todos_bp = Blueprint('todos', __name__)


def _own(id):
    return Todo.query.filter_by(id=id, user_id=current_user.id).first_or_404()


@todos_bp.route('/')
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created_at.desc()).all()
    return render_template('todos.html', todos=todos, form=TodoForm(), today=date.today())


@todos_bp.route('/add', methods=['POST'])
@login_required
def add():
    form = TodoForm()
    if form.validate_on_submit():
        try:
            db.session.add(Todo(
                title=form.title.data.strip(), priority=form.priority.data,
                due_date=form.due_date.data, due_time=form.due_time.data,
                user_id=current_user.id,
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error adding task. Please try again.', 'error')
    else:
        flash('Title is required.', 'error')
    return redirect(url_for('todos.index'))


@todos_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    try:
        task = _own(id)
        task.completed = not task.completed
        if not task.completed:
            task.reminder_sent = task.overdue_sent = False
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error updating task.', 'error')
    return redirect(url_for('todos.index'))


@todos_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = _own(id)
    form = TodoForm(obj=task)
    if form.validate_on_submit():
        try:
            task.title    = form.title.data.strip()
            task.priority = form.priority.data
            if form.due_date.data != task.due_date:
                task.reminder_sent = task.overdue_sent = False
            task.due_date = form.due_date.data
            task.due_time = form.due_time.data
            db.session.commit()
            flash('Task updated.', 'success')
            return redirect(url_for('todos.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating task.', 'error')
    return render_template('edit_todo.html', form=form, todo=task)


@todos_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        db.session.delete(_own(id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error deleting task.', 'error')
    return redirect(url_for('todos.index'))


@todos_bp.route('/clear-completed', methods=['POST'])
@login_required
def clear_completed():
    try:
        Todo.query.filter_by(user_id=current_user.id, completed=True).delete()
        db.session.commit()
        flash('Completed tasks cleared.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error clearing tasks.', 'error')
    return redirect(url_for('todos.index'))


@todos_bp.route('/api')
@login_required
def api():
    return jsonify([t.to_dict() for t in Todo.query.filter_by(user_id=current_user.id).all()])