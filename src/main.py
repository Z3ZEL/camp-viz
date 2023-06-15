import gpxpy
import gpxpy.gpx
import os
import psycopg2
import sys
from dotenv import load_dotenv

## LOCAL IMPORTS
from log import Log
from data_manipulations.data_updater import DataUpdater
from camp_data import CampData

gpx_file = open('input/explore.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

from data_vis.data_vis_console import Visualizer



def main(args):
    METHOD="local"

    #CHECK VERBOSE OPTIONS
    verbose = False
    if "-v" in args:
        verbose = True
    if "--method" in args:
        method = args[args.index("--method") + 1]
        if method == "local":
            METHOD = "local"
        elif method == "database":            
            METHOD = "database"
        else:
            print("Invalid method")
            exit(1)
    
    logger = Log(verbose=verbose, header="[MAIN]")

    #LOAD DOTENV
    load_dotenv()


    host = os.getenv("PGHOST")
    database = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    

    #PRINT ENVIRONMENT VARIABLES
    logger.print("--------------------")
    logger.print("POSTGRES_HOST: " + host)
    logger.print("POSTGRES_DB: " + database)
    logger.print("POSTGRES_USER: " + user)
    logger.print("--------------------")
   
        

    # CREATE DATA OBJECT


  
    method=None
    if METHOD == "local":
        from save_methods.save_local import SaveLocal
        method = SaveLocal(verbose=verbose)
    elif METHOD == "database":
        from save_methods.save_database import SaveDatabase
        try:
            # Connect to postgresql
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            # CHECK CONNECTION
            if conn:
                logger.printAnyway("Connection established")
            else:
                logger.error("Connection not established")
        except (psycopg2.Error) as e:
            pass
        method = SaveDatabase(conn,verbose=verbose)

    

    data = CampData(method=method,verbose=verbose)

    


    code = data.fetchData() 
    if code != 0:
        if(code == -2):
            data.createData()
    # data.printData()
    # # CREATE DATA UPDATER
    # updater = DataUpdater(data, verbose=verbose)
    # # # # UPDATE DATA
    # updater.updateFromGpx(gpx)
    
    # data.saveData()


    vis = Visualizer(data, verbose=verbose)
    vis.loop()




if __name__ == '__main__':
    main(sys.argv[1:])