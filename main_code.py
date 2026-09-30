from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mailman import Mail, EmailMessage
from email_validator import validate_email, EmailNotValidError
from werkzeug.exceptions import HTTPException
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = '9s☼№▬us░j35○═nkT5♠ljV*Eg╔Sl◘(g↓☻O▒q•q↕s¶░D♫┬☼rk8Z!0←№4№I♪№q↕mNm8'
app.permanent_session_lifetime = timedelta(days=31)
admin_list = ['lyceum_phymly_main_admin']

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_STARTTLS'] = False
app.config['MAIL_USERNAME'] = 'chemlysis@gmail.com'
app.config['MAIL_PASSWORD'] = 'lkyzwygqjbwnqujs'
app.config['MAIL_DEFAULT_SENDER'] = 'ChemLysis Account Verification'

mail = Mail(app)

ua = ["а", "б", "в", "г", "ґ", "д", "е", "є", "ж", "з", "и", "і", "ї", "й", "к",
    "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "ю", "я"]

chem_classes = {"луги":"луги", "луг":"луги",
                "кислоти":"кислоти", "кислота":"кислоти",
                "оксиди":"оксиди", "оксид":"оксиди",
                "солі":"солі", "сіль":"солі",
                "основи":"основи", "основа":"основи",
                "метали":"метали", "метал":"метали",
                "неметали":"неметали", "неметал":"неметали"}

'''
@app.errorhandler(HTTPException)
def handle_http_errors(e):
    return redirect('/')
'''

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.before_request
def init_session_once():
    if 'loaded' not in session:
        session['task_id'] = None
        session['working_task'] = None
        session['no_tasks'] = False
        session['loaded'] = True
        session['admin'] = False
        session['admin_mode'] = False
        session['logined'] = False
        session['num'] = 0
        session['info'] = None
        session['not_found'] = False
        session['formula'] = ''
        session['tasks_given'] = []
        session['is_signed_in'] = False
        session['person'] = {'username': "", 'password': ""}
        session['username_value'], session['password_value'] = "", ""
        session['email_value'], session['password_2_value'] = "", ""
        session['success_login'] = False
        session['person_login'] = {'username_login': "", 'password_login': ""}
        session['username_value_login'], session['password_value_login'] = "", ""
        session['show_answer_can'] = False
        session['show_note_can'] = False
        session['begin_verification'] = False
        session['amount_of_attemps'] = 5
        session['blocked_sign_in'] = False
        session['email_not_exists'] = False
        session['show_tasks'] = False
        session['show_answer'] = False
        session['show_note'] = False
        session['blocked_previous_button'] = True
        session['blocked_next_button'] = False
        session['Formula'] = ""
        session['current_formula'] = 0
        session['formulas'] = []
        session['blocked_next_formula'] = False
        session['blocked_previous_formula'] = True
        session['formula_classes'] = False
        session['task_status'] = 'new'
        session['task_statuses'] = []
        session['show_formulas_buttons'] = False
        session['selected_statuses_4_filters'] = ['all_statuses']
        session['selected_types_4_filters'] = ['all_types']
        session['tasks_given_filtered'] = []
        session['task_statuses_filtered'] = []
        session['searching_text'] = ""
        session['amount_class_formulas'] = 0
        session['entered_class'] = ""
        session['tasks_list_amount'] = 1
        session['blocked_previous_tasks_list_button'] = True
        session['blocked_next_tasks_list_button'] = False
        session['can_scroll_tasks'] = True
        session['tags'] = []
        session['set_task_type_4_show'] = [""]
        session['show_profile_info'] = False
        session['person_tasks_info'] = {'done':0, 'revised':0, 'done_amount':0, 'revised_amount':0, 'new_amount':0}
        session['what_changing'] = ""
        session['all_found_users_list'] = [['nobody more(', 'none']]
        session['can_show_users_list'] = False

def get_type_4_show():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT type FROM tasks WHERE task_id = ?', (session['task_id'],))
        tranzit = cursor.fetchone()
        if tranzit:
            session['set_task_type_4_show'] = [tranzit[0]]
    return 0

def get_tags():
    task_id = session['task_id']
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT tags FROM tasks WHERE task_id = ?", (task_id,))
        tags = cursor.fetchone()
        this = []
        if tags and tags[0]:
            tags = tags[0].split()
            for tag in tags:
                if '_' in tag:
                    tag = tag.replace("_", " ")
                this.append(tag)
        else: this = []
        session['tags'] = this
        return session['tags']

def get_task_status(task_id, username):
    task_id = str(task_id)
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_info = cursor.fetchone()
        if user_info:
            done_tasks = user_info[5]
            revised_tasks = user_info[6]
            if done_tasks: done_tasks = done_tasks.split()
            else: done_tasks = []
            if revised_tasks: revised_tasks = revised_tasks.split()
            else: revised_tasks = []
            if task_id in done_tasks: status = 'done'
            elif task_id in revised_tasks: status = 'revised'
            else: status = 'new'
        else:
            status = 'new'
        return status

def find_task_status():
    person = session['person_login']
    username = person['username_login']
    task_id = session['task_id']
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_info = cursor.fetchone()
        if user_info:
            done_tasks = user_info[5]
            revised_tasks = user_info[6]
            if done_tasks: done_tasks = done_tasks.split()
            else: done_tasks = []
            if revised_tasks: revised_tasks = revised_tasks.split()
            else: revised_tasks = []
            if str(task_id) in done_tasks: session['task_status'] = 'done'
            elif str(task_id) in revised_tasks: session['task_status'] = 'revised'
            else: session['task_status'] = 'new'
        else: session['task_status'] = 'new'
    return

def find_tag(tag, word):
    if not tag: return(tag, 0)
    work_tag = tag.lower().split()
    persame = 1/max(len(tag), len(word))
    result = []
    for work in work_tag:
        procent = 0
        previous_idx = 0
        for letter in word:
            if letter not in work:
                procent -= persame
                continue
            idx = work.index(letter)
            length = abs(idx - previous_idx)
            if idx+1 == len(work): length = 1
            elif length == 0 and work[idx+1] == letter: length = 1
            elif length == 0: length = min(len(tag), len(word))
            procent += persame / length
            previous_idx = idx
        result.append(procent)
    procent = max(result)
    return(tag, round(procent, 4))

def normalize_formula(formula):
    subscript_map = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    formula = formula.translate(subscript_map).lower()
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT formula, correct_name, common_name FROM description")
        tranzit_name = cursor.fetchall()
        lst = []
        for block in tranzit_name:
            lst += list(block)
        itis = ""
        for one in lst:
            work = one.lower()
            if "," in work:
                idx = work.index(",")
                work = work[idx+2:]
            if work == formula:
                itis = one
                break
        if itis and itis[-1].lower() in ua:
            cursor.execute("SELECT formula FROM description WHERE correct_name = ? OR common_name = ? OR the_formula = ?", (itis, itis, itis,))
            xformula = cursor.fetchone()
            if xformula:
                itis = xformula[0]
            else:
                itis = ""
        if not itis:
            formula = ""
            session["Formula"] = ""
        else:
            formula = itis
            cursor.execute("SELECT the_formula FROM description WHERE formula = ?", (formula,))
            the_formula = cursor.fetchone()
            if the_formula and the_formula[0]: the_formula = the_formula[0]
            else: the_formula = 'not_found'
            session["Formula"] = the_formula
    return formula

def cleaner(folder_path):
    if not os.path.exists(folder_path):
        return ["static/images/default.png"]
    photos = os.listdir(folder_path)
    images_urls = [os.path.join(folder_path, photo) for photo in photos]
    images_urls.sort()
    return images_urls

@app.route("/", methods=['POST', 'GET'])
def index():
    session['task_id'] = None
    session['working_task'] = None
    session['no_tasks'] = False
    session['loaded'] = True
    session['num'] = 0
    session['info'] = None
    session['not_found'] = False
    session['formula'] = ''
    session['tasks_given'] = []
    session['is_signed_in'] = False
    session['show_answer_can'] = False
    session['show_note_can'] = False
    session['show_tasks'] = False
    session['show_answer'] = False
    session['show_note'] = False
    session['blocked_previous_button'] = True
    session['blocked_next_button'] = False
    session['Formula'] = ""
    session['current_formula'] = 0
    session['formulas'] = []
    session['blocked_next_formula'] = False
    session['blocked_previous_formula'] = True
    session['formula_classes'] = False
    session['task_status'] = 'new'
    session['task_statuses'] = []
    session['selected_statuses_4_filters'] = ['all_statuses']
    session['selected_types_4_filters'] = ['all_types']
    session['tasks_given_filtered'] = []
    session['task_statuses_filtered'] = []
    session['searching_text'] = ""
    session['amount_class_formulas'] = 0
    session['entered_class'] = ""
    session['tasks_list_amount'] = 1
    session['blocked_previous_tasks_list_button'] = True
    session['blocked_next_tasks_list_button'] = False
    session['can_scroll_tasks'] = True
    session['tags'] = []
    session['set_task_type_4_show'] = [""]
    session['show_profile_info'] = False
    session['person_tasks_info'] = {'done':0, 'revised':0, 'done_amount':0, 'revised_amount':0, 'new_amount':0}
    session['what_changing'] = ""
    session['all_found_users_list'] = [['nobody more(', 'none']]
    session['can_show_users_list'] = False
    return render_template('main.html',
    formula=session['formula'],
    information=session['info'],
    num=session['num'],
    admin = session['admin'],
    admin_mode = session['admin_mode'],
    logined=session.get('logined', False),
    not_found = session['not_found'],
    person=session["person_login"],
    blocked_sign_in = session['blocked_sign_in'],
    no_tasks = session['no_tasks'],
    tasks_given=session['tasks_given'],
    show_tasks = session['show_tasks'],
    amount_class_formulas = session['amount_class_formulas'],
    entered_class = session['entered_class'],
    show_profile_info = session['show_profile_info'],
    person_tasks_info = session['person_tasks_info'])

@app.route('/about')
def about():
    session['show_profile_info'] = False
    return render_template('about.html',
    formula=session['formula'],
    logined = session['logined'],
    admin = session['admin'],
    person = session['person_login'])

@app.route("/search", methods=["POST", "GET"])
def search():
    previous = session['formula']
    formula = request.values.get("formula", session['formula']).strip()
    formula = formula.lower()
    xformula = formula
    if formula in chem_classes:
        formula = chem_classes[formula]
        session['entered_class'] = formula.capitalize()
        session['show_formulas_buttons'] = True
        prev_formulas = session['formulas']
        formulas = []
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM description')
            if cursor:
                for row in cursor:
                    chem_class = row[6]
                    if chem_class == formula:
                        formulas.append(row)
        if formulas:
            if prev_formulas != formulas: session['current_formula'] = 0
            session['not_found'] = False
            session['formula_classes'] = True
            session['formulas'] = formulas
            session['amount_class_formulas'] = len(formulas)
            prev_formula = session['info']
            the_formula = list(session['formulas'][session['current_formula']])
            the_formula[1] = cleaner(the_formula[1])
            session['info'] = the_formula
            if prev_formula != the_formula:
                session['num'] = 0
            session['formula'] = formula
            session['Formula'] = the_formula[7]
        else:
            session['formula_classes'] = False
            session['formulas'] = formulas
            session['amount_class_formulas'] = len(formulas)
            session['not_found'] = True
            session['Formula'] = xformula
    else:
        if formula:
            session['formula_classes'] = False
            session['show_formulas_buttons'] = False
            if previous != formula:
                session['num'] = 0
                formula = normalize_formula(formula)
            session['formula'] = formula
            with sqlite3.connect("database.db", timeout=30) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM description WHERE formula = ?", (formula,))
                information = cursor.fetchone()
                if information is None:
                    information = None
                    session["not_found"] = True
                    session['Formula'] = xformula
                else:
                    information = list(information)
                    information[1] = cleaner(information[1])
                    session["not_found"] = False
                session['info'] = information
        else:
            session['not_found'] = True
            session['Formula'] = xformula
    blocked_previous_button = False
    if session['num'] == 0:
        blocked_previous_button = True
    session['blocked_previous_button'] = blocked_previous_button
    if session['info']:
        blocked_next_button = False
        if session['num'] + 1 == len(session['info'][1]):
            blocked_next_button = True
        session['blocked_next_button'] = blocked_next_button
    blocked_previous_formula = False
    if session['current_formula'] == 0:
        blocked_previous_formula = True
    session['blocked_previous_formula'] = blocked_previous_formula
    if session['formulas']:
        blocked_next_formula = False
        if session['current_formula'] + 1 == len(session['formulas']):
            blocked_next_formula = True
        session['blocked_next_formula'] = blocked_next_formula
    return render_template('main.html',
    formula=session['formula'],
    Formula = session['Formula'],
    information=session['info'],
    num=session['num'],
    admin = session['admin'],
    admin_mode = session['admin_mode'],
    logined=session.get('logined', False),
    not_found = session['not_found'],
    person=session["person_login"],
    blocked_previous_button = session['blocked_previous_button'],
    blocked_next_button = session['blocked_next_button'],
    blocked_sign_in = session['blocked_sign_in'],
    show_formulas_buttons = session['show_formulas_buttons'],
    blocked_next_formula = session['blocked_next_formula'],
    blocked_previous_formula = session['blocked_previous_formula'],
    formula_classes = session['formula_classes'],
    amount_class_formulas = session['amount_class_formulas'],
    entered_class = session['entered_class'],
    task_id = session['task_id'],
    show_profile_info = session['show_profile_info'],
    person_tasks_info = session['person_tasks_info'],
    users_list = session['all_found_users_list'])

@app.route('/next_formula')
def next_formula():
    num = session['current_formula']
    info = session['formulas']
    length = len(info)
    if not info: num = 0
    elif num + 1 < length:
        num += 1
    blocked_next_formula = False
    if num + 1 == length:
        blocked_next_formula = True
    session['current_formula'] = num
    session['blocked_next_formula'] = blocked_next_formula
    return redirect(url_for('search', formula=session['formula']))

@app.route('/previous_formula')
def previous_formula():
    num = session['current_formula']
    info = session['formulas']
    if not info: num = 0
    elif num - 1 > -1:
        num -= 1
    blocked_previous_formula = False
    if num == 0:
        blocked_previous_formula = True
    session['current_formula'] = num
    session['blocked_previous_formula'] = blocked_previous_formula
    return redirect(url_for('search', formula=session['formula']))

@app.route('/next_photo', methods=['POST', 'GET'])
def next_photo():
    num = session.get('num', 0)
    info = session.get('info')
    if not info or not info[1]:
        return jsonify({'status': 'error', 'message': 'No info'}), 400
    photos = info[1]
    max_idx = len(photos) - 1
    if num < max_idx:
        num += 1
        session['num'] = num
    blocked_next = num >= max_idx
    blocked_prev = num <= 0
    session['blocked_next_button'] = blocked_next
    session['blocked_previous_button'] = blocked_prev
    return jsonify({'status': 'ok','num': num,'photo_url': photos[num],'blocked_next_button': blocked_next,'blocked_previous_button': blocked_prev,})

@app.route('/previous_photo', methods=['POST', 'GET'])
def previous_photo():
    num = session.get('num', 0)
    info = session.get('info')
    if not info or not info[1]: return jsonify({'status': 'error', 'message': 'No info'}), 400
    photos = info[1]
    max_idx = len(photos) - 1
    if num > 0:
        num -= 1
        session['num'] = num
    blocked_next = num >= max_idx
    blocked_prev = num <= 0
    session['blocked_next_button'] = blocked_next
    session['blocked_previous_button'] = blocked_prev
    return jsonify({'status': 'ok','num': num,'photo_url': photos[num],'blocked_next_button': blocked_next,'blocked_previous_button': blocked_prev,})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/signin")
def signin():
    session['show_profile_info'] = False
    return render_template('signin.html',
    formula = session['formula'],
    email_not_exists = session['email_not_exists'],
    begin_verification = session['begin_verification'],
    username_value=session['username_value'],
    password_value=session['password_value'],
    password_2_value=session['password_2_value'],
    email_value=session['email_value'],
    amount_of_attemps = session['amount_of_attemps'])

@app.route('/change_email')
def change_email():
    session['begin_verification'] = False
    return redirect('/signin')

@app.route("/send_pin")
def send_pin():
    email = session['email_value']
    otp_code = str(random.randint(100000, 999999))
    session['otp_code'] = otp_code
    try:
        email_info = validate_email(email, check_deliverability=True)
        valid_email = email_info.email
        msg = EmailMessage(
            subject="Ваш код підтвердження",
            body=f"Ваш одноразовий код для входу: {otp_code}",
            from_email=app.config['MAIL_DEFAULT_SENDER'],
            to=[valid_email]
        )
        msg.send()
        session['begin_verification'] = True
    except EmailNotValidError as e:
        session['begin_verification'] = False
        session['email_not_exists'] = True
        return redirect('/signin')
    return redirect('/signin')

@app.route('/work_with_pin', methods=['POST'])
def work_with_pin():
    session['pin'] = request.form.get('pin')
    if session['pin'] == session['otp_code']:
        session['begin_verification'] = False
        session['amount_of_attemps'] = 5
        session['is_signed_in'] = True
        try:
            person = session['person']
            username = person['username']
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (session['username_value'], session['password_value'], session['email_value'],))
                connection.commit()
                session['begin_verification'] = False
                return redirect(url_for('search', formula=session['formula']))
        except sqlite3.IntegrityError:
            return redirect('/signin')
    else:
        session['amount_of_attemps'] -= 1
        if session['amount_of_attemps'] < 1:
            session['blocked_sign_in'] = True
            session['amount_of_attemps'] = 5
            return redirect(url_for('search', formula=session['formula']))
        return redirect('/signin')
    
