import sys;
import json
from shapely.geometry import Point
from psycopg2.extensions import connection
import psycopg2

sys.path.append("..")

from save_method import SaveMethod
from camp_data import CampData

class SaveDatabase(SaveMethod):
    def __init__(self,conn: connection , verbose=False):
        super().__init__(verbose)
        self.conn = conn
        self.cursor = conn.cursor()
        self.logger.print("SaveDatabase initialized")
    
    def fetch_method(self) -> tuple:
        #Check connection
        if not self.conn:
            self.logger.error("Connection not established")
            return (-3, None)
         # CHECK IF waypoints TABLE EXISTS
        try:
            self.cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'waypoints')")
            self.conn.commit()
            exists = self.cur.fetchone()[0]
        except (psycopg2.Error) as e:
            self.logger.error("Error checking waypoints table.")
            self.logger.error(e.pgerror)
            return (-1, None)
        if not exists:
            self.logger.error("Waypoints table not found")
            return (-2, None)
        
        # FETCH DATA FROM DATABASE
        self.logger.print("Reading data from database")

        try:
            self.cur.execute("SELECT id, name, description FROM waypoints")
            self.conn.commit()
            dataRaw = self.cur.fetchall()
            data = {"camps":[]}
            for row in dataRaw:
                # Convert geometry to lat lon elevation
                self.cur.execute("SELECT ST_X(geom), ST_Y(geom), ST_Z(geom) FROM waypoints WHERE id = %s", (row[0],))
                self.conn.commit()
                (lon, lat, elevation) = self.cur.fetchone()
                # Create camp object
                camp = {"name":row[1], "description":row[2], "lat":lat, "lon":lon, "elevation":elevation}
                data["camps"].append(camp)
            data["size"] = len(data["camps"])
            self.logger.print(str(data["size"]) + " camps fetched")
            return (0,data)
        except (psycopg2.Error) as e:
            self.logger.error("Error fetching data from waypoints table.")
            self.logger.error(e.pgerror)
            return (-1, None)
    def create_method(self) -> int:
        #Check connection
        if not self.conn:
            self.logger.error("Connection not established")
            return False
        try:
            self.logger.print("Creating waypoints table")
            self.cur.execute("CREATE TABLE waypoints (id SERIAL PRIMARY KEY, name VARCHAR(255), description VARCHAR(255), geom GEOMETRY(PointZ, 4326))")
            self.conn.commit()
        except (psycopg2.Error) as e:
            self.logger.error("Error creating waypoints table.")
            self.logger.error(e.pgerror)
            return -1   
        return 0
    def save_method(self, data: CampData) -> int:   
        #Check connection
        if not self.conn:
            self.logger.error("Connection not established")
            return -3
        
        # RETRIEVE DATA FROM DATABASE
        self.logger.print("Saving data to database")
        upToDate = True
        try:
            for c in data.getCamps():
                # CHECK IF CAMP EXISTS
                exists = False
                self.cur.execute('SELECT id FROM waypoints WHERE name = %s', (c.getName(),))
                self.conn.commit()
                exists = self.cur.fetchone()
                if not exists:

                    # CREATE CAMP
                    point = Point(c.getLon(), c.getLat(), c.getElevation());
                    self.cur.execute('INSERT INTO waypoints (name, description, geom) VALUES (%s, %s, ST_GeomFromText(%s, 4326))', (c.getName(), c.getDescription(), point.wkt))
                    self.conn.commit()
                    upToDate = False
                    self.logger.print("Camp " + c.getName() + " uploaded")
            
        except (psycopg2.Error) as e:
            self.logger.error("Error saving data to waypoints table.")
            self.logger.error(e.pgerror)
            return -1

        if upToDate:
            self.logger.print("Data up to date")
            return 1
        return 0
                