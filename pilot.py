"""%(program)s:  Pilot Game Center

usage:  python %(program)s command

Common Commands:

    help          -- print this help text
    run           -- run the API server
    initdb        -- database initialization
    dumpdb        -- database dump
"""


import os, sys
import json
import math
import random
from datetime import datetime, timezone, timedelta
from geopy.distance import geodesic
from flask import Flask, request, jsonify
from flask import render_template
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_bcrypt import Bcrypt
from mysql import connector

from models import Airport, Country, Plane, User, Task, User_X_Plane

import config


program = os.path.basename(sys.argv[0])


app = Flask(__name__)

#========================= Common Misc Functions ==========================

def get_weather_index(latitude):
    weather_setting = {
        1: ('Normal', 1.0),
        2: ('Great', 0.9),
        3: ('Heavy Rain', 1.1),
        4: ('Blizzard', 1.3),
        5: ('Snow', 1.2),
        6: ('Thunderstorm', 1.2)
    }
    if latitude == "tutorial":
        return weather_setting[1]
    weather_index = weather_setting[1]
    if random.random() <= 0.20:
        weather_index = weather_setting[2]
    elif random.random() >= 0.80:
        weather_index = weather_setting[3]
    elif latitude >= 60 and random.random() <= 0.05:
        weather_index = weather_setting[4]
    elif latitude >= 40 and random.random() <= 0.10:
        weather_index = weather_setting[5]
    elif latitude <= 30 and random.random() <= 0.15:
        weather_index = weather_setting[6]
    return weather_index


def calculate_carbon_emission(distance):
    """
    Calculate the carbon emission based on the given distance.
    """
    if distance <= 200:
        return distance * 0.275
    elif 200 < distance <= 1000:
        return 55 + 0.105 * (distance - 200)
    else:
        return distance * 0.139

def calculate_flight_reward(distance):
    """
    Calculate the reward based on the given distance.
    """
    emission = calculate_carbon_emission(distance)

    carbon_cost = emission * 1.3
    fuel_cost = distance * 2.5
    total_cost = carbon_cost + fuel_cost
    reward = (int(total_cost) + 500) * random.randint(90, 120) / 100
    return reward

def get_map(task):
    ax = task.departure.longitude_deg
    ay = task.departure.latitude_deg
    a_txt = 'A'

    bx = task.destination.longitude_deg
    by = task.destination.latitude_deg
    b_txt = 'B'

    cx = (ax + bx)/2
    cy = (ay + by)/2


    distance = geodesic(
        (ay, ax),
        (by, bx)
    ).kilometers

    zoom = 14.5 - math.log(distance, 2)

    px_x = (360 / (2 ** (zoom - 1))) / 1024
    px_y = (math.pi / (2 ** (zoom - 1))) / 768

    url =(
        f"https://maps.geoapify.com/v1/staticmap"
        f"?apiKey={config.map_api_key}"
        f"&style=klokantech-basic&width=1024&height=768"
        f"&center=lonlat:{cx},{cy}&zoom={zoom}"
        f"&marker="
        f"lonlat:{ax},{ay};text:{a_txt};"
        f"color:%23ff0000;size:large;textsize:small|"
        f"lonlat:{bx},{by};text:{b_txt};"
        f"color:%23ff0000;size:large;textsize:small"
    )

    ay = math.radians(ay)
    by = math.radians(by)
    cy = math.radians(cy)

    ax_px = round((ax - cx)/px_x + 512)
    ay_px = round((cy - ay)/px_y + 384)

    bx_px = round((bx - cx)/px_x + 512)
    by_px = round((cy - by)/px_y + 384)

    print(ax_px, bx_px)
    return url, (ax_px, ay_px), (bx_px, by_px)

#========================= Flask API View  ==================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/game")
@jwt_required()
def game():
    user = User.objects.get(name=get_jwt_identity())
    task = user.current_task
    context = {
        'task': task.Json,
        'map_info': get_map(task),
        'planes': [plane.plane.Json for plane in user.planes],
    }

    return context


@app.route("/game/play", methods=['POST'])
@jwt_required()
def game_play():
    user = User.objects.get(name=get_jwt_identity())
    plane_id = request.json.get("plane", None)
    task = user.current_task
    plane = Plane.objects.get(id=plane_id)
    context = {
        'task': task.Json,
        'plane': plane.Json,
        'map_info': get_map(task),
        'report': task.play(plane),
    }
    print(context['report'])

    return context

@app.route("/store")
@jwt_required()
def store():
    user = User.objects.get(name=get_jwt_identity())
    planes = Plane.objects.filter()
    user_data = {
        "id": user.id,
        "name": user.name,
        "balance": user.balance
    }
    planes_data = [plane.Json for plane in planes]
    return {"user": user_data, "planes": planes_data}

@app.route("/store/buy/<plane_id>", methods=["POST"])
@jwt_required()
def buy_plane(plane_id):
    user = User.objects.get(name=get_jwt_identity())
    plane = Plane.objects.get(id=plane_id)

    if len(User_X_Plane.objects.filter(user_id=user.id, aircraft_id=plane.id)) > 0:
        return {"status": "failure", "message": "You already own this plane."}

    if user.balance >= plane.price:
        user.balance -= plane.price
        User.objects.update(user.id, balance=user.balance)

        User_X_Plane.objects.create(user_id=user.id, aircraft_id=plane.id)

        return {"status": "success", "message": "Plane purchased successfully."}
    else:
        return {"status": "failure", "message": "Insufficient balance."}

@app.route("/gallery")
@jwt_required()
def gallery():
    user = User.objects.get(name=get_jwt_identity())
    planes = User_X_Plane.objects.filter(user_id=user.id)
    user_data = {
        "id": user.id,
        "name": user.name
    }
    planes_data = [
        plane.plane.Json
        for plane in planes
    ]
    return {"user": user_data, "planes": planes_data}


@app.route("/ranking")
@jwt_required()
def ranking():
    current_user = User.objects.get(name=get_jwt_identity())
    users = User.objects.filter(order_by='total_amount', reverse=True)
    context = {
        'current_user_id': current_user.id,
        'users': [user.Ranking for user in users],
    }

    return context


#-------------------------- Auth API ------------------------------------

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(days=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
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
    refresh_token = create_refresh_token(identity=username)
    response = jsonify({'register': True})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    default_plane = Plane.objects.get(plane_key='sky_hawk_100')
    User_X_Plane.objects.create(user_id=user.id, aircraft_id=default_plane.id)

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
    refresh_token = create_refresh_token(identity=username)
    response = jsonify({'login': True})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response

@app.route("/logout", methods=["GET", "POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/is_authenticated')
@jwt_required()
def is_authenticated():
    response_body = {
        "is_authenticated": 1,
    }

    return response_body

#------------------------- Pages --------------------------------------------

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