@app.route('/unblock', methods=['POST']) 
def unblock_signin():
    session['blocked_sign_in'] = False
    return redirect(url_for('search', formula=session['formula']))

@app.route("/send_user", methods=['POST'])
def send_user():
    username = request.form.get("username", "").strip()
    username = username.replace(" ", "_")
    password = request.form.get("password", "").strip()
    password_2 = request.form.get("password_2", "").strip()
    email = request.form.get("email", "").strip()
    session['username_value'], session['password_value'] = username, password
    session['email_value'], session['password_2_value'] = email, password_2
    session['person'] = {'username': username, 'password': password, 'email':email}
    person = session['person']
    session['is_signed_in'] = False
    error_username = person["username"] == ""
    error_password = person["password"] == ""
    error_email = person["email"] == ""
    error_password_2 = password_2 == ""
    error_username_short = False
    error_password_short = False
    error_password_nsame = password != password_2
    session['email_not_exists'] = False
    if not person["username"] == "": error_username_short = len(person["username"]) < 6
    if not person["password"] == "": error_password_short = len(person["password"]) < 6
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        found = cursor.fetchone()
        if found:
            session['is_signed_in'] = True
            return redirect(url_for('search', formula=session['formula']))
    if error_username or \
        error_password or \
        error_username_short or \
        error_password_short or \
        error_password_nsame or \
        error_email or error_password_2:
        return render_template('signin.html',
        formula = session['formula'],
        begin_verification = session['begin_verification'],
        error_username_short = error_username_short,
        error_password_short = error_password_short,
        error_username=error_username,
        error_password=error_password,
        error_password_2=error_password_2,
        error_email=error_email,
        error_password_nsame = error_password_nsame,
        username_value=session['username_value'],
        password_value=session['password_value'],
        password_2_value=session['password_2_value'],
        email_value=session['email_value'],
        signed_in = session['is_signed_in'])
    else:
        return redirect('/send_pin')

