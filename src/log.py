
class Log:
    def __init__(self, verbose=False,header="[LOG]"):
        self.verbose = verbose
        self.header = header
    def print(self, message):
        '''Print message if verbose is true'''
        if self.verbose:
            print(self.header + " : ",end='')
            print(message)
    def printAnyway(self, message):
        '''Print message anyway'''
        print(self.header + " : ",end='')
        print(message)
    def error(self, message):
        '''Print error with red color'''
        print("\033[91m" + "[ERROR] " + message + "\033[0m")
class Logger:
    def __init__(self, verbose=False,header="[LOG]"):
        self.verbose = verbose
        self.header = header
        self.logger = Log(verbose=verbose,header=header)