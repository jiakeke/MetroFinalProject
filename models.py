import random

from mysql import connector
from geopy.distance import geodesic

import config


def get_connection():
    connection = connector.connect(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_pass,
    )
    return connection



class BaseList:
    def __init__(self, model):
        self.model = model

    def conditions(self, **kws):
        conditions = ''
        if kws:
            keywords = ' AND '.join(["%s='%s'" % (k, v) for k, v in kws.items()])
            conditions = ' WHERE ' + keywords
        return conditions

    def sql_string(self, order_by=None, reverse=False, limit=None, **kws):
        sql = "SELECT * FROM %s %s" % (self.model.db_table, self.conditions(**kws))
        if order_by is not None:
            if order_by in self.model.fields:
                sql += f' ORDER BY {order_by}'
                if reverse:
                    sql += ' DESC'
            elif order_by == 'random':
                sql += f' ORDER BY RAND()'

        if isinstance(limit, int):
            sql += f' LIMIT {limit}'

        return sql

    def all(self):
        return self.filter()

    def get(self, **kws):
        res = self.filter(**kws)
        return res and res[0] or None

    def count(self, **kws):
        pass


    def filter(self, **kws):
        sql = self.sql_string(**kws)
        print(sql)
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        names = cursor.column_names
        result = cursor.fetchall()
        tmp = []
        if cursor.rowcount >0 :
            for row in result:
                props = dict(zip(names, row))
                obj = self.model(**props)
                tmp.append(obj)
        return tmp

    def create(self, **kws):
        columns = []
        values = []
        for key, value in kws.items():
            if key in self.model.fields:
                columns.append(key)
                values.append(f"'{value}'")

        sql = (
            f"INSERT INTO {self.model.db_table} ({', '.join(columns)}) "
            f"VALUES ({', '.join(values)});"
        )
        print(sql)
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        id = cursor.lastrowid
        print(f'create id: {id}')
        return self.get(id=id)

    def update(self, id, **kws):
        statements = []
        for key, value in kws.items():
            statements.append(f"{key}='{value}'")

        sql = (
            f"UPDATE {self.model.db_table} "
            f"SET {','.join(statements)} "
            f"WHERE id={id}"
        )
        print(sql)
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()

    def delete(self, **kws):
        pass


def register_class(model, list_cls=BaseList):
    model.objects = list_cls(model)


class Base:
    db_table = ''
    fields = []

    def __init__(self, **kws):
        for key, value in kws.items():
            clean_method = getattr(self, 'clean_'+key, None)
            if clean_method:
                value = clean_method(value)
            setattr(self, key, value)

    def save(self):
        pass


class Airport(Base):
    db_table = 'airport'
    fields = [
        'id', 'ident', 'type', 'name', 'longitude_deg', 'latitude_deg',
        'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
        'scheduled_service', 'gps_code', 'iata_code', 'local_code', 'home_link',
        'wikipedia_link', 'keywords'
    ]

    @property
    def coordinate(self):
        return (self.latitude_deg, self.longitude_deg)


register_class(Airport)



class Country(Base):
    db_table = 'country'


register_class(Country)



class User(Base):
    db_table = 'users'
    fields = [
        'id', 'name', 'password', 'status', 'total_amount', 'balance',
        'carbon_emission'
    ]

    @property
    def is_beginner(self):
        return self.status and True or False

    @property
    def planes(self):
        x_planes = User_X_Plane.objects.filter(user_id=self.id)
        return x_planes

    @property
    def max_capacity(self):
        props = [plane.plane.passenger_capacity for plane in self.planes]
        return max(props)

    @property
    def max_range(self):
        props = [plane.plane.flight_range for plane in self.planes]
        return max(props)

    @property
    def Ranking(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.total_amount,
        }

    def get_user_props():
        """
        Returns the maximum range and passenger capacity of all planes owned by
        the player
        """
        return self.max_range, self.max_capacity

    @property
    def current_task(self):
        from pilot import calculate_flight_reward
        task = Task.objects.get(user_id=self.id, is_new=1)

        if not task:
            if self.is_beginner:
                departure = Airport.objects.get(ident='EDDB')
                destination = Airport.objects.get(ident='EDDH')
                passenger = 10
                reward = 1000
                distance = geodesic(departure.coordinate, destination.coordinate).kilometers
                print(distance)
            else:
                departure, destination = Airport.objects.filter(
                    order_by='random', limit=2, continent='EU')

                passenger = random.randint(1, self.max_capacity + 10)
                distance = geodesic(departure.coordinate, destination.coordinate).kilometers
                reward = calculate_flight_reward(distance)

            kws = {
                'user_id': self.id,
                'departure_id': departure.id,
                'destination_id': destination.id,
                'distance': distance,
                'passenger': passenger,
                'reward': reward,
            }
            task = Task.objects.create(**kws)

        return task



