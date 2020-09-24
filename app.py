from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
from auth import AuthError, requires_auth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:telefon095@localhost:5432/capstone'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
CORS(app)

migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    events_i_attend = db.Column(db.String(5000), default='0')
    
    

    def __init__(self, email,password, active, events_i_attend):
        self.email = email
        self.password = password
        self.active = active
        self.events_i_attend = events_i_attend

    def format(self):
        return {
          'id': self.id,
          'email': self.email,
          'password': self.password,
          'active': self.active,
          'events_i_attend': self.events_i_attend}


class Race(db.Model):
    __tablename__ = 'races'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, default=1)
    participating_users = db.Column(db.Integer, nullable=True, default=1)
    racers_id = db.Column(db.String(500), nullable=True)
    users_id = db.Column(db.String(500), nullable=True)
    # date = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    def __init__(self, name, category, city, duration, participating_users, racers_id):
        self.name = name
        self.category = category
        self.city = city
        self.duration = duration
        self.participating_users = participating_users
        self.racers_id = racers_id

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'category': self.category,
          'city': self.city,
          'duration': self.duration,
          'participating_users': self.participating_users,
          'racers_id': self.racers_id }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Racer(db.Model):
    __tablename__ = 'racers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    car = db.Column(db.String(50), nullable=False)
    power = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    race_i_attend = db.Column(db.String(5000), default='0')


    def delete2(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def insert(self):
        db.session.add(self)
        db.session.commit()

db.create_all()

@app.route('/create_user', methods=['POST'])
def create_user():
    
    emailR = request.get_json()['email'] 
    phoneR = request.get_json()['phone'] 
    passwordR = request.get_json()['password'] 
    print(emailR)

    Nremail = User.query.filter(User.email.ilike(emailR)).all()
    print(len(Nremail))
    if len(Nremail) == 0:
        data = User(
        email=emailR,
        password=passwordR,
        active=True,
        events_i_attend = '0,'
        )
        db.session.add(data)
        db.session.commit()

        new_user_select = User.query.filter(User.email.ilike(emailR)).all()
        particular_email = {}
        particular_id = {}
        for user in new_user_select:
            particular_email[user.id] = user.email
            particular_id[user.id] = user.id

        return jsonify({
            'description': 'Your account has been successfully created! In a few seconds you will be redirected to the login page.',
            'id': particular_id[user.id],
            'email': particular_email[user.id],
            'redirect': True,
        })
    else:
        return jsonify({
            'description': 'Email address already exists!',
            'redirect': False
        })



    
@app.route('/racesUSer', methods=['POST'])
def racesUSer():

    emailR = request.get_json()['email'] 
    passwordR = request.get_json()['password'] 
    select_user = User.query.filter(User.email.ilike(emailR)).all()

    if(len(select_user) > 0):
        particular_email = {}
        particular_id = {}
        particular_password = {}
        for user in select_user:
            particular_email[user.id] = user.email
            particular_id[user.id] = user.id
            particular_password[user.id] = user.password

        if(emailR == particular_email[user.id] and passwordR == particular_password[user.id]):
            return jsonify({
                'success': True,
                'description': 'You will be redirected to the login page.',
                'id': particular_id[user.id],
                'email': particular_email[user.id],
                'redirect': True  
            })
        else:
            return jsonify({
                'success': False,
                'description': 'Incorrect username or password!',
                'redirect': False  
            })
    else:
        return jsonify({
            'success': False,
            'description': 'Incorrect username or password!',
            'redirect': False  
        })



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/show_races/<int:id>')
def show_races(id):
    select_user = User.query.filter(User.id==id).all()
    if(len(select_user) > 0):
        particular_active = {}
        events_i_attend = []
        for user in select_user:
            particular_active[user.id] = user.active
            events_i_attend = list(user.events_i_attend.split(","))

        if(particular_active[user.id] == False):
            return  render_template('index.html', data='You are not authorized to access this page. Please log in with valid data!')
        else:
            data_races = []
            races_select = Race.query.all()
            for race in races_select:
                v = {}
                v['id'] = race.id
                v['name'] = race.name
                v['category'] = race.category
                v['city'] = race.city
                v['duration'] = race.duration
                v['user_id'] = id
                data_races.append(v)


            print(races_select)
            return render_template('show_races.html',  races=data_races)
    else:
        return  render_template('index.html', data='You are not authorized to access this page. Please log in with valid data!')
        
@app.route('/show_races/<int:id_user>/join/<int:id_join>',  methods=['POST'])
def join_races(id_user, id_join):
    # # update number of participants + update for the races in which curent user participate
    # race_selected = Race.query.filter(Race.id == id_join).all()
    # user = User.query.filter(User.id == id_user).all()

    # race_selected[0].participating_users =  race_selected[0].participating_users + 1
    # user[0].events_i_attend = user[0].events_i_attend + str(id_join) + ','
    # db.session.commit()
    #     #     db.session.commit()
    #     # except:
    #     #     abort(400)

    # # return data_races[0].participating_users
    # return jsonify({
    #     'success': True,
    #     'user_id': id_user,
    #     'race_id': id_join
    # })

    body = request.get_json()

    race_id = body.get('race_id', '')
    user_id = body.get('user_id', '')

    select_race = Race.query.filter(Race.id == int(id_join)).one_or_none()
    user = User.query.filter(User.id == user_id).all()

    if (select_race.users_id == None):
        select_race.users_id = ''

    list_curent_users = list(select_race.users_id.split(",")) 
    list_curent_users = list_curent_users[:-1]    # remove last item ..is empty
    number_participanti =  select_race.participating_users + 1

    exist = False
    for d in list_curent_users:
        if d == user_id:
            exist = True


    if(exist == False):
        join_to_all = select_race.users_id + user_id + ','

        try:
            select_race.users_id = join_to_all
            select_race.participating_users = number_participanti

            select_race.update()

            descriere = 'You have successfully registered for this event!'

            return jsonify({
                'success': True,
                'description': descriere
            }), 200

        except:
            return jsonify({
                'success': False,
                'description': ''
            }), 422
    else:
        return jsonify({
            'success': False,
            'description': 'You are already registered for this event!'
        }), 422


# ---------------------------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ADMIN FOR RACES <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# ---------------------------------------------------------------------------------------------


@app.route('/adminRaces/')
# @requires_auth('get:races')
def admin_races():

    data_races = []
    races_select = Race.query.all()
    for race in races_select:
        v = {}
        v['id'] = race.id
        v['name'] = race.name
        v['category'] = race.category
        v['city'] = race.city
        v['duration'] = race.duration
        v['participating_users'] = race.participating_users
        data_races.append(v)


    return render_template('adminRaces.html',  races=data_races)


@app.route('/adminRaces/<int:id>/delete', methods=['DELETE'])
@requires_auth('delete:races')
def admin_races_delete(paylaod, id):

    print(paylaod)


    race = Race.query.filter(Race.id == id).one_or_none()    

    try:
        race.delete()  
        return jsonify({
            'success': True, 
            'delete': race.id
        }), 200
    except:
        return jsonify({
            'success': False,
            'paylaod': paylaod
        }), 422


@app.route('/adminRaces/<int:id>/update', methods=['PATCH'])
@requires_auth('patch:races')
def admin_races_update(payload, id):
    body = request.get_json()
    
    race = Race.query.filter(Race.id == id).one_or_none()

    name = body.get('name', '')
    category = body.get('category', '')
    city = body.get('city', '')
    duration = body.get('duration', '')

    if(name == '' or city == ''):
        return jsonify({
            'success': False,
            'description': 'You must fill all fields!'
            }), 422 
    else:
        try:
            race.name = name
            race.category = category
            race.city = city
            race.duration = duration

            race.update()

            return jsonify({
                'success': True,
                'description': ''
            }), 200

        except:
            return jsonify({
                'success': False,
                'description': ''
            }), 422


@app.route('/adminRaces/post', methods=['POST'])
@requires_auth('post:races')
def admin_races_post(payload):
    body = request.get_json()

    name = request.get_json()['name']
    category = request.get_json()['category']
    city = request.get_json()['city']
    duration = request.get_json()['duration']
    participating_users = 0 
    racers_id = ''

    if(name == '' or city == ''):
        return jsonify({
            'success': False,
            'description': 'You must fill in the "Name" and "City" fields!'
            }), 422
        

    try:
        new_race = Race(name=name, category=category, city=city, duration=duration, participating_users=participating_users, racers_id=racers_id)
        new_race.insert()

        races_select = Race.query.order_by(desc(Race.id)).first()
        id = races_select.id

        return jsonify({
            'success': True,
            'id': id
            }), 200

    except:
        jsonify({
            'success': False,
            'description': ''
            }), 422

# ---------------------------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ADMIN FOR RACERS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# ---------------------------------------------------------------------------------------------

@app.route('/adminRacers/')
def admin_racers():

    data_races =[]
    races_select = Race.query.all()
    for race in races_select:
        v = {}
        v['id'] = race.id
        v['name'] = race.name
        data_races.append(v)


    data_racers = []
    racers_select = Racer.query.all()
    if len(racers_select) <= 0:
        v = {}
        v['id'] = 'id'
        v['name'] = ''
        v['category'] = ''
        v['city'] = ''
        v['car'] = ''
        v['power'] = ''
        v['active'] = ''
        v['race_i_attend'] = ''
        v['race_details'] = data_races
        v['ascunde'] = 'none'
        data_racers.append(v)

        return render_template('adminRacers.html', racers=data_racers)
    else:
        for racer in racers_select:
            v = {}
            v['id'] = racer.id
            v['name'] = racer.name
            v['category'] = racer.category
            v['city'] = racer.city
            v['car'] = racer.car
            v['power'] = racer.power
            v['active'] = racer.active
            v['race_i_attend'] = racer.race_i_attend
            v['race_details'] = data_races
            v['ascunde'] = 'nu'
            data_racers.append(v)

        return render_template('adminRacers.html',  racers=data_racers)


@app.route('/adminRacers/post', methods=['POST'])
@requires_auth('post:users')
def admin_racers_post(payload):
    body = request.get_json()

    name = request.get_json()['name']
    category = request.get_json()['category']
    city = request.get_json()['city']
    car = request.get_json()['car']
    power = request.get_json()['power']
    active = True 
    race_i_attend = ''

    if(name == '' or city == '' or car == '' or power == ''):
        return jsonify({
            'success': False,
            'description': 'You must fill all fields!'
            }), 422
        

    try:
        new_racer = Racer(name=name, category=category, city=city, car=car, power=power, active=active, race_i_attend=race_i_attend)
        new_racer.insert()

        racers_select = Racer.query.order_by(desc(Racer.id)).first()
        id = racers_select.id

        return jsonify({
            'success': True,
            'id': id
            }), 200

    except:
        jsonify({
            'success': False,
            'description': ''
            }), 422


@app.route('/adminRacers/<int:id>/delete', methods=['DELETE'])
@requires_auth('delete:users')
def admin_racers_delete(payload, id):

    racer = Racer.query.filter(Racer.id == id).one_or_none()    

    try:
        racer.delete2()  
        return jsonify({
            'success': True, 
            'delete': racer.id
        }), 200
    except:
        return jsonify({
            'success': False
        }), 422


@app.route('/adminRacers/<int:id>/update', methods=['PATCH'])
@requires_auth('patch:users')
def admin_racers_update(payload, id):
    body = request.get_json()
    
    racer = Racer.query.filter(Racer.id == id).one_or_none()

    name = body.get('name', '')
    category = body.get('category', '')
    city = body.get('city', '')
    car = body.get('car', '')
    power = body.get('power', '')

    if(name == '' or city == '' or car == '' or power == ''):
        return jsonify({
            'success': False,
            'description': 'You must fill all fields!'
            }), 422 
    else:
        try:
            racer.name = name
            racer.category = category
            racer.city = city
            racer.car = car
            racer.power = power

            racer.update()

            return jsonify({
                'success': True
            }), 200

        except:
            return jsonify({
                'success': False
            }), 422


@app.route('/adminRacers/join', methods=['PATCH'])
@requires_auth('patch:users')
def admin_racers_join_update(paylaod):
    body = request.get_json()

    race_id = body.get('race_id', '')
    user_id = body.get('user_id', '')

    select_race = Race.query.filter(Race.id == int(race_id)).one_or_none()
    if (select_race.racers_id == None):
        select_race.racers_id = ''

    list_curent_users = list(select_race.racers_id.split(",")) 
    list_curent_users = list_curent_users[:-1]    # remove last item ..is empty

    exist = False
    for d in list_curent_users:
        if d == user_id:
            exist = True


    if(exist == False):
        join_to_all = select_race.racers_id + user_id + ','
        try:
            select_race.racers_id = join_to_all

            select_race.update()

            descriere = 'Utilizatorul ' + select_race.name + ' was successfully registered in this race!'

            return jsonify({
                'success': True,
                'description': descriere
            }), 200

        except:
            return jsonify({
                'success': False,
                'description': ''
            }), 422
    else:
        return jsonify({
            'success': False,
            'description': 'This user is already registered in this race!'
        }), 422
