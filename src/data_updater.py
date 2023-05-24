from log import Logger
import gpxpy
import gpxpy.gpx
from psycopg2.extensions import connection
import psycopg2
from shapely.geometry import Point

class DataUpdater(Logger):
    def __init__(self, conn: connection, verbose=False):
        Logger.__init__(self, verbose=verbose, header="[DATA UPDATER]")
        self.conn = conn;
        self.cur = conn.cursor()
        self.logger.print("DataUpdater initialized")

    def update(self, gpx: gpxpy.gpx.GPX):
        '''
        Update database with gpx data
        
        Parameters:
            gpx (gpxpy.gpx.GPX): GPX object

        Returns:
            int: 0 if updated, 1 if already up to date, -1 if error
    
        '''
        ##CHECK IF CONN IS GOOD TYPE AND OPEN
        if not isinstance(self.conn, connection):
            self.logger.error("Connection is not a psycopg2 connection")
            return -1
        if self.conn.closed:
            self.logger.error("Connection is closed")
            return -1
        

        # GET WAYPOINTS
        waypoints = gpx.waypoints

        # CHECK IF waypoints TABLE EXISTS
        self.cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'waypoints')")
        self.conn.commit()
        exists = self.cur.fetchone()[0]
        if not exists:
            # CREATE waypoints TABLE
            try:
                self.logger.print("Creating waypoints table")
                self.cur.execute("CREATE TABLE waypoints (id SERIAL PRIMARY KEY, name VARCHAR(255), description VARCHAR(255), geom GEOMETRY(Point, 4326))")
                self.conn.commit()
            except (psycopg2.Error) as e:
                self.logger.error("Error creating waypoints table.")
                self.logger.error(e.pgerror)
                return -1    

       
        # INSERT WAYPOINTS ONLY NEW WAYPOINTS INTO waypoints TABLE 
        updated = True;
        for waypoint in waypoints:
            point = Point(waypoint.longitude, waypoint.latitude)
        
            # INSERT WAYPOINT INTO waypoints TABLE IF NOT EXISTS
            self.cur.execute("SELECT EXISTS (SELECT * FROM waypoints WHERE name = %s)", (waypoint.name,))
            self.conn.commit()
            exists = self.cur.fetchone()[0]

            if not exists:
                # INSERT WAYPOINT INTO waypoints TABLE NAME DESCRIPTION AND GEOM*
                try:
                    self.logger.print("Inserting waypoint: " + waypoint.name)
                    self.cur.execute("INSERT INTO waypoints (name, description, geom) VALUES (%s, %s, ST_GeomFromText(%s,4326))", (waypoint.name, waypoint.description, point.wkt))
                    self.conn.commit()
                except (psycopg2.Error) as e:
                    self.logger.error("Error inserting waypoint.")
                    self.logger.error(e.pgerror)
                    return -1
                updated = False
            

        if(updated):
            self.logger.printAnyway("Waypoints are already up to date")
            return 1
        return 0

        
                
            
        


        
