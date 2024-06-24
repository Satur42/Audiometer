import sounddevice as sd
import numpy as np
import argparse

# Ab hier vom Sounddevice Beispiel
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text
    
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
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-a', '--amplitude', type=float, default=0.2,
    help='amplitude (default: %(default)s)')
args = parser.parse_args(remaining)
# bis hier

fs = sd.query_devices(args.device, 'output')['default_samplerate']
duration = 2 
frequency = 440.0 
volume = 0.01  

t = np.linspace(0, duration, int(fs * duration), endpoint=False)
waveform = volume * np.sin(2 * np.pi * frequency * t)

def test_device(device_id):
    try:
        sd.default.device = device_id
        device_info = sd.query_devices(device_id)
        output_channels = device_info['max_output_channels']
        print(f"Teste Gerät {device_id}: {device_info['name']} mit {output_channels} Ausgabekanälen")
        
        # Abspielen des Sounds
        sd.play(waveform, samplerate=fs)
        sd.wait()
        print(f"Ton erfolgreich auf Gerät {device_id} abgespielt: {device_info['name']}\n\n")
    except Exception as e:
        print(f"Fehler beim Testen des Geräts {device_id}: {e}\n\n")

# Durchlaufen und Testen aller Geräte
# for device_id in range(len(sd.query_devices())):
#     test_device(device_id)


import sounddevice as sd
import numpy as np
import os

# Setze Umgebungsvariable, um sicherzustellen, dass PulseAudio verwendet wird
os.environ['PA_ALSA_PLUGHW'] = '1'

# Frequenz und Amplitude anpassen
duration = 2
frequency = 440.0
volume = 0.5  # Erhöhen Sie die Amplitude

# Sample Rate und Wellenform erstellen
fs = 44100  # Standard-Samplerate, falls nicht bekannt
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
waveform = volume * np.sin(2 * np.pi * frequency * t)

def test_device(device_id):
    try:
        sd.default.device = device_id
        device_info = sd.query_devices(device_id)
        output_channels = device_info['max_output_channels']
        print(f"Teste Gerät {device_id}: {device_info['name']} mit {output_channels} Ausgabekanälen")
        
        # Play sound
        sd.play(waveform, samplerate=fs)
        sd.wait()
        print(f"Ton erfolgreich auf Gerät {device_id} abgespielt: {device_info['name']}\n\n")
    except Exception as e:
        print(f"Fehler beim Testen des Geräts {device_id}: {e}\n\n")

# Teste alle Ausgabegeräte
for device_id in range(len(sd.query_devices())):
    test_device(device_id)
