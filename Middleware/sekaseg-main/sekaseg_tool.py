'''
Main file: creates the main window of the tool, which contains the canvas for the objects and the treeview for the folders and objects.
'''

import tkinter as tk
from tkinter import font
import ttkbootstrap as ttk
from tkinter import filedialog, simpledialog, messagebox
import json
import os
import sys
from PIL import ImageTk, Image
import shutil

from canvas import CanvasObject
from new_object import NewObject
from tooltips import Tooltip
from navigate_versions import save_version, go_back, go_forth

class Tool:
    def __init__(self):
        self.root = ttk.Window()
        self.style = ttk.Style("cosmo")
        self.style.colors.primary = '#0065bd' # primary color TUM-Blau
        self.root.state('zoomed') # window takes on size of screen
        self.root.title("Tool")
        width= self.root.winfo_screenwidth() 
        height= self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height)) # setting the window size

        # set current path (necessary for bundling into exe file via pyinstaller)
        application_path = str()
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)

        # icon:
        self.root.iconbitmap(bitmap=os.path.join(application_path, 'Pictogrammers-Material-Forklift.ico'))
        self.root.iconbitmap(default=os.path.join(application_path, 'Pictogrammers-Material-Forklift.ico'))

        # images:
        self.home_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, 'Ionic-Ionicons-Home.32.png')))
        self.new_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, 'Microsoft-Fluentui-Emoji-Mono-New-Button.48.png')))
        self.delete_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, 'Ionic-Ionicons-Trash.48.png')))
        self.backward_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, 'Ionic-Ionicons-Arrow-back.32.png')))
        self.forward_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, 'Ionic-Ionicons-Arrow-forward.32.png')))

        # create sub-windows with draggable frames
        self.panedwindow1 = ttk.PanedWindow(self.root, orient = 'horizontal')
        self.panedwindow1.pack(expand='True', fill='both')
        self.panedwindow2 = ttk.PanedWindow(self.panedwindow1, orient = 'vertical')
        self.canvas_frame = ttk.Frame(self.panedwindow1, relief="solid", borderwidth=0.5)
        self.panedwindow1.add(self.panedwindow2, weight=1)
        self.panedwindow1.add(self.canvas_frame, weight=5)

        self.tree_frame = ttk.Frame(self.panedwindow2, relief="solid", borderwidth=0.5)
        self.button_frame = ttk.Frame(self.panedwindow2, relief="solid", borderwidth=0.5)
        self.panedwindow2.add(self.tree_frame, weight=3)
        self.panedwindow2.add(self.button_frame, weight=1)

        # create a canvas widget inside the right window frame
        vbar = ttk.Scrollbar(self.canvas_frame, orient='vertical')
        vbar.pack(fill='y', side='right')
        hbar = ttk.Scrollbar(self.canvas_frame, orient='horizontal')
        hbar.pack(fill='x', side='bottom')
        self.scrollregion = (0, 0)
        self.canvas = tk.Canvas(self.canvas_frame, width=900, height=900, bg="white", scrollregion=(0,0,self.scrollregion[0], self.scrollregion[1]),
                                yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        self.canvas.pack(fill="both", expand=True, side='left')
        vbar.config(command=self.canvas.yview)
        hbar.config(command=self.canvas.xview)
        
        # Version navigation buttons:
        self.home_button = ttk.Button(self.canvas, command=self.home, image = self.home_img, bootstyle = 'light')
        self.home_button.place(relx = 1, rely = 0, anchor = 'ne')
        Tooltip(self.home_button, "Home")
        self.forward_button = ttk.Button(self.canvas, command=self.forward, image = self.forward_img, bootstyle = 'light', state = 'disabled')
        self.forward_button.place(relx = 0.98, rely = 0, anchor = 'ne')
        Tooltip(self.forward_button, "Go forward")
        self.backward_button = ttk.Button(self.canvas, command=self.backward, image = self.backward_img, bootstyle = 'light', state = 'disabled')
        self.backward_button.place(relx = 0.96, rely = 0, anchor = 'ne')
        Tooltip(self.backward_button, "Go backward")
        
        # menu bar to choose directory
        self.directory = str()
        menu = tk.Menu(self.root)
        self.root.config(menu = menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label = "File", menu = filemenu)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        self.current_folder = None

        # click in the tree in object subwindow to highlight object
        self.file_label = tk.Label(self.tree_frame, bg='white', font=('TkDefaultFont', 12, 'bold'))
        self.file_label.config(text = '/')
        self.file_label.pack()
        self.tree = ttk.Treeview(self.tree_frame, show = 'tree')
        self.tree.bind('<<TreeviewSelect>>', self.highlight_objects)
        self.tree.pack(side = 'left', fill = 'both', expand = 'true')
        self.tree_scroll = tk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side = 'left', fill = 'both')
        self.tree.config(yscrollcommand = self.tree_scroll.set) 
        self.tree_scroll.config(command = self.tree.yview)

        # initialize all needed dictionaries/lists
        self.objects_positions = {} # keys: object names, values: object positions on canvas
        self.object_names = {} # list of object names

        # folders:
        self.folder_frame = ttk.Frame(self.button_frame)
        self.folder_frame.pack()
        self.folder_label = tk.Label(self.folder_frame, text='Folders', bg='white', font=('TkDefaultFont', 12, 'bold'))
        self.folder_label.grid(row = 0, column = 0, columnspan = 2)
        self.new_folder_button = ttk.Button(self.folder_frame, image = self.new_img, command=self.new_folder, bootstyle = 'light')
        self.new_folder_button.grid(row=1, column=0)
        Tooltip(self.new_folder_button, "New folder")
        self.delete_folder_button = ttk.Button(self.folder_frame, image = self.delete_img, command=self.delete_folder, bootstyle = 'light')
        self.delete_folder_button.grid(row = 1, column = 1)
        Tooltip(self.delete_folder_button, "Delete selected folder")
        # separator:
        separator = ttk.Separator(self.button_frame, orient='horizontal')
        separator.pack(fill='x')
        # new objects:
        self.objects_frame = ttk.Frame(self.button_frame)
        self.objects_frame.pack()
        self.objects_label = tk.Label(self.objects_frame, text='Objects', bg='white', font=('TkDefaultFont', 12, 'bold'))
        self.objects_label.grid(row = 0, column = 0, columnspan = 2)
        self.new_object_button = ttk.Button(self.objects_frame, image = self.new_img, command=self.new_object, bootstyle = 'light')
        self.new_object_button.grid(row = 1, column = 0)
        Tooltip(self.new_object_button, "New object")
        self.delete_object_button = ttk.Button(self.objects_frame, image = self.delete_img, command=self.delete_object, bootstyle = 'light')
        self.delete_object_button.grid(row = 1, column = 1)
        Tooltip(self.delete_object_button, "Delete selected object")

    def forward(self):
        go_forth(self.directory, self.backward_button, self.forward_button) # change navigation folders
        self.open_current()

    def backward(self):
        go_back(self.directory, self.backward_button, self.forward_button) # change navigation folders
        self.open_current()

    def open_current(self):
        # clear canvas & treeview:
        self.tree.delete(*self.tree.get_children())
        keys = self.object_names.keys()
        for name in keys:
            self.object_names[name].object_frame.destroy()
        self.object_names.clear()
        # open current folder:
        if self.directory:
            folders_path = os.path.join(self.directory, 'current', 'folders.txt')
            folders = []
            if os.path.isfile(folders_path): # file already exists, put old information in old dict and new information in new dict
                with open(folders_path, "r") as f: # read content first and fill object_saving_dict
                    folders = f.read()[:-2].split(', ')
            if folders != ['']:
                for folder in folders:
                    self.tree.insert('', 'end', text=folder, iid=folder)
            self.fill_tree_and_canvas()
    
    def new_file(self):
        # make space for new file
        self.tree.delete(*self.tree.get_children())
        keys = [key for key in self.object_names.keys()]
        for key in keys:
            self.object_names[key].object_frame.destroy()
        self.directory = str()

        # create objects file if it doesn't exist yet
        project_file = "Projects"
        if not os.path.exists("Projects"):
            os.makedirs(project_file)

        # create object file
        file = simpledialog.askstring("New file", "Enter file name:")
        file_list = os.listdir(project_file)
        while file in file_list:
            messagebox.showinfo("Invalid file name", "File name already exists")
            file = simpledialog.askstring("New file", "Enter file name:")
        if file:
            file_name = os.path.join(project_file, file)
            if not os.path.exists(file_name):
                os.makedirs(file_name)

            self.directory = file_name
            self.file_label.config(text = 'Project: '+file)
            
            # create versions folder & fill with folder files
            os.makedirs(os.path.join(self.directory, 'current'))
            file_path = os.path.join(self.directory, 'current', 'folders.txt')
            if not os.path.exists(file_path):
                with open(file_path, 'w+') as f:
                    f.write('')
            os.makedirs(os.path.join(self.directory, 'back'))
            file_path = os.path.join(self.directory, 'back', 'folders.txt')
            if not os.path.exists(file_path):
                with open(file_path, 'w+') as f:
                    f.write('')
            os.makedirs(os.path.join(self.directory, 'forth'))
            file_path = os.path.join(self.directory, 'forth', 'folders.txt')
            if not os.path.exists(file_path):
                with open(file_path, 'w+') as f:
                    f.write('')

    def open_file(self):
        # if another project is currently open --> clear tree & canvas:
        self.tree.delete(*self.tree.get_children())
        keys = self.object_names.keys()
        for name in keys:
            self.object_names[name].object_frame.destroy()
        self.object_names.clear()
        self.directory = str()

        # get directory for project to be opened, fill tree and display project name:
        self.directory = filedialog.askdirectory()
        if self.directory:
            folders_path = os.path.join(self.directory, 'current', 'folders.txt')
            folders = []
            if os.path.isfile(folders_path): # file already exists, put old information in old dict and new information in new dict
                with open(folders_path, "r") as f: # read content first and fill object_saving_dict
                    folders = f.read()[:-2].split(', ')
            for folder in folders:
                self.tree.insert('', 'end', text=folder, iid=folder)

            self.fill_tree_and_canvas()
            folder = self.directory.split('/')[-1]
            if folder:
                self.file_label.config(text = 'Project: '+folder)
    
    def home(self):
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
    
    def adapt_scrollregion(self, x, y):
        if self.scrollregion[0] < x+250:
            self.canvas.config(scrollregion = (0, 0, x+250, self.scrollregion[1]))
            self.scrollregion = (x+250, self.scrollregion[1])
        if self.scrollregion[1] < y+750: # 750 to have enough space for object expansion
            self.canvas.config(scrollregion = (0, 0, self.scrollregion[0], y+750))
            self.scrollregion = (self.scrollregion[0], y+750)

    def highlight_objects(self, event):
        # unhighlight all objects:
        for obj in list(self.object_names.keys()):
            self.object_names[obj].object_frame.config(highlightthickness = 0)

        # highlight object(s) of selection:
        if self.tree.selection():
            element_name = self.tree.selection()[0]
            if element_name in self.object_names.keys(): # if object has been selected
                self.object_names[element_name].object_frame.config(highlightbackground = '#0065bd', highlightthickness = 5)
            else:
                objects = self.tree.get_children(element_name)
                for obj in objects:
                    self.object_names[obj].object_frame.config(highlightbackground = '#0065bd', highlightthickness = 5)

    """ def on_click(self, event):
        index = self.tree.curselection()
        if index:
            object_name = self.tree.get(index[0])
            x, y = self.objects_positions[object_name]
            self.canvas.xview_moveto(x-250)
            self.canvas.yview_moveto(y-250)
            self.object_names[object_name].object_frame.config(highlightbackground = '#0065bd', highlightthickness = 3)
        item = self.tree.selection()
        if item:
            item = item[0]
            if item in self.object_names.keys():
                self.object_names[item].object_frame.config(highlightbackground = '#0065bd', highlightthickness = 3)

    def on_release(self, event):
        for ob in list(self.object_names.keys()):
            self.object_names[ob].object_frame.config(highlightthickness = 0) """

    # new folder:
    def new_folder(self):
        if not self.directory:
            messagebox.showinfo("No selected project", "Click on 'File' in the upper left corner and select 'New' or 'Open' to select a project folder to save the objects in")
        else:
            save_version(self.directory, self.backward_button)
            folder_name = simpledialog.askstring("New folder", "Enter folder name:")
            folders = self.tree.get_children()
            while folder_name in folders:
                messagebox.showinfo("Invalid folder name", "Folder name already exists")
                folder_name = simpledialog.askstring("New folder", "Enter folder name:")
            self.tree.insert('', 'end', text=folder_name, iid=folder_name)
            folders_path = os.path.join(self.directory, 'current', 'folders.txt')
            with open(folders_path, "a") as f:
                f.write(folder_name+', ')
    
    # delete selected folder:
    def delete_folder(self):
        if not self.directory:
            messagebox.showinfo("No selected project", "Click on 'File' in the upper left corner and select 'New' or 'Open' to select a project folder to save the objects in")
        else:
            save_version(self.directory, self.backward_button)
            folder_name = self.tree.selection()[0]
            if folder_name not in self.object_names.keys(): # ensure a folder ist selected (not an object)
                delete = messagebox.askyesno(title="Delete folder & objects", message = "Are you sure you want to delete this folder and all objects within?")
                if delete:
                    # delete objects in selected folder:
                    objects = self.tree.get_children(folder_name)
                    for obj in objects:
                        self.object_names[obj].delete_object()

                    # delete folder from listview:
                    self.tree.delete(folder_name)

                    # delete folder from folders file:
                    folders_path = os.path.join(self.directory, 'current', 'folders.txt')
                    folders = []
                    with open(folders_path, "r") as f:
                        folders = f.read()[:-2].split(', ')
                    folders.remove(folder_name)
                    with open(folders_path, "w") as f:
                        for folder in folders:
                            f.write(folder+', ')

    # create a new object
    def new_object(self):
        # user must select a folder to save objects in:
        if not self.directory:
            messagebox.showinfo("No selected project", "Click on 'File' in the upper left corner and select 'New' or 'Open' to select a project folder to save the objects in")
        elif not self.tree.get_children():
            messagebox.showinfo("No folder", "Click on the button below to create at least one folder first to store objects in")
        else:
            save_version(self.directory, self.backward_button)
            object_name = str()
            object_name = simpledialog.askstring("Create an object", "Enter the object name:")
            
            if object_name:
                while '.' in object_name:
                    messagebox.showinfo("Invalid object name", "Object name can't contain '.'")
                    object_name = simpledialog.askstring("Create an object", "Enter the object name:")
                while object_name in self.object_names.keys():
                    messagebox.showinfo("Invalid object name", "Object name already exists")
                    object_name = simpledialog.askstring("Create an object", "Enter the object name:")
                # place new object in the next free spot, 4 objects per row:          
                position = (150, 100)
                row = 0
                column = 0
                while position in self.objects_positions.values():
                    if column == 3:
                        column = 0
                        row += 1
                    else:
                        column += 1
                    position = (150+column*200, 100+row*200)
                # collect all object positions in dict:
                self.objects_positions[object_name] = position

                # adapt scrollregion:
                x, y = position
                self.adapt_scrollregion(x, y)

                # create a new folder for the object within the project folder:
                object_file = os.path.join(self.directory, 'current', object_name)
                if not os.path.exists(object_file):
                    os.makedirs(object_file)

                NewObject(self.root, object_name, self.canvas, self.scrollregion, self.tree,
                            self.objects_positions, self.directory, self.object_names, self.backward_button, position[0], position[1])
                
    def delete_object(self):
        if not self.directory:
            messagebox.showinfo("No selected project", "Click on 'File' in the upper left corner and select 'New' or 'Open' to select a project folder to save the objects in")
        else:
            save_version(self.directory, self.backward_button)
            object_name = self.tree.selection()[0]
            if object_name in self.object_names.keys(): # ensure an object has been selected (not a file)
                delete = messagebox.askyesno(title="Delete object", message = "Are you sure you want to delete this object?")
                if delete:
                    self.object_names[object_name].delete_object()

    def run(self):
        self.root.mainloop()
    
    # this is the function to get all created objects in the directory of object
    def search_all_objects(self):
        all_objects = [f for f in os.listdir(os.path.join(self.directory, 'current'))]
        all_objects.remove('folders.txt')
        return all_objects

    def fill_tree_and_canvas(self):
        # get names of all objects from working directory:
        all_objects = self.search_all_objects()
        for name in all_objects:
            # fill canvas:
            file_name = f'{name}.object.txt'
            file_path = os.path.join(self.directory, 'current', name, file_name)

            new_dict = {}
            with open(file_path, 'r') as f:
                object_info = f.read()
                object_info = object_info.replace("'", "\"")
                object_info = object_info.replace("(", "[")
                object_info = object_info.replace(")", "]")
                json_dict = json.loads(object_info)
                new_dict = json_dict["new_dict"]
                new_dict["position"] = tuple(new_dict["position"])
                
                # adapt scrollregion:
                x, y = new_dict['position']
                self.adapt_scrollregion(x, y)

                # place object on canvas:
                obj = CanvasObject(self.canvas, self.scrollregion, self.tree, self.objects_positions,
                                                   self.directory, self.object_names, name, new_dict, self.backward_button)
                self.objects_positions[name] = (x, y)
                self.object_names[name] = obj
            
            # fill tree with object name:
            parent = new_dict['folder']
            self.tree.insert(parent, 'end', text=name, iid=name)

# Create the main window
main_window = Tool()

# Run the main event loop
main_window.run()
