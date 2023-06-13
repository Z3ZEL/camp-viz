from log import Logger
from camp_data import CampData, Camp


class DataEditor(Logger):
    def __init__(self, campData:CampData, autoSaving=False, verbose=False):
        self.data = campData
        Logger.__init__(self, verbose=verbose,header='[DATA EDITOR]')
    def modifyAttributeAt(self, index, val, attribute='name'):
        campToModifyDic = self.data.getCamps()[index].toDict()
        campToModifyDic[attribute] = val
        self.data.modifyCamp(self.data.getCamps()[index], Camp.fromDict(campToModifyDic))
        #TODO: Handle error here



        