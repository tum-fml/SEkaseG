'''
This file is a function to create a dropdown menu
'''

from tkinter import *
from tkinter import ttk, simpledialog

class DropdownDialog(simpledialog.Dialog):
    def __init__(self, parent, title, options):
        self.options = options
        self.selected_option = StringVar(parent)
        self.selected_option.set(self.options[-1])  # Set the initial value of the dropdown menu
        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        self.option_menu = ttk.OptionMenu(master, self.selected_option, *self.options)
        self.option_menu.pack()
        return self.option_menu

    def apply(self):
        self.result = self.selected_option.get()
