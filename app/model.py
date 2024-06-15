from .audio_player import AudioPlayer
import numpy as np
from pynput import keyboard
import time


class Procedure():

    def __init__(self, startlevel, signal_length):
        """The parent class for the familiarization, the main procedure and the short version

        Args:
            startlevel (float): starting level of procedure in dBHL
            signal_length (float): length of played signals in seconds
        """
        self.ap = AudioPlayer()
        self.startlevel = startlevel
        self.level = startlevel
        self.signal_length = signal_length
        self.frequency = 1000
        self.zero_dbhl = 0.00002 # zero_dbhl in absolute numbers. Needs to be calibrated!
        self.tone_heard = False 


    def dbhl_to_volume(self, dbhl):
        """calculate dBHL into absolute numbers

        Args:
            dbhl (float): value in dBHL

        Returns:
            float: value in absolute numbers
        """
        return self.zero_dbhl * 10 ** (dbhl / 10)
    

    def key_press(self, key):
        if key == keyboard.Key.space:
            self.tone_heard = True
            print("Tone heard!")


    def play_tone(self):
        """set tone_heard to False, play beep, then wait 5s(?) for keypress.
        If key is pressed, set tone_heard to True.
        """
        self.tone_heard = False
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length)
        listener = keyboard.Listener(on_press=self.key_press, on_release=None)
        listener.start()
        time.sleep(5) # time to wait for keypress # TODO
        listener.stop()
        if self.tone_heard == False:
            print("Tone not heard :(")



class Familiarization(Procedure):

    def __init__(self, startlevel=40, signal_length=1):
        """familiarization process

        Args:
            startlevel (int, optional): starting level of procedure in dBHL. Defaults to 40.
            signal_length (int, optional): length of played signals in seconds. Defaults to 1.
        """

        super().__init__(startlevel, signal_length)      
        self.fails = 0 # number of times familiarization failed


    def familiarize(self): # TODO Return last level and successfull or unsuccessful
        """main funtion
        """

        while True:

            self.tone_heard = True

            # first loop (always -20dBHL)
            while self.tone_heard == True:
                self.play_tone()
                
                if self.tone_heard == True:
                    self.level -= 20
                else:
                    self.level += 10
            
            # second loop (always +10dBHL)
            while self.tone_heard == False:
                self.play_tone()

                if self.tone_heard == False:
                    self.level += 10

            # replay tone with same level
            self.play_tone()

            if self.tone_heard == False:
                self.fails += 1
                if self.fails >= 2:
                    print("Familiarization unsuccessful. Please read rules and start again.")
                    return None
                else:
                    self.level = self.startlevel

            else:
                print("Familiarization successful!")
                return None




class StandardProcedure(Procedure):
    
    def __init__(self, startlevel=40, signal_length=1):
        """Dummy StandardProcedure class
        """
        # Dummy Results
        # 125, 250, 500, 1000, 2000, 4000, 8000 #Hz
        left = np.array([5, 10, 5, 10, 20, 25, 40]) #dBHL
        right = np.array([10, 10, 10, 15, 20, 25, 50])
        self.results = {"right": right, 
                      "left": left}

    def standard_test(self):
        """Dummy StandardProcedure function

        Returns:
            dict: dummy results of the test"""
        print("Dummy Hearing Test started")
        time.sleep(2)
        print("Dummy Hearing Test done")
        return self.results



