import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import messagebox
from .audiogram import create_audiogram #TODO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.instructions import text_Familiarization
import ttkbootstrap as tb
from PIL import Image, ImageTk
import time

class App(tb.Window):
    def __init__(self, familiarization_func, program_funcs:dict):
        """Main application window. Contains all pages and controls the flow of the program.

        Args:
            familiarization_func (function): function to be called for familiarization
            *program_funcs (function): function(s) to be called for the main program
        """
        super().__init__(themename="superhero")  # Set/change the theme Link: https://ttkbootstrap.readthedocs.io/en/latest/themes/dark/

        # General settings
        self.title("Sound Player")
        self.geometry("800x800")
        self.minsize(650,650)
        self.attributes('-fullscreen', True)  #for fullscreen mode
        self.bind("<Escape>", self.exit_fullscreen)
        
        #self.set_icon("app/00_TUBerlin_Logo_rot.jpg") change the icon maybe? #TODO

        
        #this might solve the different GUI on macOS LINUX and WINDOWS problem... #TODO
        self.tk.call('tk', 'scaling', 2.0)  # Adjust for high-DPI displays
        '''
        # Set explicit fonts
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TCombobox', font=('Arial', 12))
        '''

        # Dictionary to store all pages
        self.program_funcs = program_funcs
        self.frames = {}

        # Pages, where the user can interact
        for F in (MainMenu, FamiliarizationPage, ProgramPage, ResultPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # View during familiarization
        frame = DuringFamiliarizationView(self, familiarization_func)
        self.frames[DuringFamiliarizationView] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # View during programs
        for name, program_func in program_funcs.items():
            frame = DuringProcedureView(self, 
                                        program_func,
                                        text="Programm läuft...")
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show MainMenu first
        self.show_frame(MainMenu)

        # Create menubar
        self.create_menubar()

        # Override the close button protocol (instead of extra button)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_menubar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Startseite", command=lambda: self.show_frame(MainMenu))

        # Settings for chaning the theme ##i've randomly selected 4 themes (2 dark and 2 lighthttps://ttkbootstrap.readthedocs.io/en/latest/themes/dark/
        ChangeTheme = tk.Menu(file_menu, tearoff=0)
        ChangeTheme.add_command(label="theme 1", command=lambda: self.change_theme("superhero"))
        ChangeTheme.add_command(label="theme 2", command=lambda: self.change_theme("solar"))
        ChangeTheme.add_command(label="theme 3", command=lambda: self.change_theme("cosmo"))
        ChangeTheme.add_command(label="theme 4", command=lambda: self.change_theme("sandstone"))
        file_menu.add_cascade(label="change theme", menu=ChangeTheme)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)



    def change_theme(self, theme_name):
        """Change to the specified theme"""
        current_theme = self.style.theme_use()

        if current_theme == theme_name:
            messagebox.showwarning("Ops..", "This theme is already in use.")
        else:
            self.style.theme_use(theme_name)

    def exit_fullscreen(self, event=None):
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
        """Starts a process in a new thread and calls a callback function when the process is done

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        threading.Thread(target=self.run_process, args=(process, callback)).start()

    def run_process(self, process, callback):
        """Runs a process and calls a callback function when the process is done

        Args:
            process (function): function to be called
            callback (function): function to be called when process is done
        """
        process()
        self.after(0, callback)

    def on_closing(self):
        if messagebox.askyesno(title="Quit", message="Möchten Sie wirklich das Programm beenden?"):
            self.destroy()


class MainMenu(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_option = None  # Instance variable to store selected option
        self.button_width = 25
        self.start_button = None
        self.create_widgets()

    def create_widgets(self):
        '''
        self.patient_number_label = ttk.Label(self, text="Patient Number:")
        self.patient_number_label.pack(padx=10, pady=10)
        self.patient_number_entry = ttk.Entry(self)
        self.patient_number_entry.pack(padx=10, pady=10)

        self.first_name_label = ttk.Label(self, text="First Name (Optional):")
        self.first_name_label.pack(padx=10, pady=10)
        self.first_name_entry = ttk.Entry(self)
        self.first_name_entry.pack(padx=10, pady=10)

        self.last_name_label = ttk.Label(self, text="Last Name (Optional):")
        self.last_name_label.pack(padx=10, pady=10)
        self.last_name_entry = ttk.Entry(self)
        self.last_name_entry.pack(padx=10, pady=10)

        self.gender_label = ttk.Label(self, text="Gender (M/F, Optional):")
        self.gender_label.pack(padx=10, pady=10)
        self.gender_entry = ttk.Entry(self)
        self.gender_entry.pack(padx=10, pady=10)
        '''
        self.label = ttk.Label(self, text="\nBitte wählen Sie ein Programm", font=('Arial', 16))
        self.label.pack(pady=10)

        # Dropdown menu
        options = list(self.parent.program_funcs.keys())
        self.dropdown = ttk.Combobox(self, values=options, state="readonly", width=self.button_width - 1)
        self.dropdown.set("Test wählen...")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_option_selected)

        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')

    def on_option_selected(self, event):
        self.selected_option = self.dropdown.get() 
        self.show_start_button()

    def show_start_button(self):
        if self.start_button is None:
            self.start_button = ttk.Button(self,
                                           text="Test starten",
                                           command=self.run_familiarization,
                                           width=self.button_width)
            self.start_button.pack(pady=10)

    def run_familiarization(self):
        ''' 
        patient_number = self.patient_number_entry.get()
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = self.gender_entry.get()

        self.parent.user_info = {
            "patient_number": patient_number,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender
        }
        '''
        self.parent.frames[FamiliarizationPage].selected_option = self.selected_option 
        self.parent.show_frame(FamiliarizationPage)



class FamiliarizationPage(ttk.Frame):
    def __init__(self, parent):
        """Page for starting the familiarization process

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
       
        self.label = ttk.Label(self, text=text_Familiarization, font=('Arial', 16))
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
        '''
        self.parent.show_frame(DuringFamiliarizationView)
        self.parent.wait_for_process(self.parent.frames[DuringFamiliarizationView].program, 
                                     lambda: self.parent.show_frame(ProgramPage))
        '''
    
        """Runs the familiarization process
        """
        #user_info = self.parent.user_info
        #self.familiarization = Familiarization(user_info=user_info)
        self.parent.show_frame(DuringFamiliarizationView)
        threading.Thread(target=self.parent.frames[DuringFamiliarizationView].start_familiarization).start()



