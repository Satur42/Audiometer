import os
from datetime import datetime
import csv
import random
import time
from pynput import keyboard
import tempfile as tfile
import numpy as np
from .audio_player import AudioPlayer
from .audiogram import create_audiogram


class Procedure:

    def __init__(self, startlevel, signal_length, headphone_name="Sennheiser_HDA200", calibrate=True):
        """The parent class for the familiarization, the main procedure, and the screening.

        Args:
            startlevel (float): starting level of procedure in dB HL
            signal_length (float): length of played signals in seconds
        """
        self.ap = AudioPlayer()
        self.startlevel = startlevel
        self.level = startlevel
        self.signal_length = signal_length
        self.frequency = 1000
        self.zero_dbhl = 0.000005 # zero_dbhl in absolute numbers. Needs to be calibrated!
        self.tone_heard = False
        self.freq_bands = ['125', '250', '500', '1000', '2000', '4000', '8000']
        
        #TODO das als default, aber  variabel in der GUI?
        self.freq_levels = {125: 20, 250: 20, 500: 20, 1000: 20, 2000: 20, 4000: 20, 8000: 20} # screening levels
        self.side = 'l'
        self.test_mode = True # TODO turn off for delivery
        self.jump_to_end = False
        self.use_calibration = calibrate
        self.progress = 0 # value for progressbar

        self.retspl = self.get_retspl_values(headphone_name)
        self.calibration = self.get_calibration_values()
        self.save_path = os.getcwd()  # Initialize save_path


    def get_retspl_values(self, headphone_name):
        """Read the correct RETSPL values from the retspl.csv file

        Args:
            headphone_name (str): exact name of headphone as it appears in csv file

        Returns:
            dict of int:float : RETSPL values for each frequency band from 125 Hz to 8000 Hz
        """
        file_name = 'retspl.csv'
        
        # Check if the CSV file exists
        if not os.path.isfile(file_name):
            print(f"File '{file_name}' not found.")
            return
        
        retspl_values = {}
        
        try:
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['headphone_model'] == headphone_name:
                        retspl_values[int(row['frequency'])] = float(row['retspl'])
        except Exception as e:
            print(f"Error reading the file: {e}")
            return
        
        # Check if the headphone model was found
        if not retspl_values:
            print(f"Headphone model '{headphone_name}' not found.")
            return
        
        print(retspl_values)
        return retspl_values
    

    def get_calibration_values(self):
        """Read the correct calibration values from the calibration.csv file.

        Returns:
            dict of int:float : calibration values for each frequency band from 125 Hz to 8000 Hz
        """
        file_name = 'calibration.csv'
        
        # Check if the CSV file exists
        if not os.path.isfile(file_name):
            print(f"File '{file_name}' not found.")
            return
        
        try:
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                calibration_str_values_l = next(reader)
                calibration_str_values_r = next(reader)
                
                # convert dictionary to int:float and put into extra dictionary for left and right side
                calibration_values = {}
                calibration_values['l'] = {int(k): float(v) for k, v in calibration_str_values_l.items()}
                calibration_values['r'] = {int(k): float(v) for k, v in calibration_str_values_r.items()}
                
                # if both sides are used, calculate average between both sides
                calibration_values['lr'] = {}
                for k, v in calibration_values['l'].items():
                    calibration_values['lr'][k] = (10 * np.log10((10 ** (v / 10) + 10 ** (calibration_values['r'][k] / 10)) / 2))
        
        except Exception as e:
            print(f"Error reading the file: {e}")
            return
        
        print(calibration_values)
        return calibration_values


    def dbhl_to_volume(self, dbhl):
        """Calculate dB HL into absolute numbers.

        Args:
            dbhl (float): value in dB HL

        Returns:
            float: value in absolute numbers
        """
        if self.use_calibration:
            # add RETSPL and values from calibration file at that frequency
            dbspl = dbhl + self.retspl[self.frequency] - self.calibration[self.side][self.frequency] 
        else:
            # only add RETSPL
            dbspl = dbhl + self.retspl[self.frequency] 

        return self.zero_dbhl * 10 ** (dbspl / 20) # calculate from dB to absolute numbers using the reference point self.zero_dbhl
    

    def key_press(self, key):
        if key == keyboard.Key.space:
            self.tone_heard = True
            print("Tone heard!")
        elif self.test_mode and key == keyboard.Key.right:
            self.jump_to_end = True
        

    def play_tone(self):
        """Set tone_heard to False, play beep, then wait max 4s for keypress.
        If key is pressed, set tone_heard to True.
        Then wait for around about 2s (randomized).
        """
        self.tone_heard = False
        print(self.frequency, "Hz - playing tone at", self.level, "dBHL.")
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length, self.side)
        listener = keyboard.Listener(on_press=self.key_press, on_release=None)
        listener.start()
        current_wait_time = 0
        max_wait_time = 4000 # in ms 
        step_size = 50 # in ms
        while current_wait_time < max_wait_time and not self.tone_heard: # wait for keypress
            time.sleep(step_size / 1000)
            current_wait_time += step_size
        listener.stop()
        self.ap.stop()
        if not self.tone_heard:
            print("Tone not heard :(")
        else:
            sleep_time = random.uniform(1, 2.5) # random wait time between 1 and 2.5
            time.sleep(sleep_time) # wait before next tone is played. #TODO test times

    
    def create_temp_csv(self, id="", **additional_data):
        """Creates a temporary CSV file with the relevant frequency bands as a header
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
            csv_writer.writerow(['NaN' for _ in range(len(self.freq_bands))])
            csv_writer.writerow(['NaN' for _ in range(len(self.freq_bands))])

            # Write id and additional data
            if id:
                csv_writer.writerow(["id", id])
            if additional_data:
                for key, value in additional_data.items():
                    csv_writer.writerow([key, value])

            return temp_file.name
        
        
    def add_to_temp_csv(self, value, frequency, side, temp_filename):
        """Add a value in for a specific frequency to the temporary csv file

        Args:
            value (str): level in dB HL at specific frequency
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
        else:
            rows[0][frequency] = value
            rows[1][frequency] = value

        # Write all rows back to the CSV file
        with open(temp_filename, mode='w', newline='') as temp_file:
            dict_writer = csv.DictWriter(temp_file, fieldnames=self.freq_bands)
            dict_writer.writeheader()
            dict_writer.writerows(rows)

        print(rows[0], rows[1])
        
        for row in rows[2:]:
            print(row['125'], row['250'])


    def get_value_from_csv(self, frequency, temp_filename, side='l'):
        """Get the value at a specific frequency from the temporary csv file.

        Args:
            frequency (str): frequency where value is stored
            temp_filename (str): name of temporary csv file
            side (str, optional): specify which ear ('l' or 'r'). Defaults to 'l'.

        Returns:
            str: dB HL value at specified frequency
        """
        with open(temp_filename, mode='r', newline='') as temp_file:
            dict_reader = csv.DictReader(temp_file)
            freq_dict = next(dict_reader) # left ear
            if side == 'r': # go to next line if right side
                freq_dict = next(dict_reader)    
            return freq_dict[frequency]
        


    def create_final_csv_and_audiogram(self, temp_filename, binaural=False):
        """Creates a permanent CSV file and audiogram from the temporary file.

        Args:
            temp_filename (str): Name of the temporary CSV file.
            binaural (bool): If the test is binaural.
        """
        # Read the temporary file
        with open(temp_filename, mode='r', newline='') as temp_file:
            dict_reader = csv.DictReader(temp_file)
            rows = list(dict_reader)

        # Get date and time
        now = datetime.now()
        date_str = now.strftime("%Y%m%d_%H%M%S")
        try:
            id = rows[2]['250']
        except:
            id = "missingID"

        # Create folder for the subject
        folder_name = os.path.join(self.save_path, f"{id}")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        final_csv_filename = os.path.join(folder_name, f"{id}_audiogramm_{date_str}.csv")

        # Write the permanent CSV file
        with open(final_csv_filename, mode='x', newline='') as final_file:
            dict_writer = csv.DictWriter(final_file, fieldnames=self.freq_bands)
            dict_writer.writeheader()
            dict_writer.writerows(rows)

        freqs = [int(x) for x in self.freq_bands]

        left_levels = [self.parse_dbhl_value(rows[0][freq]) for freq in self.freq_bands]
        right_levels = [self.parse_dbhl_value(rows[1][freq]) for freq in self.freq_bands]

        # Generate the audiogram filename
        audiogram_filename = os.path.join(folder_name, f"{id}_audiogram_{date_str}.png")
        print(left_levels, right_levels)
        create_audiogram(freqs, left_levels, right_levels, binaural=binaural, name=audiogram_filename, freq_levels=self.freq_levels)


    def parse_dbhl_value(self, value):
        """Parses the dBHL value from the CSV file.

        Args:
            value (str): the value from the CSV file

        Returns:
            int or None: the parsed value or None if 'NH'
        """
        if value == 'NH':
            return 'NH'
        try:
            return int(value)
        except ValueError:
            return None
        

    
    def get_progress(self):
        """gets the current progress

        Returns:
            float: progress value between 0.0 and 1.0
        """
        return self.progress



