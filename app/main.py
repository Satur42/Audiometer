from .ui import setup_ui
from .model import *
#from .dummy_model import *
from .audiogramm import create_audiogram

class Controller():

    def __init__(self):
        self.familiarization = Familiarization()
        self.standard_procedure = StandardProcedure()
        self.view = setup_ui(self.start_familiarization, 
                             self.start_standard_procedure) # add more procedures later

    def run_app(self):
        self.view.mainloop()

    def start_familiarization(self):
        self.familiarization.familiarize()

    def start_standard_procedure(self):
        self.standard_procedure.standard_test()
