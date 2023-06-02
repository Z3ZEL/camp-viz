import sys
sys.path.append("..")
# from camp_data import CampData as CampDataStruct
from log import Logger

class SaveMethod(Logger):
    def __init__(self, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[SAVE METHOD]")
        self.verbose = verbose
    '''Interface for saving data'''
    def fetch_method(self) -> tuple:
        '''Fetch data from database
        
        code = 0 if success
        code = -1 if error
        code = -2 if data not found

        Returns:
            tuple: (code,data)
        
            
        '''
        pass
    def create_method(self) -> int:
        '''Create data on database
        
        code = 0 if success
        code = -1 if error

        Returns:
            int: code
        '''
        pass
    def save_method(self, campData) -> int:
        '''Save data to database
        
        code = 0 if success
        code = -1 if error

        Args:
            campData (CampData): CampData object

        Returns:
            int: code
        '''
        pass

    