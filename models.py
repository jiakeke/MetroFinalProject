from mysql import connector
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


def register_class(model):
    model.objects = BaseList(model)




class BaseList:
    def __init__(self, model):
        self.model = model

    def conditions(self, **kws):
        keywords = ' and '.join(["%s='%s'" % (k, v) for k, v in kws.items()])
        return keywords

    def sql_string(self, **kws):
        keywords = self.conditions(**kws)
        sql = "select * from %s where %s;" % (self.model.db_table, keywords)
        return sql

    def all(self):
        pass

    def get(self, **kws):
        pass

    def count(self, ):
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

    def update(self, **kws):
        pass

    def delete(self, **kws):
        pass


class Base:
    db_table = ''
    fields = []

    def __init__(self, **kws):
        for key, value in kws.items():
            setattr(self, key, value)




class Airport(Base):
    db_table = 'airport'
    fields = [
        'id', 'ident', 'type', 'name', 'longitude_deg', 'latitude_deg',
        'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
        'scheduled_service', 'gps_code', 'iata_code', 'local_code', 'home_link',
        'wikipedia_link', 'keywords'
    ]

register_class(Airport)



class Country(Base):
    db_table = 'country'


register_class(Country)



class Plane(Base):
    pass


register_class(Plane)



class User(Base):
    db_table = 'users'
    fields = [
        'id', 'name', 'password', 'status', 'total_amount', 'balance',
        'carbon_emission'
    ]

register_class(User)



if __name__ == '__main__':
    airports = Airport.objects.filter(iso_country='FI')
    for airport in airports:
        print(airport.name)
    print(len(airports))