@app.route("/login")
def login():
    session['show_profile_info'] = False
    return render_template('login.html',
    formula = session['formula'],
    username_value=session['username_value_login'],
    password_value=session['password_value_login'])

@app.route("/enter_user_login", methods=["POST"])
def enter_user_login():
    global admin_list
    username_login = request.form.get("username_login", "").strip()
    username_login = username_login.replace(" ", "_")
    password_login = request.form.get("password_login", "").strip()
    session['username_value_login'], session['password_value_login'] = username_login, password_login
    session['person_login'] = {'username_login': username_login, 'password_login': password_login}
    person_login = session['person_login']
    session['success_login'] = False
    session.permanent = True
    error_username_login = person_login["username_login"] == ""
    error_password_login = person_login["password_login"] == ""
    error_username_short_login = False
    error_password_short_login = False
    if not person_login["username_login"] == "": error_username_short_login = len(person_login["username_login"]) < 6
    if not person_login["password_login"] == "": error_password_short_login = len(person_login["password_login"]) < 6
    if error_username_login or \
        error_password_login or \
        error_username_short_login or \
        error_password_short_login:
        return render_template('login.html',
            formula = session['formula'],
            error_username_login_short = error_username_short_login,
            error_password_login_short = error_password_short_login,
            error_username_login=error_username_login,
            error_password_login=error_password_login,
            username_value_login=session.get('username_value_login', ''),
            password_value_login=session.get('password_value_login', ''),
            success_login=session['success_login'])
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (person_login['username_login'],))
        password_check = cursor.fetchone()
        success_login = False
        if password_check and password_check[0] == person_login['password_login']:
            success_login = True
        if success_login:
            session['admin'] = person_login['username_login'] in admin_list
            session['logined'] = True
            session['person'] = {'username': person_login['username_login']}
            session.modified = True
            return redirect("/")
        else:
            session['success_login'] = True
            session['person_login'] = {'username_login': "", 'password_login': ""}
            session['username_value_login'], session['password_value_login'] = "", ""
            return render_template('login.html',
                formula = session['formula'],
                error_username_login_short = error_username_short_login,
                error_password_login_short = error_password_short_login,
                error_username_login=error_username_login,
                error_password_login=error_password_login,
                username_value_login=session.get('username_value_login', ''),
                password_value_login=session.get('password_value_login', ''),
                success_login=session['success_login'])

