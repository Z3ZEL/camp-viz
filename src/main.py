import gpxpy
import gpxpy.gpx

gpx_file = open('input/explore.gpx', 'r')
gpx = gpxpy.parse(gpx_file)


for waypoint in gpx.waypoints:
    print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))


if __name__ == '__main__':
    pass