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
        keywords = ' AND '.join(["%s='%s'" % (k, v) for k, v in kws.items()])
        return keywords

    def sql_string(self, order_by=None, limit=None, **kws):
        keywords = self.conditions(**kws)
        sql = "SELECT * FROM %s WHERE %s" % (self.model.db_table, keywords)
        if order_by is not None:
            if order_by in self.model.fields:
                sql += f' ORDER BY {order_by}'
            elif order_by == 'random':
                sql += f' ORDER BY RAND()'

        if isinstance(limit, int):
            sql += f' LIMIT {limit}'

        return sql

    def all(self):
        pass

    def get(self, **kws):
        res = self.filter(**kws)
        return res and res[0] or None

    def count(self, **kws):
        pass


    def filter(self, **kws):
        sql = self.sql_string(**kws)
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

    def update(self, **kws):
        pass

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
        props = [plane.passenger_capacity for plane in self.planes]
        return max(props)

    @property
    def max_range(self):
        props = [plane.flight_range for plane in self.planes]
        return max(props)

    def get_user_props():
        """
        Returns the maximum range and passenger capacity of all planes owned by
        the player
        """
        return self.max_range, self.max_capacity

    @property
    def current_task(self):
        task = Task.objects.get(user_id=self.id, is_new=1)

        if not task:
            if self.is_beginner:
                departure = Airport.objects.get(ident='EDDB')
                destination = Airport.objects.get(ident='EDDH')
                distance = 255.96
                passenger = 10
                reward = 1000
            else:
                departure, destination = Airport.objects.filter(order_by='random', limit=2)
                distance = geodesic(departure.coordinate, destination.coordinate).kilometers
                passenger = random.randint(1, max_capacity + 10)
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
        return {
            'departure_name': self.departure.name,
            'destination_name': self.destination.name,
            'distance': self.distance,
            'passenger': self.passenger,
            'reward': self.reward,
        }

    def play(self):
        pass


class TaskList(BaseList):
    pass


register_class(Task, TaskList)

if __name__ == '__main__':
    pass


