import tkinter as tk

class Tooltip:
    # Efficient tooltips: https://stackoverflow.com/questions/78207695/tkinter-tooltip-quite-always-not-showing-in-windows-10-enterprise
    def __init__(self, wdgt, txt):
        self.wdgt = wdgt
        self.txt = txt
        self.make_tt()

    def popup(self):
        pop = tk.Toplevel(self.wdgt)
        pop.overrideredirect(True)

        tk.Label(pop, text = self.txt, bg='white', borderwidth=1, relief="solid").pack()
        self.wdgt.bind('<Leave>', lambda x: pop.destroy())
        x_center = self.wdgt.winfo_rootx() #+ self.wdgt.winfo_width() 
        y_center = self.wdgt.winfo_rooty() + self.wdgt.winfo_height()
        pop.geometry(f"+{x_center}+{y_center}")

    def make_tt(self):
        self.wdgt.bind('<Enter>', lambda x: self.popup())