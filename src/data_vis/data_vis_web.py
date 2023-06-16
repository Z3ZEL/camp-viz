from data_vis.data_vis import IVisualizer

import sys
sys.argv.append('..')
from camp_data import CampData

from dash import Dash
import dash_leaflet as dl
from dash import html
from dash.dependencies import Input, Output

class Visualizer(IVisualizer):
    app = None
    def __init__(self, campData: CampData, verbose=False):
        super().__init__(campData, verbose)
        self.app = Dash(__name__, external_scripts=[{'src': 'https://cdn.tailwindcss.com'}], external_stylesheets=['https://cdn.jsdelivr.net/npm/daisyui@3.1.1/dist/full.css'])
        self.app.layout = self.__get_layout__()
        self.app.title = "Camp Data Visualizer"
        
        #Add script
        #disable server locally
        self.app.css.config.serve_locally = True
        self.app.scripts.config.serve_locally = True

        ##INIT CALLBACKS
        @self.app.callback(Output("camp-info", "children"), [Input("camps", "click_feature")])
        def __map_click__(feature):
            if feature is not None:
                return f"{feature['properties']['description']}"
            else:
                return "Click a point on the map"
    def __get__geojson__(self):
        '''Convert all camp to a geojson object'''
        geojson = {"type":"FeatureCollection", "features":[]}
        for camp in self.data.getCamps():
            tmp = camp.toGeoJSON()
            tmp["properties"]["name"] = camp.getName()
            tmp["properties"]["description"] = camp.getDescription()
            tmp["properties"]["tooltip"] = camp.getName()
            geojson["features"].append(tmp) 
        self.logger.print("Geojson initialized")
        return geojson

    
    ##GET LAYOUT
    def __get_layout__(self):
        #append camp
        return html.Div([self.__get__header__(), 
                         html.Div([self.__get__map__(),
                                    self.__get__information_tab__()],
                                    id="app-content", className='flex-1 grid grid-rows-1 grid-cols-2', style={"gridTemplateColumns": "4fr 1fr"})],
                                    className="grid grid-rows-2 grid-cols-1 h-screen w-screen",style={"gridTemplateRows": "1fr 6fr"}, id="layout")
          
        return geojsonEtienne
    def __get__header__(self):
        return html.Div(id="header", className='flex-none bg-black')

    def __get__information_tab__(self):
        return html.Div(id="camp-info", className='')
    def __get__map__(self):
        geodata = dl.GeoJSON(data=self.__get__geojson__(),id="camps")
        map = dl.Map(children=[dl.TileLayer(),geodata], className="h-full w-full", id="map")        
        return html.Div(map, className='w-full h-full')


  


    def loop(self) -> bool:
        #run dash app
        self.app.run_server(debug=True)
        return True
    