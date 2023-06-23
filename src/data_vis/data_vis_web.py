import dotenv
from data_vis.data_vis import IVisualizer

import sys
sys.argv.append('..')
from camp_data import CampData, Camp

from dash import Dash
import dash_leaflet as dl
from dash import html, dcc
from dash.dependencies import Input, Output, State
class Vis_State:
    VIEW=0
    EDITING=1
class Visualizer(IVisualizer):
    app = None
    def __init__(self, campData: CampData, verbose=False):
        super().__init__(campData, verbose)
        self.selected_camp : Camp = None    
        self.state = Vis_State.VIEW
        self.app = Dash(__name__,suppress_callback_exceptions=True,external_scripts=[{'src': 'https://cdn.tailwindcss.com'}], external_stylesheets=[{'href':'https://cdn.jsdelivr.net/npm/daisyui@3.1.1/dist/full.css', 'rel':'stylesheet', 'type':'text/css'}])
        
        #LAYOUT
        self.app.layout = html.Div(self.__get_layout__(),id="layout")
        self.app.title = "Camp Data Visualizer"
    
        #Add script
        #disable server locally
        self.app.css.config.serve_locally = True
        self.app.scripts.config.serve_locally = True

        ##INIT CALLBACKS
        @self.app.callback(Output("camp-desc", "children"), [Input("camps", "click_feature")])
        def __map_click__desc__(feature):
            if feature is not None:
                return f"{feature['properties']['description']}"
            else:
                return ""
        @self.app.callback(Output("camp-name", "children"), [Input("camps", "click_feature")])
        def __map_click__name__(feature):
            if feature is not None:
                self.selected_camp = self.data.getCamps()[feature['properties']['index']]
                return f"{feature['properties']['name']}"
            else:
                self.selected_camp = None
                return "Click a point on the map"
    def __get__number__without_desc__(self):
        n = 0
        for camp in self.data.getCamps():
            if camp.getDescription() == "":
                n += 1
        return n
    def __get__geojson__(self):
        '''Convert all camp to a geojson object'''
        geojson = {"type":"FeatureCollection", "features":[]}
        camps = self.data.getCamps()
        for i in range(len(self.data.getCamps())):
            tmp = camps[i].toGeoJSON()
            tmp["properties"]["name"] = camps[i].getName()
            tmp["properties"]["description"] = camps[i].getDescription()
            tmp["properties"]["tooltip"] = camps[i].getName()
            tmp["properties"]["index"] = i
            
            geojson["features"].append(tmp) 

        self.logger.print("Geojson initialized")
        return geojson

    
    ##GET LAYOUT
    def __get_layout__(self):
        #append camp
        return html.Div([html.Div(self.__get__header__(),id="header"), 
                         html.Div([html.Div(self.__get__map__(), id="map"),
                                    self.__get__information_tab__()],
                                    id="app-content", className='flex-1 grid grid-rows-1 grid-cols-2', style={"gridTemplateColumns": "4fr 1fr"})],
                                    className="grid grid-rows-2 grid-cols-1 h-screen w-screen",style={"gridTemplateRows": "1fr 5fr"})
          
    def __get__header__(self):
        return html.Div([
            html.Div([
                html.Div("Camps",className='stat-title'),
                html.Div(self.data.getSize(), className='stat-value'),
                html.Div('Number of camps', className='stat-desc')],
            className="stat shadow shadow-lg p-4 m-4 bg-base-100 rounded-box flex mx-auto flex-col items-center justify-center w-32"),
            html.Div([
                html.Div("Empty camps",className='stat-title'),
                html.Div(
                    html.Div(self.__get__number__without_desc__(), style={'--value':str(len(self.data.getCamps()) - self.__get__number__without_desc__())}, className='radial-progress text-error'),
            className='stat-value'),
                html.Div('Number of camps without description', className='stat-desc')],
            className="stat shadow shadow-lg p-4 m-4 bg-base-100 rounded-box flex mx-auto flex-col items-center justify-center w-64 h-32")
            ]
        ,className='stats flex-none w-full')

    def __get__information_tab__(self):
        self.logger.print("State : " + str(self.state))
        form = html.Div([
                html.Div([
                html.Label("Name", className='label'),
                dcc.Input(value='',className='input input-bordered', placeholder='', id='form-name'),
                html.Label("Description", className='label'),
                dcc.Textarea(value='', className='textarea textarea-bordered', placeholder="", id='form-description'),
                ], className='form-control'),
                html.Button("Save", className='btn m-6 flex w-32 mx-auto btn-outline btn-alert', id='form-button'),
            ])
        info = html.Div([
            html.Div([
                html.Div("No point selected", className='card-title', id="camp-name"),
                html.Div("Click a point on the map", className='', id="camp-desc"),
            ], className='card shadow m-6 p-6'),
            html.Button("Edit", className='btn m-6 flex w-32 mx-auto btn-outline btn-info', id='edit-button'),
            html.Div(form,className='card shadow m-6 p-6', id='camp-edit-form', hidden=True),
            html.Div(id='form-output', className='card shadow m-6 p-6 text-center')
            ], id="camp-info", className='')
        
        #VISUAL APPARENCE OF EDIT BUTTON  
        #FORM CALLBACKS
        @self.app.callback([Output('camp-edit-form','hidden', allow_duplicate=True),Output("edit-button","children", allow_duplicate=True)], [Input('edit-button','n_clicks')], prevent_initial_call=True)
        def __edit_button_toggle_form__(n_clicks):
            if (n_clicks is not None )and self.selected_camp is not None:
                if self.state == Vis_State.VIEW:
                    self.state = Vis_State.EDITING
                    return [False, "Cancel"]
                else:
                    self.state = Vis_State.VIEW
                    return [True, "Edit"]
            else:
                return [True, "Edit"]
            
        @self.app.callback([Output('form-name','value'),Output('form-description','value')], [Input('edit-button','n_clicks')])
        def __edit_button_name__(n_clicks):
            if (n_clicks is not None) and self.selected_camp is not None:
                return [self.selected_camp.getName(), self.selected_camp.getDescription()]
            else:
                return ["", ""]
        
            

        @self.app.callback(
                        [
                        Output('camp-edit-form','hidden'),
                        Output('edit-button','children'),    
                        Output('form-output','hidden'),
                        Output('form-output','children'),
                        Output('camps','data'),
                        Output('header', 'children')],
                        [Input('form-button','n_clicks')],
                        [State('form-name', 'value'), State('form-description','value')],
                    )
        def __form_event_edit__(n_clicks, new_name, new_description):
            
            self.logger.print(f"Saving callback with {new_name} and {new_description}")
            if n_clicks is not None:
                new_camp = self.selected_camp.getCopy().toDict()
                new_camp['name'] = new_name
                new_camp['description'] = new_description

                self.data.modifyCamp(self.selected_camp, Camp.fromDict(new_camp))
                code = self.data.saveData()
                if code == -1:
                    return [True, "Edit",False,'There was an error during saving data', self.__get__geojson__(), self.__get__header__()]
                else:
                    return [True, "Edit", False, 'Saved !', self.__get__geojson__(), self.__get__header__()]
            else:
                return [True,"Edit",True,'No camp to save', self.__get__geojson__(), self.__get__header__()]
    

        return info
    def __get__map__(self):
        geodata = dl.GeoJSON(data=self.__get__geojson__(),id="camps")

        tile_url = None
        attribution = None
        tile_size = 256
        #Get IGN KEY from env
        env = dotenv.dotenv_values(".env")
        
        if "IGN_KEY" in env.keys():
            tile_url = ("https://wxs.ign.fr/CLEF/geoportail/wmts?" +
                        "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                        "&STYLE=normal" +
                        "&TILEMATRIXSET=PM" +
                        "&FORMAT=image/png"+
                        "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"+
                        "&TILEMATRIX={z}" +
                        "&TILEROW={y}" +
                        "&TILECOL={x}")
            tile_url = tile_url.replace("CLEF", env["IGN_KEY"])
            tile_size = 256
            attribution = "© IGN-F/Geoportail"
        else:
            tile_url = ("https://tile.openstreetmap.org/{z}/{x}/{y}.png")
            attribution = "Map data © OpenStreetMap contributors"

        center = []
        if self.data.getCamps() is not None and len(self.data.getCamps()) > 0:
            center = [self.data.getCamps()[0].getLat(), self.data.getCamps()[0].getLon()]
        else:
            center = [0,0]

        self.map = dl.Map(children=[dl.TileLayer(url=tile_url, minZoom=0, maxZoom=18, attribution=attribution, tileSize=tile_size),geodata], center=center,zoomControl=False,zoom=5, style={ 'height': '80vh', 'width': '100%', 'margin': "auto", 'display': 'block'})   
            
        return html.Div(self.map, className='w-full h-full object-fit p-2 shadow shadow-lg rounded-box flex items-center justify-center')

    def loop(self) -> bool:
        #run dash app
        self.app.run(debug=True)
        return True
    
    