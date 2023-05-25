from log import Logger
import gpxpy
import gpxpy.gpx
from psycopg2.extensions import connection
from shapely.geometry import Point

from obj.camp_data import CampData, Camp

class DataUpdater(Logger):
    def __init__(self, data: CampData, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[DATA UPDATER]")
        self.data = data
        self.logger.print("DataUpdater initialized")        

    def updateFromGpx(self, gpx: gpxpy.gpx.GPX, method=None):
        '''
        Update database object with gpx data
        
        Parameters:
            gpx (gpxpy.gpx.GPX): GPX object

        Returns:
            int: 0 if updated, 1 if already up to date, -1 if error
    
        '''
        upToDate = True
        for waypoint in gpx.waypoints:
            camp = Camp(waypoint.name, waypoint.description, waypoint.latitude, waypoint.longitude, waypoint.elevation)
            alreadyExists = False
            for c in self.data.camps:
                if Camp.isCampSame(c, camp):
                    alreadyExists = True
                    break
            if not alreadyExists:
                self.logger.print("Adding camp " + camp.name)
                self.data.addCamp(camp)
                upToDate = False
        if upToDate:
            self.logger.printAnyway("Data is already up to date")
            return 1
        
        if method is not None:
            return self.data.saveData(method)
        else:
            return 0
        
       


        


        
