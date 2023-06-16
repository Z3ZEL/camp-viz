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
    def toGeoJSON(self):
        '''Return camp as geojson'''
        return {"type":"Feature", "properties":{}, "geometry":{"type":"Point", "coordinates":[self.lon, self.lat]}}

    #getters
    def getName(self):
        return self.name
    def getDescription(self):
        return self.description if self.description != None else ""
    def getLat(self):
        return self.lat
    def getLon(self):
        return self.lon
    def getElevation(self):
        return self.elevation
    def getCopy(self):
        return Camp(self.name, self.description, self.lat, self.lon, self.elevation)
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
    from save_methods.save_method import SaveMethod as SaveStructure
    def __init__(self, method : SaveStructure, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[CAMP DATA]")
        self.method = method
        self.logger.print("CampData initialized")
        self.modifiedQueue = []
    
    def addCamp(self, camp: Camp):
        '''Add camp to data'''
        if(not isinstance(camp, Camp)):
            self.logger.error("Camp is not a Camp object")
            return -1

        self.camps.append(camp)
        self.modifiedQueue.append(("add", camp))
        self.size += 1
    def removeCamp(self, camp: Camp):
        '''Remove camp from data'''
        self.camps.remove(camp)
        self.modifiedQueue.append(("remove", camp))
        self.size -= 1
    def modifyCamp(self, camp: Camp, newCamp: Camp):
        '''Modify camp from data'''
        index = self.camps.index(camp)
        self.camps[index] = newCamp
        self.modifiedQueue.append(("modify", newCamp))

    def createData(self):
        '''Create data file on database'''
        self.__initData__({"size":0, "camps":[]})
        return self.method.create_method()
    def fetchData(self):
        '''Fetch data from database'''
        (code,data) = self.method.fetch_method()
        if code == 0:
            self.logger.print("Data fetched")
            self.__initData__(data)
            return code
        else:
            self.logger.error("Error while fetching data, code: " + str(code))
            return code;
    def saveData(self):
        '''
        Save data to database

        Returns:
            int: 0 if saved, 1 if not dirty, -1 if error
        '''
        if not self.isDirty() :
            self.logger.print("Data is not dirty, no need to save")
            return 1
        
        code = self.method.save_method(self)
        return code
        


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
        return len(self.modifiedQueue) > 0
    def getModifiedQueue(self):
        return self.modifiedQueue
