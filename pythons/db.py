

class DB:
    import sqlalchemy as sal
    from geoalchemy2 import Geometry
    import datetime

    SCHEMA = 'boxpanda'
    GIS_TABLE_NAME = 'gis_data_table'
    USER_TABLE_NAME = 'user_table'
    ITEM_TABLE_NAME = 'item_table'
    FCM_TABLE_NAME = 'fcm_table'
    HASH_TABLE_NAME = 'hashed_table'
    DB_SERVER = 'postgresql://postgres:123456@101.101.162.213/gisdb'

    engine = sal.create_engine(DB_SERVER)
    conn = engine.connect()

    md = sal.MetaData(schema=SCHEMA)
    md._bind_to(conn)
    md.reflect(engine) 


    def init(self):
        try:
            self.md.reflect(self.engine) 
        except self.sal.exc.OperationalError as e:
            print("Reconnecting to DB server...")
            self.conn = self.engine.connect()
            self.md.reflect(self.engine) 

    def table(_table_name):
        return md.tables[SCHEMA + '.' + _table_name]

    USER_TABLE = md.tables[SCHEMA + '.' + USER_TABLE_NAME]
    GIS_TABLE = md.tables[SCHEMA + '.' + GIS_TABLE_NAME]
    ITEM_TABLE = md.tables[SCHEMA + '.' + ITEM_TABLE_NAME]
    FCM_TABLE = md.tables[SCHEMA + '.' + FCM_TABLE_NAME]
    HASHED_TABLE = md.tables[SCHEMA + '.' + HASH_TABLE_NAME]

    def result(self, _select):
        try:
            ret = self.conn.execute(_select)
        except self.sal.exc.OperationalError as e:
            print("Reconnecting to DB server...")
            self.conn = self.engine.connect()
            ret = self.conn.execute(_select)
        return ret.fetchall()

    def insert(self, _table, _params):
        params = []
        if type(_params[0]) != type(list()):
            print('Insert _params with list.')
            return 0
        else:
            for _param in _params:
                if (_table.name == self.USER_TABLE_NAME):
                    params.append(
                        {
                            'name':_param[0]
                        }
                    )
                elif (_table.name == self.ITEM_TABLE_NAME):
                    params.append(
                        {
                            'user_id':_param[0],
                            'start_point':_param[1],
                            'end_point':'POINT(0 0)',
                            'timestamp':_param[2]
                        }
                    )
                elif (_table.name == self.GIS_TABLE_NAME):
                    params.append(
                        {
                            'item_id':_param[0],
                            'point':_param[1],
                            'timestamp':_param[2]
                        }
                    )
                elif (_table.name == self.FCM_TABLE_NAME):
                    params.append(
                        {
                            'device_key':_param[1],
                            'user_id':_param[0]
                        }
                    )
                elif (_table.name == self.HASH_TABLE_NAME):
                    params.append(
                        {
                            'hash_id':_param[0],
                            'item_id':_param[1]
                        }
                    )
            try:
                result = self.conn.execute(_table.insert(), params)
            except self.sal.exc.OperationalError as e:
                print("Reconnecting to DB server...")
                self.conn = self.engine.connect()
                result = self.conn.execute(_table.insert(), params)
                
        return result
        