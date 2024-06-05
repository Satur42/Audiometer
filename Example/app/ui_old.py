import tkinter as tk

class App(tk.Tk):
    def __init__(self, startfunc):
        super().__init__()
        self.title("Sound Player")
        self.geometry("400x200")
        self.frames = {}
        self.start = startfunc

        for F in (Menu, Programm):
            page_name = F.__name__
            frame = F(parent=self, controller=self, start=self.start)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Menu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class Menu(tk.Frame):
    def __init__(self, parent, controller, start):
        super().__init__(parent)
        self.controller = controller
        self.start = start
        self.create_widgets()

    def create_widgets(self):
        self.play_button = tk.Button(self, text="Click me :)", command=self.start_view)
        self.play_button.grid(row=0, column=0, padx=10, pady=10)

    def start_view(self):
        self.start()
        self.controller.show_frame("Programm")


class Programm(tk.Frame):
    def __init__(self, parent, controller, start):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.stop_button = tk.Button(self, text="Make it stop!", command=self.stop)
        self.stop_button.grid(row=0, column=0, padx=10, pady=10)

    def stop(self):
        self.audio_player.stop_beep()
        self.controller.show_frame("Menu")



def setup_ui(startfunc):
    app = App(startfunc)
    return app
