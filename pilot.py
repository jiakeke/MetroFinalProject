"""%(program)s:  Pilot Game Center

usage:  python %(program)s command

Common Commands:

    help          -- print this help text
    run           -- run the API server
    initdb        -- database initialization
    dumpdb        -- database dump
"""


import os, sys
import datetime
from flask import Flask, request, jsonify
from flask import render_template
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from flask_bcrypt import Bcrypt
from mysql import connector

from models import Airport, Country, Plane, User

import config


program = os.path.basename(sys.argv[0])


app = Flask(__name__)

#========================= Flask API View  ==================================


@app.route("/airport/<id>")
def airport(icao):
    airports = Airport.objects.random(continent='EU', limit=2)
    if len(airports) > 0:
        context = {
            'ICAO': icao,
            'Name': airports[0]['name'],
            'Location':airports[0]['municipality']
        }
        return context
    return {'ICAO': icao, 'Status': 'Not Found'}


@app.route('/')
def index():
    return render_template('index.html')

#-------------------------- Auth API ------------------------------------

app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/register', methods=["POST"])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not (username and password):
        return {"msg": "Please input both name and password"}, 400

    exist_users = User.objects.filter(name=username)
    if len(exist_users) > 0:
        return {"msg": "The username you entered already exists."}, 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User.objects.create(name=username, password=hashed_password)

    access_token = create_access_token(identity=username)
    response = {"access_token":access_token}
    return response

@app.route('/login', methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    exist_users = User.objects.filter(name=username)
    if len(exist_users) <= 0:
        return {"msg": "The username is not exist."}, 401

    user = exist_users[0]

    print(password, user.password)
    is_valid = bcrypt.check_password_hash(user.password, password)
    if not is_valid:
        return {"msg": "Wrong username or password."}, 401

    access_token = create_access_token(identity=username)
    response = {"access_token":access_token}
    return response

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/authinfo')
@jwt_required()
def my_profile():
    response_body = {
        "name": "Nagato",
        "about" :"Hello! I'm a full stack developer that loves python and javascript"
    }

    return response_body

#------------------------- Pages --------------------------------------------
@app.route('/pages/login')
def login_form():
    return render_template('login_form.html')

#========================= Programming Control ==============================

def run_command(cmd):
    print(cmd)
    os.system(cmd)


def main():
    if len(sys.argv) == 1:
        run()
    cmd = sys.argv[1]
    if cmd in cmds_map:
        method = cmds_map[cmd]
        method()
    else:
        run()

def run():
    app.run(
        use_reloader=config.reloader_mode,
        debug=config.debug,
        host=config.site_host,
        port=config.site_port)


def usage():
    print(__doc__ % {"program": program})


def initdb():
    run_command(
        f'mysql -u{config.db_user} -p{config.db_pass} '
        f'-e "DROP DATABASE IF EXISTS {config.db_name}"')

    run_command(
        f'mysql -u{config.db_user} -p{config.db_pass} '
        f'-e "CREATE DATABASE IF NOT EXISTS {config.db_name}"')

    if os.path.exists('database.sql'):
        run_command(
            f'mysql -u{config.db_user} -p{config.db_pass} '
            f'{config.db_name} < database.sql')

    if os.path.exists('update.sql'):
        run_command(
            f'mysql -u{config.db_user} -p{config.db_pass} '
            f'{config.db_name} < update.sql')


def dumpdb():
    dt = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    run_command(
        f'mysqldump -u{config.db_user} -p{config.db_pass} '
        f'{config.db_name} > database_{dt}.sql')


cmds_map = {
    'help': usage,
    'initdb': initdb,
    'dumpdb': dumpdb,
}

if __name__ == '__main__':
    main()

