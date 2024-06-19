from .audio_player import AudioPlayer

from pynput import keyboard
import time
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
        print("playing tone..")
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
        print("listener stopped.")
        self.ap.stop()
        if self.tone_heard == False:
            print("Tone not heard :(")
        sleep_time = random.gauss(2, 1.2)
        while sleep_time < 0: # make sure number is not negative
            sleep_time = random.gauss(2, 1.2)    
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



    def familiarize(self):
        """main funtion

        Returns:
            boolean: familiarization successfull
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
                    return False
                else:
                    self.level = self.startlevel

            else:
                print("Familiarization successful!")
                # TODO write current level in file
                return True




