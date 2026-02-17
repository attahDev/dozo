from datetime import datetime, date
from flask_login import UserMixin
from app import db, login, bcrypt


@login.user_loader
def load_user(uid): return User.query.get(int(uid))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(64),  unique=True, nullable=False, index=True)
    email           = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash   = db.Column(db.String(256), nullable=False)
    bio             = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # notification prefs
    notify_reminder = db.Column(db.Boolean, default=True)
    notify_overdue  = db.Column(db.Boolean, default=True)
    notify_digest   = db.Column(db.Boolean, default=False)

    todos = db.relationship('Todo', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, pw):   self.password_hash = bcrypt.generate_password_hash(pw).decode()
    def check_password(self, pw): return bcrypt.check_password_hash(self.password_hash, pw)


class Todo(db.Model):
    __tablename__ = 'todos'
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(256), nullable=False)
    completed     = db.Column(db.Boolean, default=False, nullable=False)
    priority      = db.Column(db.String(16), default='normal', nullable=False)
    due_date      = db.Column(db.Date)
    due_time      = db.Column(db.Time)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    reminder_sent = db.Column(db.Boolean, default=False)
    overdue_sent  = db.Column(db.Boolean, default=False)

    @property
    def is_overdue(self):
        return not self.completed and self.due_date is not None and self.due_date < date.today()

    @property
    def is_due_today(self):
        return self.due_date == date.today() if self.due_date else False

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title,
            'completed': self.completed, 'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
        }