import hashlib
from collections import namedtuple

from modules.user import *
from modules.chat import *

from  flask import Flask, render_template, request, flash, redirect, url_for, session


app = Flask(__name__)
app.secret_key = 'super secret'


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if (len(request.form) == 0):
        return render_template('register.html')

    else:
        try:
            register_user(
                request.form['login'], request.form['password'], request.form['name'], 
                request.form['surname'], request.form['email'], request.form['department'], 
                request.form['rank'], request.headers
                )
            return redirect(url_for('login_page'))

        except Exception as e:
            flash(e)
            return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))    

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'auth' not in session:
        try:
            login = request.form['login']
            password = request.form['password']

            user = User(login, password)
            session['auth'] = user.key
            
            update_session(login, request.headers)

            return redirect(url_for('menu'))
        except:
            flash("Invalid login or password!")
            return redirect(url_for('main'))

    return redirect(url_for('menu'))
    
@app.route('/menu')
def menu():
    if 'auth' not in session:
        flash('Please authorize!')
        return redirect(url_for('login_page'))
    
    if ';' not in session['auth']:
        session.pop('auth')
        return redirect(url_for('login_page'))

    key = session['auth'].split(';')

    try:
        user = User(key[0], key[1])
        chats = user.get_chats()
    except:
        flash('Please authorize!')
        return redirect(url_for('login_page'))

    
    return render_template("selector.html", chats=chats, name=key[0])

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'drop' in request.form:
        drop_chat(
            username=session['auth'].split(';')[0],
            chat_id=request.form.get('drop')
            )
    elif 'redirect' in request.form:
        session['chat_id'] = request.form.get('redirect')
        return render_template(
            'chat.html',
            chat_name=get_chat_name(session['chat_id']),
            messages=get_messages(request.form.get('redirect'))
            )
    elif 'send-msg' in request.form:
        send_message(
            text=request.form.get('text-msg'),
            username=session['auth'].split(';')[0],
            chat_id=session['chat_id']
            )
        
        return render_template('chat.html', chat_name=get_chat_name(session['chat_id']), messages=get_messages(session['chat_id']))
        
    


if __name__ == '__main__':
    app.run()