class ProgramPage(ttk.Frame):
    def __init__(self, parent):
        """Page for starting the main program

        Args:
            parent (App): parent application
        """
        super().__init__(parent)
        self.parent = parent
        self.selected_option = None 
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the page
        """
        self.start_button = ttk.Button(self, text="Starte Prozess", command=self.run_program)
        self.start_button.pack(padx=10, pady=200)
    

        for widget in self.winfo_children():
            widget.pack_configure(anchor='center')

    def run_program(self):
        """Runs the main program
        """
        self.selected_option = self.parent.frames[MainMenu].selected_option
        self.parent.show_frame(self.selected_option)
        self.parent.wait_for_process(self.parent.frames[self.selected_option].program,
                                     lambda: self.parent.show_frame(ResultPage))

class DuringFamiliarizationView(ttk.Frame):
    def __init__(self, parent, familiarization_func):
        """View during familiarization process
        
        Args:
            parent (App): parent application
            familiarization_func (function): function to be called for familiarization"""
        super().__init__(parent)
        self.parent = parent
        self.program = familiarization_func  # Hinweis: hier läuft gerade die Dummy Eingewöhnung
        self.text = "Eingewöhnung läuft..."
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the view
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.pack(padx=10, pady=10)

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(padx=10, pady=10)

        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(fill=tk.BOTH, expand=True)

        self.progress_label = ttk.Label(self, text="0%", anchor="center")
        self.progress_label.pack(padx=10, pady=10)
        #self.progress_label.place(relx=0.5, rely=0.5, anchor="center")


    def update_progress(self, value):
        """Updates the progress bar and label
        """
        self.progress["value"] = value
        self.progress_label["text"] = f"{value}%"
        self.progress_label.update_idletasks()

    def start_familiarization(self):
        """Starts the familiarization process and updates the progress bar
        """
        max_value = 100  # Define the maximum value for the progress bar
        step_value = max_value // 10  # Example: 10 steps

        for i in range(1, 11):
            self.program()
            self.update_progress(i * step_value)
            self.update_idletasks()
            time.sleep(1)  # Simulate time taken for each step (replace with actual process duration)

        self.parent.show_frame(ProgramPage)  # Show the next page after familiarization


class DuringProcedureView(ttk.Frame):
    def __init__(self, parent, program_func, text):
        """View during main program

        Args:
            parent (App): parent application
            program_func (function): function to be called for the main program
            text (str): text to be displayed
        """
        super().__init__(parent)
        self.parent = parent
        self.program = program_func  # Hinweis: hier läuft gerade die Dummy Procedure
        self.text = text
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the view
        """
        self.info = ttk.Label(self, text=self.text)
        self.info.grid(row=0, column=0, padx=10, pady=10)
        

class ResultPage(ttk.Frame):
    def __init__(self, parent):
        """Page for showing the results of the program

        Args:
            parent (App): parent application"""
        
        super().__init__(parent)
        self.parent = parent

        freq = [63, 125, 250, 500, 1000, 2000, 4000, 8000]
        dummy_right = [10, 15, 20, 25, 30, 35, 40, 45]
        dummy_left = [5, 10, 15, 20, 25, 30, 35, 40]

        # Create audiogram plot
        fig = create_audiogram(freq, dummy_right, dummy_left)
        
        # Create widgets
        self.create_widgets(fig)

    def create_widgets(self,fig):
        """Creates the widgets for the view`
        """
        self.info = ttk.Label(self, text="Ergebnisse", font=('Arial', 18))
        self.info.pack(padx=10, pady=10)

        # Set the title on the parent window
        self.parent.title("Audiogram")

        # Display the plot
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, expand=0)

        self.BackToMainMenu = ttk.Button(self, text="Zurück zur Startseite", command=lambda: self.parent.show_frame(MainMenu))
        self.BackToMainMenu.pack(padx=10, pady=10)

    
    def back_to_MainMenu(self):
        self.parent.show_frame(MainMenu)


def setup_ui(startfunc, programfuncs):
    app = App(startfunc, programfuncs)
    return app