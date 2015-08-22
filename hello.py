#-*-coding:utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask.ext.script import Manager
from flask import Flask,render_template,session,redirect,url_for,flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.script import Manager
from flask.ext.moment import Moment

app =Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

app.debug = True
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

class NameForm(Form):
    name = StringField(u'请输入你的姓名', validators=[Required()])
    submit = SubmitField(u'提交')

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('与上次输入的不同！')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

if (__name__) == '__main__':
    manager.run()

