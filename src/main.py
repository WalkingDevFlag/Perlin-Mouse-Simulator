# main.py
import tkinter as tk
from app_gui import App # Import the App class

if __name__ == "__main__":
    root = tk.Tk()
    app_instance = App(root) # Create an instance of your application
    root.mainloop()