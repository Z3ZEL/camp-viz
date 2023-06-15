import sys;
import json

from save_methods.save_method import SaveMethod;

sys.path.append("..")


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
        from camp_data import Camp
        self.logger.print("Saving data to local file")
        # SAVE DATA TO LOCAL FILE
        campsToSave = data.getModifiedQueue()
        with open('data/camp_data.json') as json_file:
            # READ JSON FILE
            data = json.load(json_file)
            # UPDATE DATA
            for (action, camp) in campsToSave:
                self.logger.print("Saving "+camp.getName())
                if action == "add":
                    data["camps"].append(camp.toDict())
                elif action == "remove":
                    data["camps"].remove(camp.toDict())
                elif action == "modify":
                    for i in range(len(data["camps"])):
                        if Camp.isCampSame(Camp.fromDict(data["camps"][i]), camp):
                            data["camps"][i] = camp.toDict()
                            break
            data["size"] = len(data["camps"])
            # WRITE JSON FILE
            with open('data/camp_data.json', 'w') as outfile:
                json.dump(data, outfile)
                return 0
        return -1