class Familiarization(Procedure):

    def __init__(self, startlevel=40, signal_length=1, headphone_name="Sennheiser_HDA200", calibrate=True, id="", **additional_data):
        """Familiarization process

        Args:
            startlevel (int, optional): starting level of procedure in dB HL. Defaults to 40.
            signal_length (int, optional): length of played signals in seconds. Defaults to 1.
        """
        super().__init__(startlevel, signal_length, headphone_name=headphone_name, calibrate=calibrate)      
        self.fails = 0 # number of times familiarization failed
        self.tempfile = self.create_temp_csv(id=id, **additional_data) # create a temporary file to store level at frequencies


    def get_temp_csv_filename(self):
        return self.tempfile


    def familiarize(self):
        """Main function

        Returns:
            bool: familiarization successful
        """
        while True:
            self.progress = 0.01
            self.tone_heard = True

            # first loop (always -20dBHL)
            while self.tone_heard:
                self.play_tone()

                if self.jump_to_end == True:
                    for f in self.freq_bands:
                        self.add_to_temp_csv(20, f, 'lr', self.get_temp_csv_filename())
                    return True
                
                if self.tone_heard:
                    self.level -= 20
                else:
                    self.level += 10

            self.progress = 1/3        
            
            # second loop (always +10dBHL)
            while not self.tone_heard:
                self.play_tone()
                if not self.tone_heard:
                    self.level += 10

            self.progress = 2/3

            # replay tone with same level
            self.play_tone()

            if not self.tone_heard:
                self.fails += 1
                if self.fails >= 2:
                    self.progress = 1
                    print("Familiarization unsuccessful. Please read rules and start again.")
                    return False
                else:
                    self.level = self.startlevel

            else:
                print("Familiarization successful!")
                self.progress = 1
                self.add_to_temp_csv(self.level, '1000', 'l', self.tempfile)
                return True
            

