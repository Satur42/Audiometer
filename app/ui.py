import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from PIL import Image, ImageTk
import os
import csv
import time
import random
from .instructions import *

# Theme settings
LIGHT_THEME = "sandstone"
DARK_THEME = "superhero"

# Font settings
HEADER_SIZE = 20
SUBHEADER_SIZE = 16
TEXT_SIZE = 12
FONT_FAMILY = 'Arial'

# UI settings
BUTTON_WIDTH = 25
BUTTON_SIZE = 12
GEOMETRY = "800x800"


class App(tb.Window):

    def __init__(self, familiarization_func, program_funcs:dict, calibration_funcs:list, progress_func):
        """Main application window. Contains all pages and controls the flow of the program.

        Args:
            familiarization_func (function): function to be called for familiarization
            audiogram_func (function): function to be called for creating audiogram
            program_funcs (dict of str:function): function(s) to be called for the main program
            calibration_funcs (list function): list of function(s) for calibration in this order: start, next, repeat, stop, set_level

        """
        super().__init__(themename=LIGHT_THEME)

        # General theme settings
        self.title("Sound Player")
        self.geometry(GEOMETRY)
        self.minsize(650,650)
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", self.exit_fullscreen)

        self.save_path = os.path.join(os.getcwd())
        os.makedirs(self.save_path, exist_ok=True)

        # Update program_funcs to use the current save_path
        self.program_funcs = {key: lambda save_path=self.save_path: func(save_path=save_path) for key, func in program_funcs.items()}
        self.familiarization_func = lambda save_path=self.save_path: familiarization_func(save_path=save_path)
        self.calibration_funcs = [lambda save_path=self.save_path: func(save_path=save_path) for func in calibration_funcs]


        #self.set_icon("app/00_TUBerlin_Logo_rot.jpg") change the icon maybe? #TODO
        
        self.tk.call('tk', 'scaling', 2.0)  # Adjust for high-DPI displays
        
        # Dictionary to store all pages
        self.program_funcs = program_funcs
        self.frames = {}
        self.binaural_test = False

        # Interactive Pages
        for F in (MainMenu, FamiliarizationPage, ProgramPage, ResultPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Calibration separately to give it its functions
        frame = CalibrationPage(self, calibration_funcs)
        self.frames[CalibrationPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # View during familiarization
        frame = DuringFamiliarizationView(self, familiarization_func, progress_func)
        self.frames[DuringFamiliarizationView] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # View during programs
        for name, program_func in program_funcs.items():
            frame = DuringProcedureView(self, 
                                        program_func, progress_func,
                                        text="Programm läuft...")
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show MainMenu first
        self.show_frame(MainMenu)

        # Create menubar
        self.create_menubar()

        # Variable for threading
        self.process_done = False

        # Override the close button protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def create_menubar(self):
        """Create a menubar with options for changing the theme and exiting the program"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Startseite", command=lambda: self.show_frame(MainMenu))
        file_menu.add_command(label="Speicherort ändern", command=self.change_save_path)

        # Settings for changing the theme Link: lighthttps://ttkbootstrap.readthedocs.io/en/latest/themes/dark/
        ChangeTheme = tk.Menu(file_menu, tearoff=0)
        

        ChangeTheme.add_command(label="light", command=lambda: self.change_theme(LIGHT_THEME))
        ChangeTheme.add_command(label="dark", command=lambda: self.change_theme(DARK_THEME))

        file_menu.add_cascade(label="Theme ändern", menu=ChangeTheme)

        file_menu.add_separator()
        file_menu.add_command(label="Programm beenden", command=self.on_closing)
        menubar.add_cascade(label="Einstellungen", menu=file_menu)


    def change_theme(self, theme_name):
        """Change to the specified theme"""
        current_theme = self.style.theme_use()

        if current_theme == theme_name:
            messagebox.showwarning("Oops..", "Dieses Theme wird bereits verwendet.")
        else:
            self.style.theme_use(theme_name)


    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.attributes('-fullscreen', False)


    def set_icon(self, path):
        """Set the window icon using Pillow"""
        img = Image.open(path)
        photo = ImageTk.PhotoImage(img)
        self.iconphoto(False, photo)          


    def show_frame(self, page):
        """Show a frame for the given page name

        Args:
            page(class): class of the page to be shown
        """
        frame = self.frames[page]
        frame.tkraise()


    def wait_for_process(self, process, callback):
        """Starts a process in a new thread and calls a callback function when the process is done.

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        t = threading.Thread(target=self.run_process, args=(process, callback))
        t.daemon = True
        t.start()


    def run_process(self, process, callback):
        """Runs a process and calls a callback function when the process is done

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        process()
        self.process_done = True
        self.after(100, callback)


    def change_save_path(self):
        """Ask the user to select a folder to save the files"""
        new_path = filedialog.askdirectory(title="Select Folder to Save Files")
        if new_path:
            self.save_path = new_path
            # Update program_funcs to use the new save_path
            self.program_funcs = {key: lambda save_path=self.save_path: func(save_path=save_path) for key, func in self.program_funcs.items()}
            self.familiarization_func = lambda save_path=self.save_path: self.original_familiarization_func(save_path=save_path)
            self.calibration_funcs = [lambda save_path=self.save_path: func(save_path=save_path) for func in self.calibration_funcs]
            messagebox.showinfo("Speicherort geändert", f"Neuer Speicherort: {self.save_path}")


    def on_closing(self):
        """Ask for confirmation before closing the program"""
        if messagebox.askyesno(title="Quit", message="Möchten Sie wirklich das Programm beenden?"):
            self.destroy()


    def get_images_in_path(self, directory, image_extensions=[".png", ".jpg", ".jpeg", ".gif", ".bmp"]):
        """
        Get a list of image files in the specified directory.

        Args:
        directory (str): The path to the directory to check.
        image_extensions (list): List of image file extensions to check for.

        Returns:
        list: List of image file paths if any image files are found, False otherwise.
        """
        if not os.path.exists(directory):
            return False

        image_files = [os.path.join(directory, file) for file in os.listdir(directory) if any(file.lower().endswith(ext) for ext in image_extensions)]
        return image_files if image_files else False


class MainMenu(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.button_width = 25
        self.start_button = None
        self.binaural_test = tk.BooleanVar()
        self.use_calibration = tk.BooleanVar(value=True)
        self.selected_option = None
        self.patient_number = ""
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the page
        """
        self.patient_number_label = ttk.Label(self, text="Probandennummer:",font=(FONT_FAMILY, TEXT_SIZE))
        self.patient_number_label.pack(padx=10, pady=10)
        self.patient_number_entry = ttk.Entry(self,width=self.button_width+1)
        self.patient_number_entry.pack(padx=10, pady=10)

        self.gender_label = ttk.Label(self, text="Geschlecht (Optional):", font=(FONT_FAMILY, TEXT_SIZE))
        self.gender_label.pack(padx=10, pady=10)
        self.gender_dropdown = ttk.Combobox(self, values=["Männlich", "Weiblich", "Divers", "Keine Angabe"], state="readonly", width=self.button_width - 1)
        self.gender_dropdown.set("Geschlecht...")
        self.gender_dropdown.pack(padx=10, pady=10)

        self.age_label = ttk.Label(self, text="Alter (Optional):", font=(FONT_FAMILY, TEXT_SIZE))
        self.age_label.pack(padx=10, pady=10)
        self.age_entry = ttk.Entry(self, width=self.button_width+1)
        self.age_entry.pack(padx=10, pady=10)

        self.label = ttk.Label(self, text="\nBitte wählen Sie ein Programm", font=(FONT_FAMILY, TEXT_SIZE))
        self.label.pack(pady=10)

        # Dropdown menu
        options = list(self.parent.program_funcs.keys())
        self.dropdown = ttk.Combobox(self, values=options, state="readonly", width=self.button_width - 1)
        self.dropdown.set("Test wählen...")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_option_selected)

        self.binaural_button = ttk.Checkbutton(self, 
                                         text="Binaurale Testung", 
                                         variable=self.binaural_test)
        self.binaural_button.pack(pady=10)

        # Use calibration button
        self.cal_button = ttk.Checkbutton(self, 
                                         text="Werte aus letzter Kalibrierung verwenden", 
                                         variable=self.use_calibration)
        self.cal_button.pack(pady=10, side="bottom")

        # Headphone selection
        self.headphone_dropdown = ttk.Combobox(self, values=self.get_headphone_options(), state="readonly", width=self.button_width - 1)
        self.headphone_dropdown.set("Sennheiser_HDA200")
        self.headphone_dropdown.pack(padx=10, pady=10, side="bottom")
        self.headphone_label = ttk.Label(self, text="Kopfhörer:", font=(FONT_FAMILY, TEXT_SIZE))
        self.headphone_label.pack(padx=10, pady=10, side="bottom")


    def get_headphone_options(self):

        file_name = 'retspl.csv'
        
        # Check if the CSV file exists
        if not os.path.isfile(file_name):
            messagebox.showwarning("Warnung", f'Die Datei "{file_name}" konnte nicht gefunden werden.')
            return
        
        headphone_options = []

        try:
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    headphone_options.append(row['headphone_model'])
                    headphone_options = list(set(headphone_options))
            return headphone_options
        except Exception as e:
            messagebox.showwarning("Warnung", f'Fehler beim Lesen der Datei "{file_name}": {e}')
            return
        

    def on_option_selected(self, event):
        self.selected_option = self.dropdown.get()
        self.show_start_button()
        if self.selected_option == "Kalibrierung":
            self.cal_button.config(state=tk.DISABLED)
            self.binaural_button.config(state=tk.DISABLED)
            self.gender_dropdown.config(state=tk.DISABLED)
            self.patient_number_entry.config(state=tk.DISABLED)
        else:
            self.cal_button.config(state=tk.NORMAL)
            self.binaural_button.config(state=tk.NORMAL)
            self.gender_dropdown.config(state=tk.NORMAL)
            self.patient_number_entry.config(state=tk.NORMAL)    


    def show_start_button(self):
        if self.start_button is None:
            self.start_button = ttk.Button(self,
                                           text="Test starten",
                                           command=self.go_to_next_page,
                                           width=self.button_width)
            self.start_button.pack(pady=10)


    def go_to_next_page(self):
        if self.selected_option == "Kalibrierung":
            self.parent.show_frame(CalibrationPage)
            
        else:
            self.patient_number = self.patient_number_entry.get()
            if not self.patient_number:
                messagebox.showwarning("Warnung", "Bitte geben Sie eine Probandennummer ein.")
                return
            
            # check if valide age is entered
            if self.age_entry.get():
                try:
                    i = int(self.age_entry.get())
                    if i > 110 or i < 0:
                        messagebox.showwarning("Warnung", 'Bitte geben Sie beim Alter eine gültige Zahl ein.')
                        return
                except:
                    messagebox.showwarning("Warnung", 'Bitte geben Sie beim Alter eine gültige Zahl ein.')
                    return

            patient_folder = os.path.join(self.parent.save_path, self.patient_number)
            pics = self.parent.get_images_in_path(patient_folder)
            if pics:
                if messagebox.askyesno("Proband vorhanden", "Für diese Probandennummer gibt es bereits Ergebnisse. Möchten Sie diese anzeigen?"):
                    results_page = self.parent.frames[ResultPage]
                    results_page.display_images(self.patient_number)
                    self.parent.show_frame(ResultPage)
                    return

            self.parent.show_frame(FamiliarizationPage)


class FamiliarizationPage(ttk.Frame):

    def __init__(self, parent):
        """Page for starting the familiarization process.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the page
        """
        button_width = 25 

        self.label = ttk.Label(self, text=text_Familiarization, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.label.pack(padx=10, pady=10)
        self.play_button = ttk.Button(self, 
                                      text="Starte Eingewöhnung", 
                                      command=self.run_familiarization, 
                                      width=button_width)
        self.play_button.pack(padx=10, pady=10)
        self.go_back_button = ttk.Button(self, 
                                         text="zurück", 
                                         command=lambda: self.parent.show_frame(MainMenu), 
                                         width=button_width)
        self.go_back_button.pack(padx=10, pady=10)

        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')


    def run_familiarization(self):
        """Runs the familiarization process
        """
        self.use_calibration = self.parent.frames[MainMenu].use_calibration.get()
        self.parent.show_frame(DuringFamiliarizationView)
        
        gender = self.parent.frames[MainMenu].gender_dropdown.get()
        if gender == "Geschlecht..." or gender == "Keine Angabe":
            gender = ""

        age = self.parent.frames[MainMenu].age_entry.get()

        self.parent.wait_for_process(lambda: self.parent.frames[DuringFamiliarizationView].program(id=self.parent.frames[MainMenu].patient_number, 
                                                                                                   calibrate=self.use_calibration, 
                                                                                                   gender=gender,
                                                                                                   age=age), 
                                     lambda: self.parent.show_frame(ProgramPage))
        time.sleep(0.001)
        self.update()
        counter = 0
        sleep_time = random.uniform(1, 2.5) # random time in seconds between 1 and 2.5 to update progress bar
        while self.parent.frames[DuringFamiliarizationView].progress_var.get() < 100 and not self.parent.process_done:
            progress = int(self.parent.frames[DuringFamiliarizationView].get_progress() * 100)
            if counter >= sleep_time * 1000:
                self.parent.frames[DuringFamiliarizationView].progress_var.set(progress)
                counter = 0
            time.sleep(0.001)
            counter += 1
            self.update()
        self.parent.process_done = False


class ProgramPage(ttk.Frame):

    def __init__(self, parent):
        """Page for starting the main program.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.selected_option = None 
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the page"""
        self.start_button = ttk.Button(self, text="Starte Prozess", command=self.run_program)
        self.start_button.pack(padx=10, pady=200)
    
        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')


    def run_program(self):
        """Runs the main program"""
        self.selected_option = self.parent.frames[MainMenu].selected_option
        self.binaural_test = self.parent.frames[MainMenu].binaural_test.get()
        self.use_calibration = self.parent.frames[MainMenu].use_calibration.get()
        self.parent.show_frame(self.selected_option)

        self.parent.wait_for_process(lambda: self.parent.frames[self.selected_option].program(self.binaural_test, calibrate=self.use_calibration),
                                     self.show_results)
        
        time.sleep(0.001)
        self.update()
        counter = 0
        sleep_time = random.uniform(1, 2.5) # random time in seconds between 1 and 2.5 to update progress bar
        while self.parent.frames[self.selected_option].progress_var.get() < 100 and not self.parent.process_done:
            progress = int(self.parent.frames[self.selected_option].get_progress() * 100)
            if counter >= sleep_time * 1000:
                self.parent.frames[self.selected_option].progress_var.set(progress)
                counter = 0
            time.sleep(0.001)
            counter += 1
            self.update()
        self.parent.process_done = False


    def show_results(self):
        """Show the results page with the images"""
        patient_number = self.parent.frames[MainMenu].patient_number
        results_page = self.parent.frames[ResultPage]
        results_page.display_images(patient_number)
        self.parent.show_frame(ResultPage)



class DuringFamiliarizationView(ttk.Frame):
    


    def __init__(self, parent, familiarization_func, progress_func):
        """View during familiarization process
        
        Args:
            parent (App): parent application
            familiarization_func (function): function to be called for familiarization"""
        super().__init__(parent)
        self.parent = parent
        self.program = familiarization_func
        self.get_progress = progress_func 
        self.text = "Eingewöhnung läuft..."
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the view
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.pack(padx=10, pady=10)
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(padx=10, pady=100)


class DuringProcedureView(ttk.Frame):

    def __init__(self, parent, program_func, progress_func, text):
        """View during main program

        Args:
            parent (App): parent application
            program_func (function): function to be called for the main program
            text (str): text to be displayed
        """
        super().__init__(parent)
        self.parent = parent
        self.program = program_func
        self.get_progress = progress_func  
        self.text = text
        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the view
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.pack(padx=10, pady=10)
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(padx=10, pady=100)


class ResultPage(ttk.Frame):

    def __init__(self, parent):
        """Page for showing the results of the program.

        Args:
            parent (App): parent application"""
        
        super().__init__(parent)
        self.parent = parent

        self.create_widgets()


    def create_widgets(self):
        """Creates the widgets for the view"""
        self.info = ttk.Label(self, text="Ergebnisse", font=(FONT_FAMILY, HEADER_SIZE))
        self.info.pack(padx=10, pady=10)

        # Set the title on the parent window
        self.parent.title("Audiogramm")

        # Create a frame for the images
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(anchor="center")   #,fill="both", expand=True)

        # Button to go back to the main menu
        self.BackToMainMenu = ttk.Button(self, text="Zurück zur Startseite", command=lambda: self.parent.show_frame(MainMenu))
        self.BackToMainMenu.pack(padx=10, pady=10)


    def display_images(self, folder_name):
        """Display all images in the given folder"""
        folder_path = os.path.join(self.parent.save_path, folder_name)
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        # TODO das muss viel schöner angezeigt werden, mittig, groß, Datum und Uhrzeit etc. ...
        
        pics = self.parent.get_images_in_path(folder_path)
        if pics:
            for file in pics:
                img = Image.open(file)
                #img = img.resize((400, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                label = ttk.Label(self.image_frame, image=photo)
                label.image = photo
                label.pack(padx=10, pady=10, side="left")


    def back_to_MainMenu(self):
        self.parent.show_frame(MainMenu)



class CalibrationPage(ttk.Frame):

    def __init__(self, parent, calibration_funcs):
        """Page for calibrating the audiometer.

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.cal_start = calibration_funcs[0]
        self.cal_next = calibration_funcs[1]
        self.cal_repeat = calibration_funcs[2]
        self.cal_stop = calibration_funcs[3]
        self.cal_setlevel = calibration_funcs[4]
        self.create_widgets()
        self.finished = False


    def create_widgets(self):
        """Creates the widgets for the page.
        """
        button_width = 25 

        self.intro = ttk.Label(self, text=text_calibration, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.intro.pack(padx=10, pady=10)
        self.level_label = ttk.Label(self, text="Wert in dBHL, bei dem kalibriert werden soll:", font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_label.pack(padx=10, pady=10)
        self.level_entry_var = tk.StringVar()
        self.level_entry_var.set("10")
        self.level_entry = ttk.Entry(self,width=button_width-10, textvariable=self.level_entry_var)
        self.level_entry.pack(padx=10, pady=10)
        self.start_button = ttk.Button(self, 
                                      text="Kalibrierung starten", 
                                      command=self.start_calibration, 
                                      width=button_width)
        self.start_button.pack(padx=10, pady=10)
        self.next_button = ttk.Button(self, 
                                      text="Nächste Frequenz", 
                                      command=self.next_frequency, 
                                      width=button_width,
                                      state=tk.DISABLED)
        self.next_button.pack(padx=10, pady=10)
        self.repeat_button = ttk.Button(self, 
                                         text="Erneut wiedergeben", 
                                         command=self.repeat_frequency, 
                                         width=button_width,
                                         state=tk.DISABLED)
        self.repeat_button.pack(padx=10, pady=10)
        self.stop_button = ttk.Button(self, 
                                         text="Wiedergabe stoppen", 
                                         command=self.stop_playing, 
                                         width=button_width,
                                         state=tk.DISABLED)
        self.stop_button.pack(padx=10, pady=10)
        self.back_button = ttk.Button(self, 
                                         text="Zurück zum Hauptmenü", 
                                         command=lambda: self.parent.show_frame(MainMenu), 
                                         width=button_width) # TODO Kalibrierung resetten, damit man sie dann wieder von vorne anfangen kann
        self.back_button.pack(padx=10, pady=20)
        

        self.spacer_frame = tk.Frame(self, width=20, height=80)
        self.spacer_frame.pack()

        self.current_freq_var = tk.StringVar(value="Aktuelle Frequenz:")
        self.current_freq = ttk.Label(self, textvariable=self.current_freq_var, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.current_freq.pack(padx=10, pady=10)
        self.level_expected_var = tk.StringVar(value="Schalldruckpegel (soll):")
        self.level_expected_label = ttk.Label(self, textvariable=self.level_expected_var, font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_expected_label.pack(padx=10, pady=10)
        self.level_measured_label = ttk.Label(self, text="Gemessener Schalldruckpegel in dB:", font=(FONT_FAMILY, SUBHEADER_SIZE))
        self.level_measured_label.pack(padx=10, pady=10)
        self.level_measured_var = tk.StringVar()
        self.level_measured_entry = ttk.Entry(self, width=button_width-10, 
                                              font=(FONT_FAMILY, SUBHEADER_SIZE), state=tk.DISABLED,
                                              textvariable=self.level_measured_var)
        self.level_measured_entry.pack(padx=10, pady=10)


        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')


    def start_calibration(self):
        try:
            current_freq, current_spl = self.cal_start(float(self.level_entry_var.get()))
        except:
            messagebox.showwarning("Warnung", 'Bitte geben Sie eine Zahl ein.')
            return
        
        self.start_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.repeat_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.level_measured_entry.config(state=tk.NORMAL)

        self.current_freq_var.set("Aktuelle Frequenz: " + str(current_freq) + " Hz")
        self.level_expected_var.set("Schalldruckpegel (soll): " + str(current_spl) + " dB") 
        

    def next_frequency(self):
        try:
            if self.level_measured_var.get() != "":
                self.cal_setlevel(float(self.level_measured_var.get()))
            else:
                messagebox.showwarning("Warnung", 'Bitte geben Sie bei "gemessener Schalldruckpegel" eine Zahl ein.')
                return    
        except ValueError:
            messagebox.showwarning("Warnung", 'Bitte geben Sie bei "gemessener Schalldruck" eine Zahl ein.')
            return
        self.level_measured_var.set("")
        more_freqs, current_freq, current_spl = self.cal_next()
        # Change Button when last frequency
        if not more_freqs:

            # Grey out all buttons when finished
            if self.finished:
                self.next_button.config(state=tk.DISABLED)
                self.repeat_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.level_measured_entry.config(state=tk.DISABLED)
                messagebox.showwarning("Kalibrierung abgeschlossen.", "Die Kalibrierung wurde erfolgreich abgeschlossen. Datei gespeichert als calibration.csv")
                return
            
            self.next_button.config(text="Kalibrierung abschließen")
            self.finished = True

        self.current_freq_var.set("Aktuelle Frequenz: " + str(current_freq) + " Hz")
        self.level_expected_var.set("Schalldruckpegel (soll): " + str(current_spl) + " dB")    


    def repeat_frequency(self):
        self.cal_repeat()


    def stop_playing(self):
        self.cal_stop()


def setup_ui(startfunc, programfuncs, calibrationfuncs, progressfunc):
    app = App(startfunc, programfuncs, calibrationfuncs, progressfunc)
    return app

