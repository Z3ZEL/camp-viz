import gpxpy
import gpxpy.gpx
import os
import psycopg2
import sys
from dotenv import load_dotenv

## LOCAL IMPORTS
from log import Log
from data_updater import DataUpdater
from obj.camp_data import CampData

gpx_file = open('input/explore.gpx', 'r')
gpx = gpxpy.parse(gpx_file)




def main(args):
    #CHECK VERBOSE OPTIONS
    verbose = False
    if "-v" in args:
        verbose = True
    
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

    # CREATE DATA OBJECT
  


    data = CampData(conn=conn,verbose=verbose)

    
    fetch_method = data.fetch_method_database
    create_method = data.create_method_database
    save_method = data.save_method_database

    code = data.fetchData(fetch_method) 
    if code != 0:
        if(code == -2):
            data.createData(create_method)
    # data.printData()
    # # CREATE DATA UPDATER
    updater = DataUpdater(data, verbose=verbose)
    # # # UPDATE DATA
    updater.updateFromGpx(gpx, method=save_method)







if __name__ == '__main__':
    main(sys.argv[1:])