class StandardProcedure(Procedure):

    def __init__(self, temp_filename, signal_length=1, headphone_name="Sennheiser_HDA200", calibrate=True):
        """Standard audiometer process (rising level).

        Args:
            temp_filename (str): name of temporary csv file where starting level is stored and future values will be stored
            signal_length (int, optional): length of played signal in seconds. Defaults to 1.
        """
        startlevel = int(self.get_value_from_csv('1000', temp_filename)) - 10 # 10 dB under level from familiarization
        super().__init__(startlevel, signal_length, headphone_name=headphone_name, calibrate=calibrate)
        self.temp_filename = temp_filename
        self.freq_order = [1000, 2000, 4000, 8000, 500, 250, 125] # order in which frequencies are tested
        
        self.progress_step = 0.95 / 14


    def standard_test(self, binaural=False):
        """Main function

        Returns:
            bool: test successful
        """

        if not binaural:
            self.side = 'l'
            
            success_l = self.standard_test_one_ear()

            if self.test_mode == True and self.jump_to_end == True:
                self.create_final_csv_and_audiogram(self.temp_filename, binaural)
                self.progress = 1
                return True
            
            self.side = 'r'
            success_r = self.standard_test_one_ear()

            if success_l and success_r:
                self.create_final_csv_and_audiogram(self.temp_filename, binaural)
                self.progress = 1
                return True
        
        if binaural:
            self.progress_step = 0.95 / 7
            self.side = 'lr'
            success_lr = self.standard_test_one_ear()

            if self.test_mode == True and self.jump_to_end == True:
                self.create_final_csv_and_audiogram(self.temp_filename, binaural)
                self.progress = 1
                return True
            
            if success_lr:
                self.create_final_csv_and_audiogram(self.temp_filename, binaural)
                self.progress = 1
                return True

        return False

        
    def standard_test_one_ear(self):
        """Audiometer for one ear

        Returns:
            bool: test successful
        """
        success = []

        self.tone_heard = False
        self.frequency = 1000
        self.level = self.startlevel

        # Step 1 (raise tone in 5 dB steps until it is heard)
        while not self.tone_heard:
            self.play_tone()

            if self.test_mode == True and self.jump_to_end == True:
                return True

            if not self.tone_heard:
                self.level += 5
        
        self.startlevel = self.level
        print(f"Starting level: {self.startlevel} dBHL")

        # test every frequency
        for f in self.freq_order:
            print(f"Testing frequency {f} Hz")
            s = self.standard_test_one_freq(f)

            if self.test_mode == True and self.jump_to_end == True:
                return True
            
            success.append(s)

        # retest 1000 Hz (and more frequencies if discrepancy is too high)
        for f in self.freq_order:
            print(f"Retest at frequency {f} Hz")
            s = self.standard_test_one_freq(f, retest=True)
            if s:
                break

        if all(success):
            return True
        
        else:
            return False


    def standard_test_one_freq(self, freq, retest=False):
        """Test for one frequency

        Args:
            freq (int): frequency at which hearing is tested
            retest (bool, optional): this is the retest at the end of step 3 according to DIN. Defaults to False

        Returns:
            bool: test successful
        """
        self.tone_heard = True
        self.frequency = freq
        self.level = self.startlevel

        # Step 2
        answers = []
        tries = 0

        while tries < 6:
            # reduce in 10dB steps until no answer
            while self.tone_heard:
                self.level -= 10
                self.play_tone()

            # raise in 5 dB steps until answer
            while not self.tone_heard:
                self.level += 5
                self.play_tone()

            tries += 1
            answers.append(self.level)
            print(f"Try nr {tries}: level: {self.level}")

            if answers.count(self.level) >= 2:
                if retest:
                    if abs(self.level - int(self.get_value_from_csv(str(self.frequency), self.temp_filename, self.side))) > 5:
                        self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                        return False
                    else:
                        self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                        return True

                # TODO Wenn Streuung mehr als 10 dB: Vermerk im Audiogramm
                self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
                if self.progress < 0.95 - self.progress_step:
                    self.progress += self.progress_step
                return True
            
            # no two same answers in three tries
            if tries == 3:
                self.level += 10
                self.play_tone()
                answers = []

        print("Something went wrong, please try from the beginning again.")
        return False

        