@app.route("/show_answer", methods=['POST'])
def show_answer():
    session['show_answer'] = not session['show_answer']
    return jsonify({'status': 'ok', 'show_answer': session['show_answer']})

@app.route("/show_note", methods=['POST'])
def show_note():
    session['show_note'] = not session['show_note']
    return jsonify({'status': 'ok', 'show_note': session['show_note']})

@app.route("/switch_adm_mode_main")
def switch_admin_mode_main():
    if session['admin']: session['admin_mode'] = not session['admin_mode']
    return redirect(url_for('search', formula=session['formula']))

@app.route("/switch_adm_mode_tasks")
def switch_admin_mode_tasks():
    if session['admin']: session['admin_mode'] = not session['admin_mode']
    if session['task_id']: return redirect(url_for('task', task_id=session['task_id']))
    else: return redirect('/task')

@app.route('/update_description', methods=['POST'])
def update_description():
    the_formula = request.form['the_formula']
    correct_name = request.form['correct_name']
    common_name = request.form['common_name']
    solubility = request.form['solubility']
    smell = request.form['smell']
    chem_class = request.form['class']
    if not correct_name and not common_name and not solubility and not smell and not chem_class and not the_formula:
        flash("Ви не змінили жодні дані в описі!")
        return redirect(url_for('search', formula=session['formula']))
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE description SET correct_name = ?, common_name = ?, solubility = ?, smell = ?, class = ?, the_formula = ? WHERE formula = ?', 
        (correct_name, common_name, solubility, smell, chem_class, the_formula, session['formula']))
        cursor.execute('SELECT * FROM description WHERE formula = ?', (session['formula'],))
        new_info = cursor.fetchone()
        new_info = list(new_info)
        new_info[1] = cleaner(new_info[1])
        session['info'] = new_info
        connection.commit()
        return redirect(url_for('search', formula=session['formula']))

@app.route('/add_img', methods=["POST"])
def add_img():
    img = request.files['add_photo']
    photo = img.read()
    try:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM description WHERE formula = ?", (session['formula'],))
            info = list(cursor.fetchone())
            path = info[1]
        name = f'{session['formula']}_{session['num']}.jpg'
        full_path = os.path.join(path, name)
        with open(full_path, "wb") as f:
            f.write(photo.read() if hasattr(photo, 'read') else photo)
        cursor.execute("SELECT * FROM description WHERE formula = ?", (session['formula'],))
        information = cursor.fetchone()
        information = list(information)
        information[1] = cleaner(information[1])
        session['info'] = information
        return redirect(url_for('search', formula=session['formula']))
    except:
        flash("Виникла помилка при завантаженні зображення, повторіть спробу!")
        return redirect(url_for('search', formula=session['formula']))

