import json
import sys
sys.path.append("..")

# IMPORTS
from log import Logger

class CampData(Logger):
    def __init__(self, conn=None, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[DATA UPDATER]")
        self.conn = conn
        self.logger.print("CampData initialized")
    
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
        
    def fetch_method_local(self):
        '''Fetch data from local file'''
        # READ THE DATA ON LOCAL FILE 
        self.logger.print("Reading data from local file")
        # CHECK IF FILE EXISTS
        try:
            with open('data/camp_data.json') as json_file:
                # READ JSON FILE
                data = json.load(json_file)
                # PRINT DATA
                self.logger.print(data)
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
            return False
        self.logger.print("Reading data from database")
    def create_method_local(self):
        '''Create data file on local file'''
        self.logger.print("Creating data file on local file")
        # CREATE JSON FILE
        data = {"size":0}
        try:
            with open('data/camp_data.json', 'w') as outfile:
                # WRITE JSON FILE
                json.dump(data, outfile)
                return 0
        except:
            self.logger.error("Error while creating file")
            return -1

    def __initData__(self, data):
        return 0;