class ScreeningProcedure(Procedure):

    def __init__(self,  temp_filename, signal_length=1, headphone_name="Sennheiser_HDA200", calibrate=True):
        """Short screening process to check if subject can hear specific frequencies at certain levels.

        Args:
            signal_length (int, optional): length of played signals in seconds. Defaults to 1.
        """
        super().__init__(startlevel=0, signal_length=signal_length, headphone_name=headphone_name, calibrate=calibrate)
        self.temp_filename = temp_filename
        self.freq_order = [1000, 2000, 4000, 8000, 500, 250, 125]
        

        #TODO das als default, aber  variabel in der GUI?
        self.freq_levels = {125: 70, 250: 70, 500: 70, 1000: 70, 2000: 70, 4000: 70, 8000: 70}

        self.progress_step = 1 / 14

    def screen_test(self, binaural=False):
        """main functions

        Returns:
            bool: test successful
        """
        if not binaural:
            self.side = 'l'
            self.screen_one_ear()
            
            self.side = 'r'
            self.screen_one_ear()

            self.progress = 1

            self.create_final_csv_and_audiogram(self.temp_filename, binaural)
            return True
        
        if binaural:
            self.progress_step = 1 / 7
            self.side = 'lr'
            self.screen_one_ear()
            self.progress = 1

        self.create_final_csv_and_audiogram(self.temp_filename, binaural)


    def screen_one_ear(self):
        success = []

        for f in self.freq_order:
            print(f"Testing frequency {f} Hz")
            s = self.screen_one_freq(f)
            success.append(s)


    def screen_one_freq(self, freq):
        """screening for one frequency

        Args:
            freq (int): frequency to be tested

        Returns:
            bool: tone heard
        """
        self.frequency = freq
        self.level = self.freq_levels[freq]
        self.tone_heard = False
        self.num_heard = 0

        for i in range(2):
            self.play_tone()

            if self.tone_heard:
                self.num_heard += 1

        if self.num_heard == 1:
            self.play_tone()

            if self.tone_heard:
                self.num_heard += 1
        
        if self.num_heard >= 2:
            self.add_to_temp_csv(str(self.level), str(self.frequency), self.side, self.temp_filename)
            self.progress += self.progress_step
            return
 
        self.add_to_temp_csv('NH', str(self.frequency), self.side, self.temp_filename)
        self.progress += self.progress_step



