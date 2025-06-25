import os
from flask import render_template, request, redirect, url_for, jsonify, flash, send_file, make_response
from . import db
from .models import User, Client, Event
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

def init_routes(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        return render_template('index.html', current="index")
    
    @app.route('/users')
    @login_required
    def users():
        users = User.query.all()
        return render_template('users.html', current="users", users=users)

    @app.route('/user/add', methods=["GET", "POST"])
    @login_required
    def user_add():
        if request.method == "GET":
            return render_template('user/add.html', current="users")
        if request.method == "POST":
            user = User()
            user.username = request.form["username"]
            user.telegram_id = request.form["telegram_id"]
            user.password = request.form["password"]
            db.session.add(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/user/edit/<id>', methods=["GET", "POST"])
    @login_required
    def user_edit(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/edit.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            user.username = request.form["username"]
            user.password = request.form["password"]
            user.telegram_id = request.form["telegram_id"]
            db.session.commit()
            return redirect("/users")

    @app.route('/user/del/<id>', methods=["GET", "POST"])
    @login_required
    def user_del(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/del.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            db.session.delete(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/clients')
    @login_required
    def clients():
        clients = Client.query.all()
        return render_template('clients.html', current="clients", clients=clients)

    @app.route('/client/add', methods=["GET", "POST"])
    @login_required
    def client_add():
        if request.method == "GET":
            return render_template('client/add.html', current="clients")
        if request.method == "POST":
            client = Client()
            client.first_name = request.form["first-name"]
            client.last_name = request.form["last-name"]
            client.patronymic = request.form["patronymic"]
            client.group = request.form["account_number"]
            db.session.add(client)
            db.session.commit()
            return redirect("/clients")

    @app.route('/client/edit/<id>', methods=["GET", "POST"])
    @login_required
    def client_edit(id):
        if request.method == "GET":
            client = db.get_or_404(Client, id)
            return render_template('client/edit.html', current="clients", client=client)
        if request.method == "POST":
            client = db.get_or_404(Client, request.form["id"])
            client.first_name = request.form["first-name"]
            client.last_name = request.form["last-name"]
            client.patronymic = request.form["patronymic"]
            client.account_number = request.form["account_number"]
            db.session.commit()
            return redirect("/clients")

    @app.route('/client/del/<id>', methods=["GET", "POST"])
    @login_required
    def client_del(id):
        if request.method == "GET":
            client = db.get_or_404(Client, id)
            return render_template('client/del.html', current="clients", client=client)
        if request.method == "POST":
            client = db.get_or_404(client, request.form["id"])
            db.session.delete(client)
            db.session.commit()
            return redirect("/clients")
    
    @app.route('/client/photo-edit/<id>', methods=["GET", "POST"])
    def client_photo_edit(id):
        if request.method == "GET":
            client = db.get_or_404(Client, id)
            return render_template('client/add_photo.html', current="clients", client=client)
        if request.method == "POST":
            # Проверяем, есть ли файл в запросе
            if 'photo' not in request.files:
                flash('No file part')
                return redirect("/clients")
        
            file = request.files['photo']
        
            # Если пользователь не выбрал файл
            if file.filename == '':
                flash('No selected file')
                return redirect("/clients")
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jpg"}
            
            # Если файл разрешен и корректен
            if file and allowed_file(file.filename):
                if not os.path.exists(app.config['IMGS']):
                    os.makedirs(app.config['IMGS'])
                file.save(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")))
                return redirect("/clients")
    
        return redirect("/clients")

    @app.route('/client/photo/<id>', methods=["GET", "POST"])
    def client_photo(id):
        if request.method == "GET":
            client = db.get_or_404(Client, id)
            if os.path.isfile(os.path.join(app.config['IMGS'], f"{id}.jpg")):
                return send_file(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")), as_attachment=True)
            else:
                return make_response(f"File '{id}' not found.", 404)
    
    @app.route('/clients/json')
    def clients_all():
        clients = Client.query.all()
        result = []
        for client in clients:
            client_dict = client.__dict__
            client_dict.pop('_sa_instance_state', None)  # Удаляем служебное поле SQLAlchemy
            result.append(client_dict)
        return jsonify(result)

    @app.route('/events')
    @login_required
    def events():
        events = Event.query.all()
        
        return render_template('events.html', current="events", events=events)

    def send_event_telegram(event):

        users = User.query.all()
        msg = f"{event.name}\n{event.description}"
        url = f"http://{app.config['TELEGRAM_URL']}/send_notification"
        headers = {"X-API-KEY": app.config['TELEGRAM_API_KEY']}
        for user in users:
            if user.telegram_id == None : continue
            data = {
                "user_id": user.telegram_id,  # ID пользователя из Telegram
                "message": msg
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                if response.status_code != 200:
                    print(f"Ошибка отправки сообщения {data}")
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка подключения к Telegram Bot")

    @app.route('/event/add', methods=["GET", "POST"])
    def event_add():
        if request.method == "POST":
            event = Event()
            event.name = request.json["name"]
            event.description = request.json["description"]
            db.session.add(event)
            db.session.commit()
            send_event_telegram(event)
            return make_response("", 200)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
    
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            print(username)
            print(password)
            user = User.query.filter_by(username=username, password=password).first()
            print(user)
            if user:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/")
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
    
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")