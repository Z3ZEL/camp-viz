import gpxpy
import gpxpy.gpx
import os
import psycopg2
from dotenv import load_dotenv
gpx_file = open('input/explore.gpx', 'r')
gpx = gpxpy.parse(gpx_file)


for waypoint in gpx.waypoints:
    print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))


def main():
    #LOAD DOTENV
    load_dotenv()

    host = os.getenv("PGHOST")
    database = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    

    #PRINT ENVIRONMENT VARIABLES
    print("--------------------")
    print("POSTGRES_HOST: " + host)
    print("POSTGRES_DB: " + database)
    print("POSTGRES_USER: " + user)

    print("--------------------")

    ## Connect to postgresql
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    # CHECK CONNECTION
    if conn:
        print("Connection established")
    else:
        print("Connection not established")
        


if __name__ == '__main__':
    main()