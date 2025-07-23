import tkinter as tk
from tkinter.filedialog import askdirectory
   
def directory():
    return askdirectory(title = 'Select Folder')
    