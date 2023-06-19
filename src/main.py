import importlib
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

class VIS_PATH:
    CONSOLE = 'data_vis.data_vis_console'
    WEB = 'data_vis.data_vis_web'


def main(args):
    METHOD="local"
    VIS=VIS_PATH.CONSOLE
    GPX_FILE_PATH = ""
    GPX = False


    #CHECK VERBOSE OPTIONS
    verbose = False
    if "-v" in args or "--verbose" in args:
        verbose = True

    logger = Log(verbose=verbose, header="[MAIN]")
    
    def is_missing_arg(arg):
        if len(args) <= args.index(arg) + 1:
            logger.error("Missing argument after " + arg)
            exit(1)
    ## ------ SAVE OPTIONS ------
    def make_method(arg):
        if method == "local":
            return "local"
        elif method == "database":
            return "database"
        else:
            logger.error("Invalid method")
            exit(1)

    if "--method" in args:
        is_missing_arg("--method")
        method = args[args.index("--method") + 1]
        METHOD = make_method(method)
    if "-m" in args:
        is_missing_arg("-m")
        method = args[args.index("-m") + 1]
        METHOD = make_method(method)


    ## ------ VISUALIZATION OPTIONS ------
    def make_vis(arg):
        if vis == "console":
            return VIS_PATH.CONSOLE
        elif vis == "web":
            return VIS_PATH.WEB
        else:
            logger.error("Invalid vis")
            exit(1)

    if "--display" in args:
        is_missing_arg("--display")
        vis = args[args.index("--display") + 1]
        VIS = make_vis(vis)
    if "-d" in args:
        is_missing_arg("-d")
        vis = args[args.index("-d") + 1]
        VIS = make_vis(vis)


    ## ------ GPX OPTIONS ------
    if "--update" in args:
        #CHECK IF there is an argument after --update
        is_missing_arg("--update")
        GPX_FILE_PATH = args[args.index("--update") + 1]
        GPX = True
    if "-u" in args:
        #CHECK IF there is an argument after -u
        is_missing_arg("-u")
        GPX_FILE_PATH = args[args.index("-u") + 1]
        GPX = True



    ## ------ HELP ------
    if "--help" in args or "-h" in args:
        print("Usage: python3 main.py [options]")
        print("Options:")
        print("\t--verbose, -v\t Enable verbose mode")
        print("\t--method, -m\t Set save method (local, database)")
        print("\t--vis, -d\t Set visualization method (console, web)")
        print("\t--update, -u\t Update database with gpx file")
        print("\t--help, -h\t Show this help message")
        exit(0)

    

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

    if GPX:
        try:
            gpx_file = open(GPX_FILE_PATH, 'r')
        except (FileNotFoundError) as e:
            logger.error('File not found')
            exit(1)



        gpx = gpxpy.parse(gpx_file)
        updater = DataUpdater(data, verbose=verbose)
        output = updater.updateFromGpx(gpx)
        if output == 0:
            logger.printAnyway("Data already up to date")
            exit(0)
        elif output == -1:
            logger.error("Error while updating data")
            exit(1)
        else:
            logger.printAnyway(f"{output} new camps found. Do you want to add them to the database? (y/n)")
            answer = input()
            if answer == "y":
                saving_output = data.saveData()
                if saving_output == 0:
                    logger.printAnyway("Data saved")
                if saving_output == -1:
                    logger.error("Error while saving data")
            else:
                logger.printAnyway("Data not saved")
            exit(0)
    # data.printData()
    # # CREATE DATA UPDATER
    # updater = DataUpdater(data, verbose=verbose)
    # # # # UPDATE DATA
    # updater.updateFromGpx(gpx)
    
    # data.saveData()
    Visualizer = importlib.import_module(VIS).Visualizer

    vis = Visualizer(data, verbose=verbose)
    vis.loop()




if __name__ == '__main__':
    main(sys.argv[1:])