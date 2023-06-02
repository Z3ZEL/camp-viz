import sys;
import json

from save_methods.save_method import SaveMethod;

sys.path.append("..")
# from save_method import SaveMethod


class SaveLocal(SaveMethod):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.logger.print("SaveLocal initialized")
    
    def fetch_method(self) -> tuple:
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
    def create_method(self) -> int:
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
    def save_method(self, data) -> int:
        self.logger.print("Saving data to local file")
        # SAVE DATA TO LOCAL FILE
        data = {"size":data.getSize(),"camps": [c.toDict() for c in data.getCamps()]}
        try:
            with open('data/camp_data.json', 'w') as outfile:
                # WRITE JSON FILE
                json.dump(data, outfile)
                return 0
        except Exception as e:
            self.logger.error("Error while saving file : " + str(e))
            return -1