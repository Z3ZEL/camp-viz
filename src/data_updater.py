from log import Log
import gpxpy
import gpxpy.gpx
from shapely.geometry import Point

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

        # CHECK IF waypoints TABLE EXISTS
        self.cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'waypoints')")
        self.conn.commit()
        exists = self.cur.fetchone()[0]
        if not exists:
            # CREATE waypoints TABLE
            self.logger.print("Creating waypoints table")
            self.cur.execute("CREATE TABLE waypoints (id SERIAL PRIMARY KEY, name VARCHAR(255), description VARCHAR(255), geom GEOMETRY(Point, 4326))")
            self.conn.commit()

        # INSERT WAYPOINTS ONLY NEW WAYPOINTS INTO waypoints TABLE 
        for waypoint in waypoints:
            point = Point(waypoint.longitude, waypoint.latitude)
        
            # INSERT WAYPOINT INTO waypoints TABLE IF NOT EXISTS
            self.cur.execute("SELECT EXISTS (SELECT * FROM waypoints WHERE name = %s)", (waypoint.name,))
            self.conn.commit()
            exists = self.cur.fetchone()[0]

            updated = True;

            if not exists:
                # INSERT WAYPOINT INTO waypoints TABLE NAME DESCRIPTION AND GEOM
                self.logger.print("Inserting waypoint: " + waypoint.name)
                exe = self.cur.execute("INSERT INTO waypoints (name, description, geom) VALUES (%s, %s, ST_GeomFromText(%s,4326))", (waypoint.name, waypoint.description, point.wkt))
                self.conn.commit()
                if(not(exe)):
                    self.logger.error("Failed to insert waypoint: " + waypoint.name)
                    self.conn.rollback()
                updated = False
            

            if(updated):
                self.logger.printAnyway("Waypoints are already up to date")

            
                
            
        


        
