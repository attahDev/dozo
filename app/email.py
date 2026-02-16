"""Email notifications — due reminder, overdue alert, daily digest, welcome, password changed."""
import logging
from datetime import date, datetime, timedelta
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail

log = logging.getLogger(__name__)

# ── Shared inline CSS ────────────────────────────────────────────────────────
_CSS = """
body{margin:0;padding:0;background:#0d0d0d;font-family:'Helvetica Neue',Arial,sans-serif}
.w{max-width:560px;margin:0 auto;padding:32px 16px}
.c{background:#141414;border:1px solid #2a2a2a;border-radius:10px;overflow:hidden}
.h{padding:24px 28px;border-bottom:1px solid #2a2a2a}
.logo{font-size:22px;font-weight:900;letter-spacing:.1em;color:#f59e0b}
.b{padding:28px;color:#e8e6e0}
h1{font-size:20px;margin:0 0 8px;color:#e8e6e0}
p{font-size:14px;line-height:1.6;color:#9a9590;margin:0 0 14px}
.task{background:#1c1c1c;border:1px solid #333;border-left:3px solid #f59e0b;
      border-radius:6px;padding:14px 18px;margin:18px 0}
.tn{font-size:16px;font-weight:600;color:#e8e6e0;margin-bottom:4px}
.tm{font-size:11px;color:#5a5550;font-family:monospace}
.overdue{border-left-color:#ef4444;background:rgba(239,68,68,.05)}
.btn{display:inline-block;padding:11px 24px;background:#f59e0b;color:#0d0d0d;
     font-weight:700;font-size:13px;border-radius:5px;text-decoration:none;margin:4px 0 18px}
.f{padding:20px 28px;border-top:1px solid #1c1c1c}
.f p{font-size:11px;color:#3a3530;margin:0}
.f a{color:#5a5550}
"""

def _send(subject, to, html):
    try:
        mail.send(Message(subject=subject, recipients=[to], html=html,
                          body='Please view in an HTML email client.'))
        log.info('Email sent: %s → %s', subject, to)
        return True
    except Exception as e:
        log.error('Email failed: %s → %s: %s', subject, to, e)
        return False

def _url():
    return current_app.config.get('APP_URL', 'http://localhost:5000')

def _r(tmpl, **ctx):
    return render_template_string(tmpl, css=_CSS, url=_url(), **ctx)


# ── Templates ────────────────────────────────────────────────────────────────

_REMINDER = """<!DOCTYPE html><html><head><style>{{css}}</style></head><body><div class="w"><div class="c">
<div class="h"><span class="logo">DZ DOZO</span></div>
<div class="b">
  <h1>⏰ Task due soon</h1>
  <p>Hey <strong style="color:#e8e6e0">{{user}}</strong>, this task is coming up:</p>
  <div class="task"><div class="tn">{{title}}</div><div class="tm">DUE: {{due}} · {{priority|upper}}</div></div>
  <a href="{{url}}/todos/" class="btn">Open Tasks →</a>
</div>
<div class="f"><p>DOZO · <a href="{{url}}/auth/settings">Manage notifications</a></p></div>
</div></div></body></html>"""

_OVERDUE = """<!DOCTYPE html><html><head><style>{{css}}</style></head><body><div class="w"><div class="c">
<div class="h"><span class="logo">DZ DOZO</span></div>
<div class="b">
  <h1>⚠ Task overdue</h1>
  <p>Hey <strong style="color:#e8e6e0">{{user}}</strong>, this task passed its due date:</p>
  <div class="task overdue"><div class="tn">{{title}}</div><div class="tm">WAS DUE: {{due}}</div></div>
  <a href="{{url}}/todos/" class="btn">Go to Tasks →</a>
</div>
<div class="f"><p>DOZO · <a href="{{url}}/auth/settings">Manage notifications</a></p></div>
</div></div></body></html>"""