@app.route('/upload_img', methods=["POST"])
def upload_img():
    img = request.files['upload_photo']
    try:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM description WHERE formula = ?", (session['formula'],))
            info = list(cursor.fetchone())
            path = info[1]
            file_count = len(os.listdir(path))
            name = f'{session['formula']}_{file_count}.jpg'
            path = os.path.join(path, name)
            img.save(path)
            information = list(info)
            information[1] = cleaner(information[1])
            session['info'] = information
            return redirect(url_for('search', formula=session['formula']))
    except:
        flash("Виникла помилка при завантаженні зображення, повторіть спробу!")
        return redirect(url_for('search', formula=session['formula']))
    
@app.route("/delete_img")
def delete_img():
    photos = session.get('info')
    try:
        path = photos[1][session['num']]
        photos[1][session['num']] = None
    except:
        flash("Зображення відсутнє!")
        return redirect(url_for('search', formula=session['formula']))
    if path:
        os.remove(path)
    else:
        flash("Зображення відсутнє!")
        return redirect(url_for('search', formula=session['formula']))
    return redirect(url_for('search', formula=session['formula']))

@app.route('/add_formula', methods=['POST'])
def add_formula():
    formula = request.form.get('formula')
    session['formula'] = formula
    change = False
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM description WHERE formula = ?", (session['formula'],))
        check_description = cursor.fetchone()
        if check_description is None:
            change = True
            cursor.execute("INSERT INTO description (formula, photo) VALUES (?, ?)", (session['formula'], f"static/images/{session['formula']}",))
        if not os.path.exists(f"static/images/{session['formula']}"):
            change = True
            path_main = f"static/images/{session['formula']}"
            os.makedirs(path_main, exist_ok=True)
        connection.commit()
        if change:
            return redirect(url_for('search', formula=session['formula']))
        else:
            flash("Формула вже є в БД!")
            return redirect(url_for('search', formula=session['formula']))
    
@app.route('/add_task_text', methods=['POST'])
def add_task_text():
    text = request.form.get("task_text")
    if not text:
        return "", 204
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO tasks (task, task_id) VALUES (?, COALESCE((SELECT MAX(task_id) FROM tasks), 0) + 1)", (text,))
            connection.commit()
            cursor.execute("SELECT task_id FROM tasks WHERE rowid = ?", (cursor.lastrowid,))
            task_id = cursor.fetchone()[0]
            session['task_id'] = task_id
            return redirect('/tasks')
    except:
        flash("Виникла помилка при завантаженні завдання, повторіть спробу!")
        return redirect('/tasks')
    
@app.route('/delete_task', methods=['POST'])
def delete_task():
    try:
        task_id = session['task_id']
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
            connection.commit()
            path = f"static/tasks/task_{task_id}.png"
            if os.path.exists(path):
                os.remove(path)
            cursor.execute("SELECT * FROM users")
            if cursor:
                task_id = str(task_id)
                for row in cursor:
                    username = row[1]
                    done_tasks = row[5]
                    revised_tasks = row[6]
                    changed = False
                    if done_tasks:
                        done_tasks = done_tasks.split()
                        if task_id in done_tasks:
                            done_tasks.remove(task_id)
                            changed = True
                        done_tasks = " ".join(done_tasks)
                    if revised_tasks:
                        revised_tasks = revised_tasks.split()
                        if task_id in revised_tasks:
                            revised_tasks.remove(task_id)
                            changed = True
                        revised_tasks = " ".join(revised_tasks)
                    if changed:
                        cursor.execute("UPDATE users SET done = ?, revised = ? WHERE username = ?", (done_tasks, revised_tasks, username,))
            connection.commit()
            session['task_id'] = None
            return redirect("/tasks")
    except:
        flash("Виникла помилка при видаленні завдання, повторіть спробу!")
        return redirect(url_for('task', task_id=session['task_id']))

@app.route('/delete_task_img')
def delete_task_img():
    path = f"static/tasks/task_{session['task_id']}.png"
    if os.path.exists(path):
        os.remove(path)
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE tasks SET photo = NULL WHERE task_id = ?', (session['task_id'],))
            connection.commit()
    return redirect("/tasks")

@app.route('/change_task_photo', methods=['POST'])
def change_task_photo():
    img = request.files['new_task']
    path = f"static/tasks/task_{session['task_id']}.png"
    try:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE tasks SET photo=? WHERE task_id = ?", (path, session['task_id'],))
            connection.commit()
            img.save(path)
            return redirect(url_for('task', task_id=session['task_id']))
    except:
        flash("Виникла помилка під час змінення фото, повторіть спробу!")
        return redirect(url_for('task', task_id=session['task_id']))

@app.route('/change_task_text', methods=["POST"])
def change_task_text():
    text = request.form.get('new_task_text')
    if not text:
        return "", 204
    try:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (session['task_id'],))
            task = cursor.fetchone()
            if task:
                if 'static/images/' in task[0]:
                    os.remove(task[0])
            cursor.execute("UPDATE tasks SET task=? WHERE task_id = ?", (text, session['task_id'],))
            connection.commit()
            return redirect(url_for('task', task_id=session['task_id']))
    except:
        flash("Виникла помилка під час змінення завдання, повторіть спробу!")
        return redirect(url_for('task', task_id=session['task_id']))

