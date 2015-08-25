#-*-coding:utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from flask.ext.script import Manager
from flask import Flask,render_template,session,redirect,url_for,flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.script import Manager
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.mail import Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app =Flask(__name__)
#数据库的配置
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'hard to guess string'

#邮件设置
app.config['MaIL_SERVER'] = 'smtp.126.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hugesoft@126.com'
app.config['MAIL_PASSWORD'] = 'enter0087!'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <hugesoft@126.com>'
app.config['FLASKY_ADMIN'] = 'hugesoft@126.com'

app.debug = True
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

#邮件发送函数
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

class NameForm(Form):
    name = StringField(u'请输入你的姓名', validators=[Required()])
    submit = SubmitField(u'提交')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('与上次输入的不同！')
        if app.config['FLASKY_ADMIN']:
            send_email(app.config['FLASKY_ADMIN'],'New User',
                'mail/new_user', user=user)

        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

if (__name__) == '__main__':
    manager.run()

