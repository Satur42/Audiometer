#from .audio_player import AudioPlayer
from audio_player import AudioPlayer

from pynput import keyboard
import time
import numpy as np
import random


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
        #   print("playing tone..")
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length)
        listener = keyboard.Listener(on_press=self.key_press, on_release=None)
        listener.start()
        current_wait_time = 0
        max_wait_time = 4000 # in ms 
        step_size = 50 # in ms
        while current_wait_time < max_wait_time and self.tone_heard == False: # wait for keypress
            time.sleep(step_size / 1000)
            current_wait_time += step_size
        listener.stop()
        #print("listener stopped.")
        self.ap.stop()
        if self.tone_heard == False:
            print("Tone not heard :(")
        sleep_time = np.abs(random.gauss(2, 1.2))

        time.sleep(sleep_time) # wait before next tone is played. #TODO test times



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
            while self.tone_heard:
                self.play_tone()
                
                if self.tone_heard:
                    self.level -= 20
                else:
                    self.level += 10
            
            # second loop (always +10dBHL)
            while not self.tone_heard:
                self.play_tone()

                if not self.tone_heard:
                    self.level += 10

            # replay tone with same level
            self.play_tone()

            if not self.tone_heard:
                self.fails += 1
                if self.fails >= 2:
                    print("Familiarization unsuccessful. Please read rules and start again.")
                    return None
                else:
                    self.level = self.startlevel

            else:
                print("Familiarization successful!")
                return None


class Test(Procedure):

    def __init__(self, startlevel=40, signal_length=1):

        super().__init__(startlevel, signal_length)
        self.frequencies = [1000, 2000, 4000, 8000, 500, 250, 125]
        self.current_frequency_index = 0
        self.run_count = 0
        self.hearing_thresholds = {freq: None for freq in self.frequencies}  # TODO               
    

    def run_test(self, freq):
        self.frequency = freq
        self.level = self.startlevel
        self.levels = {}
        self.run_count = 0
        stop_outer_loop = False

        while not stop_outer_loop:
            self.tone_heard = True
            self.run_count += 1
            print(f"Run {self.run_count} for frequency {freq}.")

            while self.tone_heard:
                if self.level not in self.levels:
                    self.levels[self.level] = 0

                print(f"playing tone at {self.level} dBHL.")
                self.play_tone()

                if self.tone_heard:
                    self.levels[self.level] += 1
                    print(f"Tone heard for the {self.levels[self.level]} time(s)." )     
                    self.level -= 10
                else:
                    self.level += 5

            while not self.tone_heard:
                if self.level not in self.levels:
                    self.levels[self.level] = 0

                print(f"playing tone at {self.level} dBHL.")           
                self.play_tone()

                if not self.tone_heard:
                    self.level += 5

                elif self.levels[self.level] >= 2 and self.run_count < 5:
                    print("3x gleicher Pegel bei maximal fünf Durchgängen!  ")
                    self.hearing_thresholds[freq] = self.level
                    stop_outer_loop = True
                    break

                elif self.run_count >= 5:
                    self.levels[self.level] += 1
                    print(f"Tone heard for the {self.levels[self.level]} time(s)." )

                else:
                    self.levels[self.level] += 1
                    print(f"Tone heard for the {self.levels[self.level]} time(s)." )  
                    self.level += 10
                    self.run_count = 0
            if stop_outer_loop:
                break


    def run_all_tests(self):
        # TODO nochmal nachlesen in welcher Reihenfolge und Ohren etc.
        for freq in self.frequencies:
            self.run_test(freq)
        print(self.hearing_thresholds)
        return self.hearing_thresholds  


test = Test()
test.run_test(1000)

