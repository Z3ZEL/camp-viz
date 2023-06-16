from camp_data import CampData
from log import Logger
class IVisualizer(Logger):
    def __init__(self, campData : CampData, verbose=False):
        Logger.__init__(self,verbose=verbose, header="[Visualizer]")
        self.data = campData

    def repaint(self) -> bool:
        pass
    
    def loop(self) -> bool:
        pass