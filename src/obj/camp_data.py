import json
import sys
sys.path.append("..")
import psycopg2
from psycopg2.extensions import connection
from shapely.geometry import Point

# IMPORTS
from log import Logger

class Camp():
    def __init__(self, name, description, lat, lon, elevation):
        self.name = name
        self.description = description
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
    def __str__(self):
        '''Mutliple lines string'''
        return "\n--------------\nName: " + str(self.name) + "\nDescription: " + str(self.description) + "\nLat: " + str(self.lat) + "\nLon: " + str(self.lon) + "\nElevation: " + str(self.elevation)+"\n--------------"
    def toDict(self):
        '''Return camp as json'''
        return self.__dict__


    #getters
    def getName(self):
        return self.name
    def getDescription(self):
        return self.description
    def getLat(self):
        return self.lat
    def getLon(self):
        return self.lon
    def getElevation(self):
        return self.elevation
        ## STATIC
    @staticmethod
    def isCampSame(camp1, camp2) -> bool:
        '''Check if two camps are the same'''
        if camp1.lat == camp2.lat and camp1.lon == camp2.lon and camp1.elevation == camp2.elevation:
            return True
        else:
            return False
    @staticmethod
    def fromDict(d: dict):
        '''Create camp from dict'''
        return Camp(d["name"], d["description"], d["lat"], d["lon"], d["elevation"])

#TODO: gerer l'update, avec une queue des points modifiés comme ça on selectionne les points modifiés et on les update
class CampData(Logger):
    def __init__(self, conn:connection=None, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[CAMP DATA]")
        if conn is not None :
            self.conn = conn
            self.cur = conn.cursor()
        self.logger.print("CampData initialized")
    
    def addCamp(self, camp: Camp):
        '''Add camp to data'''
        if(not isinstance(camp, Camp)):
            self.logger.error("Camp is not a Camp object")
            return -1

        self.camps.append(camp)
        self.size += 1
        self.isDirty = True
    def removeCamp(self, camp):
        '''Remove camp from data'''
        self.camps.remove(camp)
        self.size -= 1
        self.isDirty = True

    def createData(self,method):
        '''Create data file on database'''
        return method()
    def fetchData(self, method):
        '''Fetch data from database'''
        (code,data) = method()
        if code == 0:
            self.logger.print("Data fetched")
            self.__initData__(data)
            return code
        else:
            self.logger.error("Error while fetching data, code: " + str(code))
            return code;
    def saveData(self, method):
        '''Save data to database'''
        return method()        

    # METHODS
    def fetch_method_local(self):
        '''Fetch data from local file'''
        # READ THE DATA ON LOCAL FILE 
        self.logger.print("Reading data from local file")
        # CHECK IF FILE EXISTS
        try:
            with open('data/camp_data.json') as json_file:
                # READ JSON FILE
                data = json.load(json_file)
                # create data object
                return (0,data)
        except:
            self.logger.error("File not found")
            return (-2, None)
    def fetch_method_database(self):
        '''Fetch data from database'''
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

    
    def create_method_database(self):
        '''Create data file on database'''
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



    def create_method_local(self):
        '''Create data file on local file'''
        self.logger.print("Creating data file on local file")
        # CREATE JSON FILE
        data = {"size":0,"camps":[]}
        try:
            with open('data/camp_data.json', 'w') as outfile:
                # WRITE JSON FILE
                json.dump(data, outfile)
                return 0
        except:
            self.logger.error("Error while creating file")
            return -1
    def save_method_local(self):
        '''Save data to local file'''
        if not self.isDirty:
            self.logger.print("Data not dirty")
            return 0
        self.logger.print("Saving data to local file")
        # SAVE DATA TO LOCAL FILE
        data = {"size":self.size,"camps": [c.toDict() for c in self.camps]}
        try:
            with open('data/camp_data.json', 'w') as outfile:
                # WRITE JSON FILE
                json.dump(data, outfile)
                return 0
        except Exception as e:
            self.logger.error("Error while saving file : " + str(e))
            return -1
    def save_method_database(self):
        '''Save data to database'''
        if not self.isDirty:
            self.logger.print("Data not dirty")
            return 0
        
        #Check connection
        if not self.conn:
            self.logger.error("Connection not established")
            return -3
        
        # RETRIEVE DATA FROM DATABASE
        self.logger.print("Saving data to database")
        upToDate = True
        try:
            for c in self.camps:
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
                
            



        



    def __initData__(self, data):
        '''Initialize data from dict
        Dict format:
        {
            "size": 0,
            "camps": [{
                "name": "Camp 1",
                "description": "Camp 1 description",
                "lat": 0,
                "lon": 0,
                "elevation": 0
            }]
        }
        
         
        Args:
            data (dict): data dict
            
            '''
        self.size = data["size"]
        self.camps = [Camp.fromDict(c) for c in data["camps"]]

    def printData(self):
        '''Print data'''
        print("Size: " + str(self.size))
        for camp in self.camps:
            self.logger.print(str(camp))


    ## GETTERS
    def getSize(self):
        return self.size
    def getCamps(self):
        return self.camps
    def isDirty(self):
        return self.isDirty
    
