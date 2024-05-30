from app import Controller

# Run this script to start the application
# make sure you have sounddevice installed 
# (pip install sounddevice / conda install conda-forge::python-sounddevice)

if __name__ == "__main__":
    c = Controller()
    c.run_app()

# https://realpython.com/if-name-main-python/
# https://docs.python.org/3/library/__main__.html
       