@app.route('/task', methods=['GET'])
def task():
    prev_id = session['task_id']
    task_id = request.args.get('task_id', session['task_id'])
    session['task_id'] = task_id
    if prev_id != task_id:
        session['show_answer'] = False
        session['show_note'] = False
    person = session['person_login']
    username = person['username_login']
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (session['task_id'],))
        searching = cursor.fetchone()
        if searching:
            task = searching[0]
            session['task_photo'] = searching[4]
            if searching[2]:
                session['note'] = searching[2]
                session['show_note_can'] = True
            else:
                session['note'] = "Немає пояснення до такого завдання!"
                session['show_note_can'] = False
            if searching[3]:
                session['answer'] = searching[3]
                session['show_answer_can'] = True
            else:
                session['answer'] = "Немає відповіді до такого завдання!"
                session['show_answer_can'] = False
        else:
            task = ''
            session['task_photo'] = None
            session['answer'] = "Немає відповіді до такого завдання!"
            session['show_answer_can'] = False
            session['note'] = "Немає пояснення до такого завдання!"
            session['show_note_can'] = False
        session['task'] = task
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        tasks_given = session['tasks_given']
        if not session['tasks_given'] and tasks:
            for task in tasks:
                tasks_given.append(str(task[1]))
            session['no_tasks'] = False
        elif not tasks:
            session['no_tasks'] = True
        session['tasks_given'] = tasks_given
        task_statuses = []
        tranzit_tasks_statuses = []
        for task in tasks_given:
            task_status = get_task_status(task, username)
            task_statuses.append(task_status)
            if str(task) in session['tasks_given_filtered']: tranzit_tasks_statuses.append(task_status)
        session['task_statuses'] = task_statuses
        session['task_statuses_filtered'] = tranzit_tasks_statuses
        if len(session['tasks_given_filtered']) > 10: session['can_scroll_tasks'] = True
        else: session['can_scroll_tasks'] = False
        if session['logined']: find_task_status()
        else: session['task_status'] = 'new'
        session['tags'] = get_tags()
        get_type_4_show()
        session['show_profile_info'] = False
        return render_template('tasks.html',
        formula = session['formula'],
        admin = session['admin'],
        person = session['person_login'],
        admin_mode = session['admin_mode'],
        task_id = session['task_id'],
        task=session['task'],
        photo = session['task_photo'],
        answer=session['answer'],
        note=session['note'],
        show_answer = session['show_answer'],
        show_note = session['show_note'],
        show_answer_can = session['show_answer_can'],
        show_note_can = session['show_note_can'],
        no_tasks = session['no_tasks'],
        tasks_given=session['tasks_given_filtered'][((session['tasks_list_amount']-1)*10):(session['tasks_list_amount']*10)],
        logined = session['logined'],
        task_status = session['task_status'],
        task_statuses = session['task_statuses_filtered'][((session['tasks_list_amount']-1)*10):(session['tasks_list_amount']*10)],
        task_statuses_4_search = session['selected_statuses_4_filters'],
        task_types_4_search = session['selected_types_4_filters'],
        searching_text = session['searching_text'],
        blocked_previous_tasks_list_button = session['blocked_previous_tasks_list_button'],
        blocked_next_tasks_list_button = session['blocked_next_tasks_list_button'],
        can_scroll_tasks = session['can_scroll_tasks'],
        tags = session['tags'],
        set_task_type_4_show = session['set_task_type_4_show'])

@app.route('/tasks')
def tasks():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        person = session['person_login']
        username = person['username_login']
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        tasks_given = session['tasks_given']
        if not session['tasks_given_filtered']: session['tasks_given_filtered'] = session['tasks_given']
        if not session['tasks_given'] and tasks:
            for task in tasks:
                tasks_given.append(str(task[1]))
            session['no_tasks'] = False
        elif not tasks:
            session['no_tasks'] = True
        session['tasks_given'] = tasks_given
        task_statuses = []
        tranzit_tasks_statuses = []
        for task in tasks_given:
            task_status = get_task_status(task, username)
            task_statuses.append(task_status)
            if str(task) in session['tasks_given_filtered']: tranzit_tasks_statuses.append(task_status)
        session['task_statuses'] = task_statuses
        session['task_statuses_filtered'] = tranzit_tasks_statuses
        if len(session['tasks_given_filtered']) > 10: session['can_scroll_tasks'] = True
        else: session['can_scroll_tasks'] = False
    session['show_profile_info'] = False
    return render_template('tasks.html',
    logined = session['logined'],
    admin = session['admin'],
    task_id = session['task_id'],
    person = session['person_login'],
    admin_mode = session['admin_mode'],
    no_tasks = session['no_tasks'],
    tasks_given=session['tasks_given_filtered'][((session['tasks_list_amount']-1)*10):(session['tasks_list_amount']*10)],
    task_statuses = session['task_statuses_filtered'][((session['tasks_list_amount']-1)*10):(session['tasks_list_amount']*10)],
    task_statuses_4_search = session['selected_statuses_4_filters'],
    task_types_4_search = session['selected_types_4_filters'],
    searching_text = session['searching_text'],
    blocked_previous_tasks_list_button = session['blocked_previous_tasks_list_button'],
    blocked_next_tasks_list_button = session['blocked_next_tasks_list_button'],
    can_scroll_tasks = session['can_scroll_tasks'],
    set_task_type_4_show = session['set_task_type_4_show'])

@app.route('/change_answer', methods=['POST'])
def change_answer():
    answer = request.form['change_answer']
    task_id = session['task_id']
    if not answer:
        flash('Ви не ввели відповідь!')
        return redirect(url_for('task', task_id=session['task_id']))
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE tasks SET answer = ? WHERE task_id=?', (answer, task_id,))
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        answer = cursor.fetchone()
        answer = answer[4]
        if answer:
            session['answer'] = answer
        else:
            session['answer'] = "Немає відповіді до такого завдання!"
        connection.commit()
        return redirect(url_for('task', task_id=session['task_id']))
    
@app.route('/change_note', methods=['POST'])
def change_note():
    note = request.form['change_note']
    task_id = session['task_id']
    if not note:
        flash("Ви не ввели пояснення!")
        return redirect(url_for('task', task_id=session['task_id']))
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE tasks SET note = ? WHERE task_id=?', (note, task_id,))
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        note = cursor.fetchone()
        note = note[3]
        if note:
            session['note'] = note
        else:
            session['note'] = "Немає пояснення до такого завдання!"
        connection.commit()
        return redirect(url_for('task', task_id=session['task_id']))

@app.route('/find_task', methods=["POST"])
def find_task():
    word = request.values.get("tags")
    session['searching_text'] = word
    all_ids = []
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tasks")
        if cursor:
            for row in cursor:
                current_tags = row[5]
                if current_tags:
                    this = find_tag(current_tags, word)
                    this = (row[1], this[1])
                    if this[1] > 0: all_ids.append(this)
    all_ids.sort(key=lambda x: x[1], reverse = True)
    if all_ids:
        tasks_given = []
        for task in all_ids: tasks_given.append(str(task[0]))
        session['tasks_given'], session['tasks_given_filtered'] = tasks_given, tasks_given
        session['no_tasks'] = False
    else:
        flash("Завдання не знайдено!")
        session['no_tasks'] = True
    session['tasks_list_amount'] = 1
    session['blocked_previous_tasks_list_button'] = True
    session['blocked_next_tasks_list_button'] = False
    return redirect("/tasks")

@app.route("/update_task_statuses", methods=["POST"])
def update_task_statuses():
    selected_statuses = request.form.getlist("statuses")
    session['selected_statuses_4_filters'] = selected_statuses
    return "", 204