_DIGEST = """<!DOCTYPE html><html><head><style>{{css}}
.sec{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#5a5550;font-family:monospace;margin:20px 0 6px}
ul{margin:0;padding:0;list-style:none}
li{padding:8px 0;border-bottom:1px solid #1c1c1c;font-size:13px;color:#9a9590}
li:last-child{border:none}
.t{color:#e8e6e0;font-weight:500}
</style></head><body><div class="w"><div class="c">
<div class="h"><span class="logo">DZ DOZO</span></div>
<div class="b">
  <h1>☀ Good morning, {{user}}</h1>
  <p>Your task rundown for <strong style="color:#e8e6e0">{{today}}</strong>.</p>
  {% if overdue %}<p class="sec">⚠ Overdue ({{overdue|length}})</p>
  <ul>{% for t in overdue %}<li><span class="t">{{t.title}}</span></li>{% endfor %}</ul>{% endif %}
  {% if due_today %}<p class="sec">◷ Due today ({{due_today|length}})</p>
  <ul>{% for t in due_today %}<li><span class="t">{{t.title}}</span></li>{% endfor %}</ul>{% endif %}
  {% if upcoming %}<p class="sec">→ Upcoming ({{upcoming|length}})</p>
  <ul>{% for t in upcoming %}<li><span class="t">{{t.title}}</span>
    <span style="float:right;font-family:monospace;font-size:11px;color:#5a5550">{{t.due_date.strftime('%b %d')}}</span>
  </li>{% endfor %}</ul>{% endif %}
  {% if not overdue and not due_today and not upcoming %}<p style="color:#5a5550;font-style:italic">No pending tasks — enjoy your clear day ✓</p>{% endif %}
  <a href="{{url}}/todos/" class="btn" style="margin-top:20px">Open Tasks →</a>
</div>
<div class="f"><p>DOZO Daily Digest · <a href="{{url}}/auth/settings">Manage notifications</a></p></div>
</div></div></body></html>"""

_WELCOME = """<!DOCTYPE html><html><head><style>{{css}}</style></head><body><div class="w"><div class="c">
<div class="h"><span class="logo">DZ DOZO</span></div>
<div class="b">
  <h1>Welcome to DOZO 👋</h1>
  <p>Hey <strong style="color:#e8e6e0">{{user}}</strong> — your account is ready.</p>
  <p>Set due dates on tasks and DOZO will email you before deadlines hit.</p>
  <a href="{{url}}/todos/" class="btn">Go to Tasks →</a>
  <p style="margin-top:8px;font-size:13px">Quick tip: press <code style="color:#f59e0b">N</code> to add a task instantly.</p>
</div>
<div class="f"><p>DOZO · Stop forgetting. Start doing.</p></div>
</div></div></body></html>"""

_PW_CHANGED = """<!DOCTYPE html><html><head><style>{{css}}</style></head><body><div class="w"><div class="c">
<div class="h"><span class="logo">DZ DOZO</span></div>
<div class="b">
  <h1>🔐 Password changed</h1>
  <p>Hey <strong style="color:#e8e6e0">{{user}}</strong>, your password was just updated.</p>
  <p>If this wasn't you, <a href="{{url}}/auth/login" style="color:#f59e0b">sign in immediately</a> and reset it.</p>
</div>
<div class="f"><p>DOZO Security Alert · {{ts}}</p></div>
</div></div></body></html>"""


# ── Public API ───────────────────────────────────────────────────────────────

def send_reminder(user, task) -> bool:
    if not user.notify_reminder:
        return False
    due = task.due_date.strftime('%B %d') + (f' at {task.due_time.strftime("%H:%M")}' if task.due_time else '')
    return _send(f'⏰ "{task.title}" is due soon', user.email,
                 _r(_REMINDER, user=user.username, title=task.title, due=due, priority=task.priority))


def send_overdue(user, task) -> bool:
    if not user.notify_overdue:
        return False
    return _send(f'⚠ Overdue: "{task.title}"', user.email,
                 _r(_OVERDUE, user=user.username, title=task.title,
                    due=task.due_date.strftime('%B %d')))


def send_digest(user, overdue, due_today, upcoming) -> bool:
    if not user.notify_digest or (not overdue and not due_today and not upcoming):
        return False
    return _send(f'☀ DOZO Daily — {date.today().strftime("%b %d")}', user.email,
                 _r(_DIGEST, user=user.username, today=date.today().strftime('%A, %B %d'),
                    overdue=overdue, due_today=due_today, upcoming=upcoming))


def send_welcome(user) -> bool:
    return _send('Welcome to DOZO 👋', user.email, _r(_WELCOME, user=user.username))


def send_pw_changed(user) -> bool:
    return _send('🔐 Your DOZO password was changed', user.email,
                 _r(_PW_CHANGED, user=user.username, ts=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')))