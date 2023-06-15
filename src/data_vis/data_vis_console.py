from data_vis.data_vis import IVisualizer
import os
import sys 
sys.argv.append('..')
from util.text_format import color;
import termios, tty
from data_manipulations.data_editor import DataEditor


def cls():
    if os.name == 'posix':
        _ = os.system('clear')
    elif os.name == 'nt':
        _ = os.system('cls')

class state:
    LISTING=0
    EDITING=1

class Visualizer(IVisualizer):
    def __init__(self, campData, verbose=False):
        IVisualizer.__init__(self, campData, verbose=verbose)
        self.logger.print("Visualizer initialized")
        self.selected = 0
        self.state = state.LISTING
        self.editor = DataEditor(campData, verbose=verbose)
        self.consoleQueue = []

    def __print_listing__(self):
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
    def __print_editing__(self):

        camp = self.data.getCamps()[self.selected]

        #Print header in bold and orange
        print(color.BOLD + color.YELLOW + "Editing camp: " + camp.getName() + color.END)
        print("1. Name: " + camp.getName())
        print("2. Description: " + camp.getDescription())
        print("-" * 20)

        print(" Longitude: " + str(camp.getLon()))
        print(" Latitude: " + str(camp.getLat()))
        print(" Elevation: " + str(camp.getElevation()))

        print()
        print()

        print("Press the number of the field you want to edit")
        print("Press 's' to save") 



    def repaint(self) -> bool:
        self.logger.print("Repainting console...  (State : " + str(self.state) + ")")
        if(not(self.verbose)):
            cls()

        if self.state == state.LISTING:
            self.__print_listing__()
        elif self.state == state.EDITING:
            self.__print_editing__()

        #Depile queue
        while len(self.consoleQueue) != 0:
            mess = self.consoleQueue.pop()
            mess()
        


        return True
                
    def listen_for_text(self):
        # Sauvegarde de la configuration du terminal
            
        # Lecture du texte entré par l'utilisateur
        print("Enter text: (Press Enter to validate)")
        user_input = ""
        while True:
            char = sys.stdin.read(1)
            
            # Si l'utilisateur appuie sur Entrée, on sort de la boucle
            if char == '\r' or char == '\n':
                break
            elif char == '\x7f':
                # Si l'utilisateur appuie sur la touche de suppression (Backspace/Delete)
                # On supprime le dernier caractère du texte de l'utilisateur
                if len(user_input) > 0:
                    user_input = user_input[:-1]
                    # Effacer le caractère précédent dans la console
                    sys.stdout.write('\b \b')
                    print("",end='', flush=True)
            elif char == '\x03':
                # Si l'utilisateur appuie sur Ctrl+C, on interrompt le programme
                raise KeyboardInterrupt()
            else:
                # Ajouter le caractère au texte de l'utilisateur
                user_input += char
                print(char, end='', flush=True)
                
        return user_input
       


    def __navigation__(self, key):
        if not(self.state == state.LISTING):
            return
        self.logger.print("Key pressed: " + str(key))
        if key == '\x1b[A': #down arrow
            if self.selected > 0:
                self.selected -= 1
        elif key == '\x1b[B': #up arrow
            if self.selected < self.data.getSize() - 1:
                self.selected += 1
    def __edit__(self, key):
        if not(self.state == state.EDITING):
            return

        #Check number
        if key == '1':
            self.logger.print("Editing name")
            self.logger.print("Enter new name: ")
            new_name = self.listen_for_text()
            self.editor.modifyAttributeAt(self.selected, new_name,attribute="name")
        elif key == '2':
            self.logger.print("Editing description")
            self.logger.print("Enter new description: ")
            new_description = self.listen_for_text()
            self.editor.modifyAttributeAt(self.selected, new_description,attribute="description")


    def loop(self) -> bool:
        self.repaint()
        # Create a keyboard listener
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        

        # Boucle pour lire les touches jusqu'à obtenir la séquence d'échappement
        while True:
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)

                # Vérifie si la touche est la séquence d'échappement (ASCII: \x1b)
                if key == '\x1b':
                    # Lecture des autres touches dans la séquence d'échappement
                    key += sys.stdin.read(2)
            
                    self.__navigation__(key)
                #Check ctrl+c
                elif key == '\x03':
                    break

                # Check ENTER
                elif key == '\r' and self.state == state.LISTING:
                    self.state = state.EDITING

                # Check backspace 
                elif key == '\x7f' and self.state == state.EDITING:
                    self.state = state.LISTING

                self.__edit__(key)

                if key == 's':
                    code = self.data.saveData()
                    if code == 0:
                        self.consoleQueue.append(lambda : self.logger.printAnyway("Modification Saved"))

                # Traitez la touche selon vos besoins
                # Ici, nous imprimons simplement la touche
                if key == 'q':
                    break
                    
            finally:
                # Rétablit les paramètres du terminal à leur état initial
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                self.repaint()
        


           
            