@app.route("/update_task_types", methods=['POST'])
def update_task_types():
    selected_types = request.form.getlist("task_types")
    session['selected_types_4_filters'] = selected_types
    return "", 204

@app.route("/submit_filters")
def submit_filters():
    if session['logined']:
        tasks_given = session['tasks_given']
        statuses = session['selected_statuses_4_filters']
        types = session['selected_types_4_filters']
        task_statuses = session['task_statuses']
        new_tasks = []
        session['tasks_list_amount'] = 1
        session['blocked_previous_tasks_list_button'] = True
        session['blocked_next_tasks_list_button'] = False
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            for idx, task in enumerate(tasks_given):
                add_status, add_type = False, False
                cursor.execute("SELECT type FROM tasks WHERE task_id = ?", (task,))
                task_type = cursor.fetchone()
                print(task_type[0])
                if task_type[0] and task_type[0] in types or types == ['all_types']: add_type = True
                if task_statuses[idx] in statuses or statuses == ['all_statuses']: add_status = True
                if statuses and types and add_status and add_type: new_tasks.append(task)
        if new_tasks: session['tasks_given_filtered'] = new_tasks; session['no_tasks'] = False
        else:
            flash('Завдання за даними фільтрами не знайдено!')
            session['no_tasks'] = True
    return redirect("/tasks")
    
@app.route('/task_status', methods=['POST'])
def task_status():
    status = request.form.get("task_status", "new").strip()
    task_id = session['task_id']
    person = session['person_login']
    username = person['username_login']
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_info = cursor.fetchone()
        if user_info:
            done_tasks = user_info[5]
            revised_tasks = user_info[6]
            if done_tasks: done_tasks = done_tasks.split()
            else: done_tasks = []
            if revised_tasks: revised_tasks = revised_tasks.split()
            else: revised_tasks = []
            if status == 'new':
                if str(task_id) in done_tasks: done_tasks.remove(str(task_id))
                if str(task_id) in revised_tasks: revised_tasks.remove(str(task_id))
            elif status == 'done':
                if str(task_id) not in done_tasks: done_tasks.append(str(task_id))
                if str(task_id) in revised_tasks: revised_tasks.remove(str(task_id))
            elif status == 'in_progress':
                if str(task_id) not in revised_tasks: revised_tasks.append(str(task_id))
                if str(task_id) in done_tasks: done_tasks.remove(str(task_id))
            done_tasks = " ".join(done_tasks)
            revised_tasks = " ".join(revised_tasks)
            cursor.execute("UPDATE users SET done = ?, revised = ? WHERE username = ?", (done_tasks, revised_tasks, username,))
    return redirect(url_for('task', task_id=task_id))

@app.route("/reload_filters_2_scratch")
def reload_filters_2_scratch():
    session['selected_statuses_4_filters'] = ['all_statuses']
    session['selected_types_4_filters'] = ['all_types']
    session['tasks_given_filtered'] = session['tasks_given']
    session['task_statuses_filtered'] = session['task_statuses']
    session['tasks_list_amount'] = 1
    session['blocked_previous_tasks_list_button'] = True
    session['blocked_next_tasks_list_button'] = False
    session['searching_text'] = ""
    session['task_id'] = ''
    with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            tasks_given = []
            if tasks:
                for task in tasks:
                    tasks_given.append(str(task[1]))
                session['no_tasks'] = False
            elif not tasks:
                session['no_tasks'] = True
            session['tasks_given'], session['tasks_given_filtered'] = tasks_given, tasks_given
    return redirect('/tasks')

@app.route('/next_tasks_list')
def next_tasks_list():
    current_amount = session['tasks_list_amount']
    length = len(session['tasks_given_filtered'])
    session['blocked_next_tasks_list_button'] = False
    session['blocked_previous_tasks_list_button'] = False
    if length % 10 != 0: length = length//10 + 1
    else: length //= 10
    if current_amount + 1 <= length: current_amount += 1
    if current_amount >= length: session['blocked_next_tasks_list_button'] = True
    if current_amount <= 1: session['blocked_previous_tasks_list_button'] = True
    session['tasks_list_amount'] = current_amount
    if session['task_id']: return redirect(url_for('task', task_id = session['task_id']))
    else: return redirect('/tasks')

@app.route('/previous_tasks_list')
def previous_tasks_list():
    current_amount = session['tasks_list_amount']
    session['blocked_previous_tasks_list_button'] = False
    session['blocked_next_tasks_list_button'] = False
    length = len(session['tasks_given_filtered'])
    if length % 10 != 0: length = length//10 + 1
    else: length //= 10
    if current_amount - 1 >= 1: current_amount -= 1
    if current_amount <= 1: session['blocked_previous_tasks_list_button'] = True
    if current_amount + 1 > length: session['blocked_next_tasks_list_button'] = True
    session['tasks_list_amount'] = current_amount
    if session['task_id']: return redirect(url_for('task', task_id = session['task_id']))
    else: return redirect('/tasks')

@app.route('/set_task_class', methods=['POST'])
def set_task_class():
    task_id = session['task_id']
    selected = request.form.getlist("set_task_type")
    session['set_task_type_4_show'] = selected
    if selected:
        selected = selected[0]
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE tasks SET type = ? WHERE task_id = ?', (selected, task_id,))
            connection.commit()
    return redirect(url_for('task', task_id=session['task_id']))

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    person = session['person_login']
    username = person['username_login']
    done, revised = 0, 0
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT done, revised FROM users WHERE username = ?', (username,))
        tasks_info = cursor.fetchone()
        if tasks_info:
            if tasks_info[0]: done = len(tasks_info[0].split())
            if tasks_info[1]: revised = len(tasks_info[1].split())
        cursor.execute('SELECT * FROM tasks')
        all_tasks = len(cursor.fetchall())
        if all_tasks:
            session['person_tasks_info'] = {'done':round(done/all_tasks*100, 1), 'revised':round(revised/all_tasks*100, 1), 'done_amount':int(done), 'revised_amount':int(revised), 'new_amount':int(all_tasks-(done+revised))}
        session['show_profile_info'] = True
    if session['formula']: return redirect(url_for('search', formula=session['formula']))
    else: return redirect('/search')

