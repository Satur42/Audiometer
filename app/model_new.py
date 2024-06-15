#from .audio_player import AudioPlayer
import numpy as np
import sounddevice as sd
import threading
from pynput import keyboard
import time


class AudioPlayer:

    def __init__(self):
        """An audio player that can play sine beeps at various frequencies, volumes and with various durations.
        Automatically detects current samplerate of selected sound device.
        """
        self.fs = self.get_device_samplerate()
        self.beep_duration = 10
        self.volume = 0.5
        self.frequency = 440
        self.stream = None
        self.is_playing = False

    def generate_tone(self):
        """Generates a sine tone with current audio player settings

        Returns:
            np.array: sine wave as numpy array
        """
        t = np.linspace(start=0, 
                        stop=self.beep_duration, 
                        num=int(self.fs * self.beep_duration), 
                        endpoint=False)
        tone = np.sin(2 * np.pi * self.frequency * t) * self.volume
        return tone

    def play_beep(self, frequency, volume, duration):
        """Sets the frequency, volume and beep duration of the audio player and then plays a beep with those parameters

        Args:
            frequency (int): f in Hz
            volume (float): volume multiplier (between 0 and 1)
            duration (int): duration of beep in seconds
        """
        self.frequency = frequency
        self.volume = volume
        self.beep_duration = duration
        self.is_playing = True
        tone = self.generate_tone()
        sd.play(tone, self.fs)
        sd.wait()
        self.is_playing = False

    def stop(self):
        """Stops the currently playing beep."""
        sd.stop()
        self.is_playing = False


    def int_or_str(self, text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text


    def get_device_samplerate(self):
        """gets current samplerate from the selected audio output device

        Returns:
            float: samplerate of current sound device
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        args, remaining = parser.parse_known_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            'frequency', nargs='?', metavar='FREQUENCY', type=float, default=500,
            help='frequency in Hz (default: %(default)s)')
        parser.add_argument(
            '-d', '--device', type=self.int_or_str,
            help='output device (numeric ID or substring)')
        parser.add_argument(
            '-a', '--amplitude', type=float, default=0.2,
            help='amplitude (default: %(default)s)')
        args = parser.parse_args(remaining)
        return sd.query_devices(args.device, 'output')['default_samplerate']
    
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
        """Calculate dBHL into absolute numbers

        Args:
            dbhl (float): value in dBHL

        Returns:
            float: value in absolute numbers
        """
        return self.zero_dbhl * 10 ** (dbhl / 10)

    def key_press(self, key):
        if key == keyboard.Key.space:
            self.tone_heard = True
            self.ap.stop()
            return False

    def play_tone(self):
        """Set tone_heard to False, play beep, then wait for keypress.
        If key is pressed, set tone_heard to True.
        """
        self.tone_heard = False
        beep_thread = threading.Thread(target=self.ap.play_beep, args=(self.frequency, self.dbhl_to_volume(self.level), self.signal_length))
        listener_thread = threading.Thread(target=self.listen_for_keypress)
        
        beep_thread.start()
        listener_thread.start()

        beep_thread.join()
        listener_thread.join()

        if not self.tone_heard:
            print("Tone not heard :(")

    def listen_for_keypress(self):
        with keyboard.Listener(on_press=self.key_press) as listener:
            listener.join()




class Familiarization(Procedure):

    def __init__(self, startlevel=40, signal_length=1):
        """Familiarization process

        Args:
            startlevel (int, optional): starting level of procedure in dBHL. Defaults to 40.
            signal_length (int, optional): length of played signals in seconds. Defaults to 1.
        """
        super().__init__(startlevel, signal_length)      
        self.fails = 0 # number of times familiarization failed

    def familiarize(self):
        """Main function"""

        while True:

            self.tone_heard = True

            # First loop (always -20dBHL)
            while self.tone_heard:
                self.play_tone()
                if self.tone_heard:
                    self.level -= 20
                else:
                    self.level += 10

            # Second loop (always +10dBHL)
            while not self.tone_heard:
                self.play_tone()
                if not self.tone_heard:
                    self.level += 10

            # Replay tone with same level
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



familiarization = Familiarization()
familiarization.familiarize()