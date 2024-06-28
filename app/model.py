from .audio_player import AudioPlayer

from pynput import keyboard
import time
import random
import tempfile as tfile
import csv


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
        self.freq_bands = ['125', '250', '500', '1000', '2000', '4000', '8000']
        self.side = 'lr'


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
        """set tone_heard to False, play beep, then wait max 4s for keypress.
        If key is pressed, set tone_heard to True.
        Then wait for around about 2s (randomized).
        """
        self.tone_heard = False
        print("playing tone..")
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length, self.side)
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
        else:
            sleep_time = random.uniform(1, 2.5) # random wait time vetween 1 and 2.5
            time.sleep(sleep_time) # wait before next tone is played. #TODO test times

    
    def create_temp_csv(self, id="", **aditional_data):
        """creates a temporary CSV file with the relevant frequency bands as a header
        and NaN in the second and third line as starting value for each band.
        (second line: left ear, third line: right ear)
        ID and additional data will be stored in subsequent lines in the format: key, value.

        Args:
            id (string, optional): id to be stored, that will later be used for naming exported csv file

        Returns:
            str: name of temporary file
        """
        with tfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv') as temp_file:
            # Define the CSV writer
            csv_writer = csv.writer(temp_file)

            # Write header
            csv_writer.writerow(self.freq_bands)

            # Write value NaN for each frequency in second and third row
            csv_writer.writerow(['NaN' for i in range(len(self.freq_bands))])
            csv_writer.writerow(['NaN' for i in range(len(self.freq_bands))])

            # Write id and additional data
            if id:
                csv_writer.writerow(["id", id])
            if aditional_data:
                for i in aditional_data:
                    csv_writer.writerow([i, aditional_data[i]])


            return temp_file.name
        
        
    def add_to_temp_csv(self, value, frequency, side, temp_filename):
        """add a value in for a specific frequency to the temporary csv file

        Args:
            value (str): level in dBHL at specific frequency
            frequency (str): frequency where value should be added
            side (str): specify which ear ('l' or 'r')
            temp_filename (str): name of temporary csv file
        """
        # Read all rows from the CSV file
        with open(temp_filename, mode='r', newline='') as temp_file:
            dict_reader = csv.DictReader(temp_file)
            rows = list(dict_reader)

        # Update the relevant row based on the side parameter
        if side == 'l':
            rows[0][frequency] = value
        elif side == 'r':
            rows[1][frequency] = value

        # Write all rows back to the CSV file
        with open(temp_filename, mode='w', newline='') as temp_file:
            dict_writer = csv.DictWriter(temp_file, fieldnames=self.freq_bands)
            dict_writer.writeheader()
            dict_writer.writerows(rows)

        print(rows[0], rows[1])
        for i in rows[2:]:
            print(i['125'], i['250'])


    
    def get_value_from_csv(self, frequency, temp_filename, side='l'):
        """get the value at a specific frequency from the temporary csv file

        Args:
            frequency (str): frequency where value is stored
            temp_filename (str): name of temporary csv file
            side (str, optional): specify which ear ('l' or 'r'). Defaults to 'l'.

        Returns:
            str: dBHL value at specified frequency
        """
        with open(temp_filename, mode='r', newline='') as temp_file:
            dict_reader = csv.DictReader(temp_file)
            freq_dict = next(dict_reader) # left ear
            if side == 'r': # go to next line if right side
                freq_dict = next(dict_reader)    
            return freq_dict[frequency]





class Familiarization(Procedure):

    def __init__(self, startlevel=40, signal_length=1, id="", **additional_data):
        """familiarization process

        Args:
            startlevel (int, optional): starting level of procedure in dBHL. Defaults to 40.
            signal_length (int, optional): length of played signals in seconds. Defaults to 1.
        """

        super().__init__(startlevel, signal_length)      
        self.fails = 0 # number of times familiarization failed
        self.tempfile = self.create_temp_csv(id=id, **additional_data) # create a temporary file to store level at frequencies

    def update_progress(self, value):
        if self.progress_callback:
            self.progress_callback(value)

    def get_temp_csv_filename(self):
        return self.tempfile

    def familiarize(self):
        """main funtion

        Returns:
            bool: familiarization successfull
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
                self.add_to_temp_csv(self.level, '1000', 'l', self.tempfile)
                return True




class StandardProcedure(Procedure):

    def __init__(self, temp_filename, signal_length=1):
        """standard audiometer process (rising level)

        Args:
            temp_filename (str): name of temporary csv file where starting level is stored and future values will be stored
            signal_length (int, optional): length of played signal in seconds. Defaults to 1.
        """
        startlevel = int(self.get_value_from_csv('1000', temp_filename)) - 10 # 10 dB under level from familiarization
        super().__init__(startlevel, signal_length)
        self.temp_filename = temp_filename
        self.freq_order = [1000, 2000, 4000, 8000, 500, 250, 125] # order in which frequencies are tested

    def standard_test(self):
        """main funtion

        Returns:
            bool: test successfull
        """

        self.side = 'l'
        success_l = self.standard_test_one_ear()
        self.side = 'r'
        success_r = self.standard_test_one_ear()
        if success_l and success_r:
            return True
        else:
            return False

        
    def standard_test_one_ear(self):
        """audiometer for one ear

        Returns:
            bool: test successfull
        """
        success = []
        # test every frequency
        for f in self.freq_order:
            print(f"Testing frequeny {f} Hz")
            s = self.standard_test_one_freq(f)
            success.append(s)

        # retest 1000 Hz (and more frequencies if discrepancy is too high)
        for f in self.freq_order:
            print(f"Retest at frequeny {f} Hz")
            s = self.standard_test_one_freq(f, retest=True)
            if s == True:
                break

        if all(success):
            return True
        
        else:
            return False


    def standard_test_one_freq(self, freq, retest=False):
        """test for one frequency

        Args:
            freq (int): frequency at which hearing is tested
            retest (bool, optional): Is this the retest at the end of step 3 according to DIN. Defaults to False

        Returns:
            bool: test successfull
        """

        self.tone_heard = False
        self.frequency = freq
        self.level = self.startlevel

        # Step 1 (raise tone in 5 dB steps until it is heard)
        while self.tone_heard == False:
            self.play_tone()
            if self.tone_heard == False:
                self.level += 5

        # Step 2
        answers = []
        tries = 0

        while tries < 6:

            # reduce in 10dB steps until no answer
            while self.tone_heard == True:
                self.level -= 10
                self.play_tone()

            # raise in 5 dB steps until answer
            while self.tone_heard == False:
                self.level += 5
                self.play_tone()

            tries += 1
            answers.append(self.level)
            print(f"Try nr {tries}: level: {self.level}")

            if answers.count(self.level) >= 2:
                if retest == True:
                    if abs(self.level - int(self.get_value_from_csv(str(self.frequency), self.temp_filename, self.side))) > 5:
                        self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                        return False
                    else:
                        self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                        return True

                # TODO Wenn Streuung mehr als 10 dB: Vermerk im Audiogramm
                self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                return True
            
            # no three same answers in five tries
            if tries == 3:
                self.level += 10
                self.play_tone()
                answers = []

        print("Something went wrong, please try from the beginning again.")
        return False

        


        
                

