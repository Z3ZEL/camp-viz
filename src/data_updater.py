from log import Log
import gpxpy
import gpxpy.gpx
from qgis.core import QgsGeometry, QgsPointZ

class DataUpdater():

    def __init__(self, conn, verbose=False):
        self.conn = conn;
        self.cur = conn.cursor()
        self.logger = Log(verbose=verbose, header="[DATA UPDATER]")

    def update(self, gpx: gpxpy.gpx.GPX):
        '''
        Update database with gpx data
        
        Parameters:
            gpx (gpxpy.gpx.GPX): GPX object
    
        '''

        # GET WAYPOINTS
        waypoints = gpx.waypoints

        # CHECK IF CAMP TABLE EXISTS
        self.cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'camp')")
        exists = self.cur.fetchone()[0]
        if not exists:
            # CREATE CAMP TABLE
            self.logger.print("Creating camp table")
            
        # INSERT WAYPOINTS ONLY NEW WAYPOINTS INTO CAMP TABLE 
        for waypoint in waypoints:
            self.logger.print("Inserting waypoint: " + waypoint.name)
            point = QgsPointZ(waypoint.longitude, waypoint.latitude, waypoint.elevation)
            geom = QgsGeometry.fromPointZ(point)

            # INSERT WAYPOINT INTO CAMP TABLE IF NOT EXISTS
            self.cur.execute("SELECT EXISTS (SELECT * FROM camp WHERE name = %s)", (waypoint.name,))
            exists = self.cur.fetchone()[0]

            updated = True;

            if not exists:
                # INSERT WAYPOINT INTO CAMP TABLE NAME DESCRIPTION AND GEOM
                self.logger.print("Inserting waypoint: " + waypoint.name)
                self.cur.execute("INSERT INTO camp (name, description, geom) VALUES (%s, %s, %s)", (waypoint.name, waypoint.description, geom))
                self.conn.commit()
                updated = False
            

            if(updated):
                self.logger.printAnyway("Waypoints are already up to date")

            
                
            
        


        