register_class(User)


class Plane(Base):
    db_table = 'aircraft'
    fields = [
        'id', 'name', 'passenger_capacity', 'flight_range', 'price',
        'carbon_emission', 'image', 'plane_key',
    ]

    @property
    def Json(self):
        return {
            'id': self.id,
            'name': self.name,
            'flight_range': self.flight_range,
            'price': self.price,
            'img': self.image,
            'passenger': self.passenger_capacity,
        }


register_class(Plane)


class User_X_Plane(Base):
    db_table = 'user_aircraft'
    fields = [
        'id', 'user_id', 'aircraft_id'
    ]

    @property
    def plane(self):
        return Plane.objects.get(id=self.aircraft_id)

register_class(User_X_Plane)


class Task(Base):
    db_table = 'tasks'
    fields = [
        'id', 'user_id', 'departure_id', 'destination_id', 'distance',
        'passenger', 'reward', 'is_new',
    ]

    @property
    def user(self):
        if self.user_id:
            return User.objects.get(id=self.user_id)

    @property
    def departure(self):
        if self.departure_id:
            return Airport.objects.get(id=self.departure_id)

    @property
    def destination(self):
        if self.destination_id:
            return Airport.objects.get(id=self.destination_id)

    @property
    def Json(self):
        return [
            ['departure_name', 'Departure Name', self.departure.name],
            ['destination_name', 'Destination Name', self.destination.name],
            ['distance', 'Distance', self.distance],
            ['passenger', 'Passenger', self.passenger],
            ['reward', 'Reward', self.reward],
        ]

    def play(self, plane):
        from pilot import calculate_carbon_emission
        from pilot import get_weather_index
        distance = self.distance
        carbon_coefficient = plane.carbon_emission
        carbon_emission = calculate_carbon_emission(distance)

        carbon_cost = carbon_emission * carbon_coefficient
        fuel_cost = distance * 2.2
        if self.user.is_beginner:
            latitude = "tutorial"
        else:
            latitude = self.destination.latitude_deg

        weather_index = get_weather_index(latitude)
        total_cost = (fuel_cost + carbon_cost) * weather_index[1]

        User.objects.update(self.user.id, carbon_emission=self.user.carbon_emission+carbon_emission)
        User.objects.update(self.user.id, status=0)
        Task.objects.update(self.id, is_new=0)

        refuel_cost = 0
        refuel_times = 0
        if distance > self.user.max_range:
            refuel_times = int(distance / self.user.max_range)
            refuel_cost = 50 * refuel_times
            total_cost += refuel_cost

        if self.passenger > self.user.max_capacity:
            result = {
                'status': 'Mission Fail!',
                'msgs': ["The number of passengers exceeds your plane's capacity."],
            }
            return result

        total_income = round(self.reward - total_cost, 1)
        if total_income > 0:
            self.user.objects.update(
                self.user.id,
                balance=self.user.balance+total_income,
                total_amount=self.user.total_amount+total_income
            )
        else:
            result = {
                'status': 'Mission Fail!',
                'msgs': ["Your cost is larger than profit."],
            }
            return result

        result = {'status': 'Mission Successful', 'msgs': []}
        if refuel_cost:
            result['msgs'].append(
                f"You had to refuel {refuel_times} times during your trip. "
                f"This cost an additional {refuel_cost} coins.")

        result['msgs'].append(
            f"You encountered {weather_index[0]} weather "
            f"at your destination airport")
        result['msgs'].append(
            f"Task successful!\nYou earned: {total_income:.1f}\n"
            f"Total cost was: {total_cost:.1f}\n")
        return result



register_class(Task)

if __name__ == '__main__':
    pass