@app.route('/close_profile', methods=['POST', 'GET'])
def close_profile():
    session['show_profile_info'] = False
    if session['formula']: return redirect(url_for('search', formula=session['formula']))
    else: return redirect('/search')

@app.route('/change_password', methods=['POST'])
def change_password():
    session['changing_password_way'] = 'password'
    return render_template('change_password.html', changing_password_way = session['changing_password_way'])

@app.route('/work_with_new_password', methods=['POST', 'GET'])
def work_with_new_password():
    newpass = request.form.get('new_password', '')
    session['changing_password_way'] = 'password'
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        password = request.form.get('old_password', '')
        cursor.execute('SELECT password FROM users WHERE password = ?', (password,))
        checkpass = cursor.fetchone()
        if checkpass and checkpass[0] and checkpass[0] == password:
            cursor.execute('UPDATE users SET password = ? WHERE password = ?', (newpass, password,))
            connection.commit()
            return redirect('/')
        else:
            old_password_error = 'Поточний пароль введено неправильно!'
            if not newpass: new_password_error = 'Новий пароль введено некоректно! Перевірте чи він містить мінімум 6 символів!'
            else: new_password_error = ""
            return render_template('change_password.html',
            changing_password_way = session['changing_password_way'],
            new_password_error = new_password_error,
            old_password_error = old_password_error,
            newpass = newpass)

@app.route('/choose_email_password_change', methods=['POST'])
def choose_email_password_change():
    session['changing_password_way'] = 'email'
    session['send_pin'] = False
    person = session['person_login']
    username = person['username_login']
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM users WHERE username = ?', (username,))
        work_email = cursor.fetchone()
        if work_email and work_email[0]:
            if not session['send_pin']:
                email = work_email[0]
                otp_code = str(random.randint(100000, 999999))
                session['otp_code'] = otp_code
                try:
                    email_info = validate_email(email, check_deliverability=True)
                    valid_email = email_info.email
                    msg = EmailMessage(
                        subject="Ваш код підтвердження",
                        body=f"Ваш одноразовий код для підтвердження акаунту: {otp_code}",
                        from_email=app.config['MAIL_DEFAULT_SENDER'],
                        to=[valid_email]
                    )
                    msg.send()
                    session['amount_of_changing_attemps'] = 3
                    session['send_info'] = True
                except EmailNotValidError as e:
                    session['send_pin'] = False
                    flash('Виникла помилка при зміні паролю за email!')
                    return redirect('/')
            email = work_email[0]
            idx = email.index('@')
            part = email[:idx]
            if len(part) < 5:
                part = part[0] + ("*" * (len(part) - 2)) + part[-1]
            else:
                part = part[:2] + ("*" * (len(part) - 4)) + part[-2:]
            email = part + email[idx:]
        else:
            email = ''
        session['your_email'] = email
    return render_template('change_password.html', changing_password_way = session['changing_password_way'], your_email = session['your_email'], amount_of_changing_attemps = session['amount_of_changing_attemps'])

@app.route('/work_with_changing_password_by_email_pin', methods=['POST'])
def work_with_changing_password_by_email_pin():
    session['changing_password_way'] = 'email'
    pin = request.form.get('pin', '')
    person = session['person_login']
    username = person['username_login']
    if pin == session['otp_code']:
        session['changing_password_way'] = 'confirm_password'
        return redirect('/confirm_password')
    else:
        session['amount_of_changing_attemps'] -= 1
        if session['amount_of_changing_attemps'] < 1:
            session['amount_of_changing_attemps'] = 3
            send_new_pin = "Ви використали 3 спроби! Вам надіслано новий код!"
            with sqlite3.connect('database.db') as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT email FROM users WHERE username = ?', (username,))
                email = cursor.fetchone()
                if email and email[0]: email = email[0]
                else:
                    flash('Виникла помилка при повторному надсиланні коду!')
                    return redirect('/')
            otp_code = str(random.randint(100000, 999999))
            session['otp_code'] = otp_code
            try:
                email_info = validate_email(email, check_deliverability=True)
                valid_email = email_info.email
                msg = EmailMessage(
                    subject="Ваш код підтвердження",
                    body=f"Ваш одноразовий код для підтвердження акаунту: {otp_code}",
                    from_email=app.config['MAIL_DEFAULT_SENDER'],
                    to=[valid_email]
                )
                msg.send()
                session['amount_of_changing_attemps'] = 3
                session['send_info'] = True
            except EmailNotValidError as e:
                session['send_pin'] = False
                flash('Виникла помилка при зміні паролю за email!')
                return redirect('/')
        else:
            send_new_pin = ""
        return render_template('change_password.html',
        changing_password_way = session['changing_password_way'],
        amount_of_changing_attemps = session['amount_of_changing_attemps'],
        error_not_same_pin = 'Код неправильний!',
        got_pin = pin,
        your_email = session['your_email'],
        send_new_pin = send_new_pin)

@app.route('/confirm_password', methods=['POST', 'GET'])
def confirm_password():
    password = request.form.get('final_password', '')
    person = session['person_login']
    username = person['username_login']
    if password:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (password, username,))
            connection.commit()
            return redirect('/')
    else:
        return render_template('change_password.html', changing_password_way = session['changing_password_way'], error_password_empty = 'Введіть пароль!')

@app.route('/show_users_list_for_admin', methods=['POST', 'GET'])
def show_users_list_for_admin():
    session['can_show_users_list'] = not session['can_show_users_list']
    if session['can_show_users_list']:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username, status FROM users')
            users = list(cursor.fetchall())
            for idx, current in enumerate(users):
                if current[1] == 'admin':
                    del users[idx]
                    break
    else:
        users = [['Nobody more(', 'none']]
    session['all_found_users_list'] = users
    return redirect('/profile')

@app.route('/add_tags', methods=['POST', 'GET'])
def add_tags():
    tags = request.form['some_tags']
    tags_list = []
    prev = 0
    for i in range(len(tags)):
        if tags[i] == ',':
            tags_list.append(tags[prev:i].strip().replace(' ', "_"))
            prev = i + 2
        elif i == len(tags) - 1:
            tags_list.append(tags[prev:].strip().replace(' ', "_"))
    tags = " ".join(tags_list)
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE tasks SET tags = ? WHERE task_id = ?', (tags, session['task_id'],))
    return redirect(url_for('task', task_id=session['task_id']))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