class Calibration(Procedure):

    def __init__(self, startlevel=60, signal_length=10, headphone_name="Sennheiser_HDA200", **additional_data):
        """Process for calibrating system.

        Args:
            startlevel (int, optional): starting level of procedure in dB HL. Defaults to 60.
            signal_length (int, optional): length of played signals in seconds. Defaults to 10.
        """
        super().__init__(startlevel, signal_length, headphone_name=headphone_name, calibrate=False)      
        self.tempfile = self.create_temp_csv(id="", **additional_data) # create a temporary file to store level at frequencies
        self.generator = self.get_next_freq()
        self.dbspl = self.level + self.retspl[self.frequency]


    def get_next_freq(self):
        """Generator that goes through all frequencies twice.
        Changes self.side to 'r' after going through all frequencies the first time.

        Yields:
            int: frequency
        """
        self.side = 'l'
        frequency = 125
        while frequency <= 8000:
            yield frequency
            frequency *= 2

        frequency = 125
        self.side = 'r'
        while frequency <= 8000:
            yield frequency
            frequency *= 2


    def play_one_freq(self):
        """Get the next frequency and play it.

        Returns:
            bool: False if no more frequencies left
            int: current frequency
            float: expected SPL value in dB
        """
        self.ap.stop()
        
        try:
            self.frequency = next(self.generator)
        except:
            return False, self.frequency, self.dbspl
        
        self.dbspl = self.level + self.retspl[self.frequency]
        print(f"Side {self.side} at {self.frequency} Hz: The SPL value should be {self.dbspl} dB.")
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length, self.side)
        if self.frequency >= 8000 and self.side == 'r':
            return False, self.frequency, self.dbspl
        else:
            return True, self.frequency, self.dbspl
        

    def repeat_freq(self):
        """Repeats the last played frequency.
        """
        self.ap.stop()
        print(f" Repeating side {self.side} at {self.frequency} Hz: The SPL value should be {self.dbspl} dB.")
        self.ap.play_beep(self.frequency, self.dbhl_to_volume(self.level), self.signal_length, self.side)


    def set_calibration_value(self, measured_value):
        """Rights the given calibration value into temporary csv file

        Args:
            measured_value (float): measured SPL value in dB
        """
        value = measured_value - self.dbspl
        self.add_to_temp_csv(str(value), str(self.frequency), self.side, self.tempfile)


    def finish_calibration(self):
        """Makes a permanent csv file from the temporary file that overwrites calibration.csv.

        Args:
            temp_filename (str): name of temporary csv file
        """
        #TODO csv name
        self.ap.stop()
        # read temp file
        with open(self.tempfile, mode='r', newline='') as temp_file:
            dict_reader = csv.DictReader(temp_file)
            rows = list(dict_reader)

        filename = "calibration.csv"

        with open(filename, mode='w', newline='') as final_file:
            dict_writer = csv.DictWriter(final_file, fieldnames=self.freq_bands)
            dict_writer.writeheader()
            dict_writer.writerows(rows)
        
        print("Datei gespeicher als " + filename)
        

    def stop_playing(self):
        self.ap.stop()

