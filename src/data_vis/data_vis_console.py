from data_vis.data_vis import Visualizer
import os
import sys 
sys.argv.append('..')
from util.text_format import color;
from pynput import keyboard
def cls():
    #clear stdout
    sys.stdout.write("\033[2J\033[1;1H")
    #clear screen
    os.system('cls' if os.name=='nt' else 'clear')

class VisualizerConsole(Visualizer):
    def __init__(self, campData, verbose=False):
        Visualizer.__init__(self, campData, verbose=verbose)
        self.logger.print("VisualizerConsole initialized")
        self.selected = 0

    def repaint(self) -> bool:
        self.logger.print("Repainting console...")
        if(not(self.verbose)):
            cls()
        data_camps = self.data.getCamps()

        camps = []
        for i in range(self.data.getSize()):
            camp = []
            camp.append(str(i))
            camp.append(data_camps[i].getName())
            camp.append(data_camps[i].getDescription())
            camp.append(data_camps[i].getLon())
            camp.append(data_camps[i].getLat())
            camp.append(data_camps[i].getElevation())
            camps.append(camp)
        

        max_len = [0, 0, 0, 0, 0, 0]
        #header
        header = ["N°","Name", "Description", "Longitude", "Latitude", "Elevation"]
        
        for i in range(len(camps)):
            for j in range(len(camps[i])):
                if len(str(camps[i][j])) > max_len[j]:
                    max_len[j] = len(str(camps[i][j]))
        for i in range(len(header)):
            if max_len[i] < len(header[i]):
                max_len[i] = len(header[i])
        for i in range(len(camps)):
            for j in range(len(camps[i])):
                color_tag = color.END if i != self.selected else color.BOLD
                camps[i][j] =color_tag + str(camps[i][j]) + " " * (max_len[j] - len(str(camps[i][j]))) + color.END
        
        

        for i in range(len(header)):
            header[i] = header[i] + " " * (max_len[i] - len(header[i]))
        header = "|".join(header)
        print(header)
        print("-" * len(header))

        #data
        for i in range(len(camps)):
            print("|".join(camps[i]))


        return True
    
    def __navigation__(self, key):
        if key == keyboard.Key.up:
            if self.selected > 0:
                self.selected -= 1
        elif key == keyboard.Key.down:
            if self.selected < self.data.getSize() - 1:
                self.selected += 1 
        elif key == keyboard.Key.esc:
            self.listener.stop()

        
        self.repaint()
        


    def loop(self) -> bool:
        self.repaint()
        with keyboard.Listener(on_press=self.__navigation__) as listener:
            self.listener = listener
            listener.join()


        return True

