import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk, font
import os
import shutil
import sys
import json
from PIL import ImageTk, Image

import canvas
from object_changements import object_changements
from publish_change import publish
from vertical_scrolled_frame import VerticalScrolledFrame
import DropDown
from import_from import data_from_csv, data_from_pdf, data_from_txt, data_from_image
from tooltips import Tooltip

class ChangeObject:
    def __init__(self, canvas, scrollregion, tree, positions, directory, object_names, object_name, object_dict, back_button, directly2canvas=False):
        self.directory = directory
        self.object_names = object_names
        self.object_name = object_name
        self.canvas = canvas
        self.scrollregion = scrollregion
        self.tree = tree
        self.positions = positions
        self.back_button = back_button
        self.directly2canvas = directly2canvas

        if directly2canvas == True: # use change_object as highway (directly2canvas) for updating references of objects
            # get old dict from .txt file:
            file_name = f'{self.object_name}.object.txt'
            file_path = os.path.join(self.directory, 'current', self.object_name, file_name)
            old_dict = {}

            with open(file_path, 'r') as f:
                object_info = f.read()
                object_info = object_info.replace("'", "\"")
                object_info = object_info.replace("(", "[")
                object_info = object_info.replace(")", "]")
                json_dict = json.loads(object_info)
                old_dict = json_dict["old_dict"]

            self.new_object_dict = object_dict
            self.object_dict = old_dict
            self.save()
        else:
            # for creating exe file via pyinstaller: images have to be added separately & current path has to be set
            application_path = str()
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            elif __file__:
                application_path = os.path.dirname(__file__)

            self.defaultFont = font.nametofont("TkDefaultFont")
            self.defaultFont.configure(family = "Helvetica", size = 10)
            root = tk.Toplevel()
            root.iconbitmap(os.path.join(application_path, 'Pictogrammers-Material-Forklift.ico'))
            root.geometry("875x900")
            root.title(object_name)
            root.protocol("WM_DELETE_WINDOW", self.close)

            self.master = root
            self.frame = VerticalScrolledFrame(self.master)
            self.frame.pack(side=tk.TOP, fill=tk.Y, expand = 'true') 
            self.object_dict = object_dict
            self.x = object_dict["position"][0]
            self.y = object_dict["position"][1]

            # Images
            self.delete_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Trash.32.png")))
            self.show_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Eye-outline.32.png")))
            self.new_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Microsoft-Fluentui-Emoji-Mono-New-Button.32.png")))
            self.publish_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Megaphone-outline.32.png")))
            self.subscribe_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Github-Octicons-Bell-24.32.png")))
            self.save_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Save-outline.32.png")))
            self.unsubscribe_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Github-Octicons-Bell-slash-24.32.png")))
            self.import_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Enter-outline.32.png")))
            self.hide_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Eye-off.32.png")))
            self.open_file_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Microsoft-Fluentui-Emoji-Mono-Open-File-Folder.32.png")))

            # Initialize object data structures
            self.new_object_dict = {
                "objectives": [],
                "attributes": [],
                "inputs": [],
                "outputs": [],
                "files": [],
                "references": [],
                "subscribers": [],
                "folder": '',
                "position": [self.x, self.y]
            }

            self.object_name = object_name

            # tkinter-labels:
            self.objective_checkbuttons = []
            self.attribute_labels = []
            self.input_labels = []
            self.output_labels = []
            self.file_labels = []
            self.choose_file_buttons = []
            self.open_file_buttons = []
            self.reference_labels = []
            self.subscriber_labels = []
            self.unsubscribe_buttons = []
            self.attribute_tol_labels = []

            # Object name label
            self.object_name_label = tk.Label(self.frame.interior, text=self.object_name, font = ("Helvetica", 14, "bold"), bg = 'white')
            self.object_name_label.grid(row=0, column=0, columnspan=5)

            # Import from button
            self.import_button = ttk.Button(self.frame.interior, image=self.import_img, command = self.import_, bootstyle = "light")
            self.import_button.grid(row=1, column=0)
            Tooltip(self.import_button, "Import data from ...")
        
            # Save button
            self.save_button = ttk.Button(self.frame.interior, image=self.save_img, command=self.save, bootstyle = "light")
            self.save_button.grid(row=1, column=1)
            Tooltip(self.save_button, "Save object")

            # Delete button
            self.delete_button = ttk.Button(self.frame.interior, image=self.delete_img, command=self.delete_object, bootstyle = 'light')
            self.delete_button.grid(row=1, column=2)
            Tooltip(self.delete_button, "Delete object")

            # Subscribe button
            self.subscribe_button = ttk.Button(self.frame.interior, image=self.subscribe_img, command=self.add_subscriber, bootstyle ='light')
            self.subscribe_button.grid(row=1, column=3)
            Tooltip(self.subscribe_button, "Subscribe")

            # Save and publish button
            self.save_publish_button = ttk.Button(self.frame.interior, image=self.publish_img, command=self.save_publish, bootstyle = 'light')
            self.save_publish_button.grid(row=1, column=4)
            Tooltip(self.save_publish_button, "Save & Publish")

            # Object frames
            self.folder_frame = tk.Frame(self.frame.interior, bg = 'white')
            self.folder_frame.grid(row=2, column=0, columnspan=5)
            self.folder_label = tk.Label(self.folder_frame, text = 'Folder', font=("Helvetica", 14), bg = 'white')
            self.folder_label.pack()
            parents = list(self.tree.get_children(''))
            value_var = tk.StringVar(self.folder_frame)
            self.folder_combobox = ttk.Combobox(self.folder_frame, state="readonly", values=parents, textvariable=value_var)
            self.folder_combobox.pack()
            if self.object_dict["folder"]:
                ind = parents.index(self.object_dict["folder"])
                self.folder_combobox.current(ind)
            self.new_object_dict["folder"] = value_var

            # Objectives frame
            self.objective_frame = tk.Frame(self.frame.interior, bg = 'white')
            self.objective_frame.grid(row=3, column=0, columnspan=5)
            self.objective_label = tk.Label(self.objective_frame, bg = 'white', text="Objectives", font=("Helvetica", 14))
            self.objective_label.grid(row=0, column=0)

            self.add_objective_button = ttk.Button(self.objective_frame, image=self.new_img, command=self.add_objective, bootstyle = 'light')
            self.add_objective_button.grid(row=1, column=0)
            Tooltip(self.add_objective_button, "Add Objective")

            self.delete_objective_button = ttk.Button(self.objective_frame, image=self.delete_img, command=self.delete_objective, bootstyle = 'light')
            self.delete_objective_button.grid(row=2, column=0)
            Tooltip(self.delete_objective_button, "Delete Objective")

            if self.object_dict["objectives"]:
                for i, (label, state) in enumerate(self.object_dict["objectives"]):
                    # Label widget
                    state_var = tk.IntVar(self.objective_frame)
                    self.objective_checkbuttons.append(ttk.Checkbutton(self.objective_frame, text = label, variable=state_var))

                    # Checkbutton with state
                    if state == 1:
                        state_var.set(1)
                        self.objective_checkbuttons[-1].state = state_var
                    self.objective_checkbuttons[-1].grid(row=i+3, column=0)
                    self.new_object_dict["objectives"].append([label, state_var])

            # attributes frame
            self.attribute_frame = tk.Frame(self.frame.interior, bg='white')
            self.attribute_frame.grid(row=4, column=0, columnspan=5)
            self.attribute_label = tk.Label(self.attribute_frame, text="Attributes", font=("Helvetica", 14), bg='white')
            self.attribute_label.grid(row=0, column=0, columnspan=6)

            self.add_attribute_button = ttk.Button(self.attribute_frame, image=self.new_img, command=self.add_attribute, bootstyle = 'light')
            self.add_attribute_button.grid(row=1, column=0, columnspan=6)
            Tooltip(self.add_attribute_button, "Add attribute")

            self.delete_attribute_button = ttk.Button(self.attribute_frame, image=self.delete_img, command=self.delete_attribute, bootstyle = 'light')
            self.delete_attribute_button.grid(row=2, column=0, columnspan=6)
            Tooltip(self.delete_attribute_button, "Delete attribute")

            self.attributes_tol_button = ttk.Button(self.attribute_frame, compound='left', image=self.show_img, text = ' Tolerances', command=self.attribute_tol, bootstyle = 'light')
            self.attributes_tol_button.grid(row=3, column=0, columnspan=6)
            Tooltip(self.attributes_tol_button, "Add attribute tolerances")

            self.attribute_name_label = tk.Label(self.attribute_frame, text='Name', bg='white')
            self.attribute_shortcut_label = tk.Label(self.attribute_frame, text='Symbol', bg='white')
            self.attribute_value_label = tk.Label(self.attribute_frame, text='Value', bg='white')
            self.attribute_unit_label = tk.Label(self.attribute_frame, text='Unit', bg='white')
            self.attribute_tol_plus = tk.Label(self.attribute_frame, text="+", bg='white')
            self.attribute_tol_minus = tk.Label(self.attribute_frame, text="-", bg='white')

            if self.object_dict["attributes"]:
                self.attribute_name_label.grid(row=4, column=0)
                self.attribute_shortcut_label.grid(row=4, column=1)
                self.attribute_value_label.grid(row=4, column=2)
                self.attribute_unit_label.grid(row=4, column=3)
                if self.object_dict["attributes"][0][4]: # if there are tolerances
                    self.attributes_tol_button.config(image=self.hide_img)
                    Tooltip(self.attributes_tol_button, "Remove attribute tolerances")
                    self.attribute_tol_plus.grid(row=4, column=4)
                    self.attribute_tol_minus.grid(row=4, column=5)
                # insert attributes:
                for i, (label, shortcut, value, unit, tol) in enumerate(self.object_dict["attributes"]):
                    # Label widget
                    self.attribute_labels.append(tk.Label(self.attribute_frame, text=label, bg='white'))
                    self.attribute_labels[-1].grid(row=i+5, column=0)

                    # Shortcut widget
                    shortcut_var = tk.StringVar(self.attribute_frame) 
                    self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=shortcut_var))
                    self.attribute_labels[-1].insert(0, shortcut)
                    self.attribute_labels[-1].grid(row=i+5, column=1)

                    # Value widget
                    value_var = tk.StringVar(self.attribute_frame) 
                    self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=value_var))
                    self.attribute_labels[-1].insert(0, value)
                    self.attribute_labels[-1].grid(row=i+5, column=2)

                    # Unit widget
                    unit_var = tk.StringVar(self.attribute_frame) 
                    self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=unit_var))
                    self.attribute_labels[-1].insert(0, unit)
                    self.attribute_labels[-1].grid(row=i+5, column=3)

                    # Tolerance widget
                    if tol != []:
                        plus_var = tk.StringVar(self.attribute_frame)
                        self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                        self.attribute_tol_labels[-1].insert(0, tol[0])
                        self.attribute_tol_labels[-1].grid(row=i+5, column=4)
                        minus_var = tk.StringVar(self.attribute_frame)
                        self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                        self.attribute_tol_labels[-1].insert(0, tol[1])
                        self.attribute_tol_labels[-1].grid(row=i+5, column=5)
                        self.new_object_dict["attributes"].append([label, shortcut_var, value_var, unit_var, [plus_var, minus_var]])
                    else:
                        self.new_object_dict["attributes"].append([label, shortcut_var, value_var, unit_var, []])

            # inputs frame
            self.input_frame = tk.Frame(self.frame.interior, bg='white')
            self.input_frame.grid(row=5, column=0, columnspan=5)
            self.input_label = tk.Label(self.input_frame, text="Inputs", font=("Helvetica", 14), bg='white')
            self.input_label.grid(row=0, column=0, columnspan=4)

            self.add_input_button = ttk.Button(self.input_frame, image=self.new_img, command=self.add_input, bootstyle = 'light')
            self.add_input_button.grid(row=1, column=0, columnspan=4)
            Tooltip(self.add_input_button, "Add Input")
            self.delete_input_button = ttk.Button(self.input_frame, image=self.delete_img, command=self.delete_input, bootstyle='light')
            self.delete_input_button.grid(row=2, column=0, columnspan=4)
            Tooltip(self.delete_input_button, "Delete Input")
            
            self.input_name_label = tk.Label(self.input_frame, text='Name', bg='white')
            self.input_shortcut_label = tk.Label(self.input_frame, text='Symbol', bg='white')
            self.input_value_label = tk.Label(self.input_frame, text='Value', bg='white')
            self.input_unit_label = tk.Label(self.input_frame, text='Unit', bg='white')

            if self.object_dict["inputs"]:
                self.input_name_label.grid(row=3, column=0)
                self.input_shortcut_label.grid(row=3, column=1)
                self.input_value_label.grid(row=3, column=2)
                self.input_unit_label.grid(row=3, column=3)
                for i, (label, shortcut, value, unit) in enumerate(self.object_dict["inputs"]):
                    # Label widget
                    self.input_labels.append(tk.Label(self.input_frame, text=label, bg='white'))
                    self.input_labels[-1].grid(row=i+4, column=0)

                    # Shortcut widget
                    shortcut_var = tk.StringVar(self.input_frame) 
                    self.input_labels.append(tk.Entry(self.input_frame, textvariable=shortcut_var))
                    self.input_labels[-1].insert(0, shortcut)
                    self.input_labels[-1].grid(row=i+4, column=1)

                    # Value widget
                    value_var = tk.StringVar(self.input_frame) 
                    self.input_labels.append(tk.Entry(self.input_frame, textvariable=value_var))
                    self.input_labels[-1].insert(0, value)
                    self.input_labels[-1].grid(row=i+4, column=2)

                    # Unit widget
                    unit_var = tk.StringVar(self.input_frame) 
                    self.input_labels.append(tk.Entry(self.input_frame, textvariable=unit_var))
                    self.input_labels[-1].insert(0, unit)
                    self.input_labels[-1].grid(row=i+4, column=3)

                    self.new_object_dict["inputs"].append([label, shortcut_var, value_var, unit_var])

            # outputs frame
            self.output_frame = tk.Frame(self.frame.interior, bg='white')
            self.output_frame.grid(row=6, column=0, columnspan=5)
            self.output_label = tk.Label(self.output_frame, text="Outputs", font=("Helvetica", 14), bg='white')
            self.output_label.grid(row=0, column=0, columnspan=4)

            self.add_output_button = ttk.Button(self.output_frame, image=self.new_img, command=self.add_output, bootstyle='light')
            self.add_output_button.grid(row=1, column=0, columnspan=4)
            Tooltip(self.add_output_button, "Add Output")
            self.delete_output_button = ttk.Button(self.output_frame, image=self.delete_img, command=self.delete_output, bootstyle='light')
            self.delete_output_button.grid(row=2, column=0, columnspan=4)
            Tooltip(self.delete_output_button, "Delete Output")

            self.output_name_label = tk.Label(self.output_frame, text='Name', bg='white')
            self.output_shortcut_label = tk.Label(self.output_frame, text='Symbol', bg='white')
            self.output_value_label = tk.Label(self.output_frame, text='Value', bg='white')
            self.output_unit_label = tk.Label(self.output_frame, text='Unit', bg='white')

            if self.object_dict["outputs"]:
                self.output_name_label.grid(row=3, column=0)
                self.output_shortcut_label.grid(row=3, column=1)
                self.output_value_label.grid(row=3, column=2)
                self.output_unit_label.grid(row=3, column=3)
                for i, (label, shortcut, value, unit) in enumerate(self.object_dict["outputs"]):
                    # label widget
                    self.output_labels.append(tk.Label(self.output_frame, text=label, bg='white'))
                    self.output_labels[-1].grid(row=i+4, column=0)

                    # shortcut widget
                    shortcut_var = tk.StringVar(self.output_frame) 
                    self.output_labels.append(tk.Entry(self.output_frame, textvariable=shortcut_var))
                    self.output_labels[-1].insert(0, shortcut)
                    self.output_labels[-1].grid(row=i+4, column=1)

                    # value widget
                    value_var = tk.StringVar(self.output_frame) 
                    self.output_labels.append(tk.Entry(self.output_frame, textvariable=value_var))
                    self.output_labels[-1].insert(0, value)
                    self.output_labels[-1].grid(row=i+4, column=2)
                    
                    # unit widget
                    unit_var = tk.StringVar(self.output_frame) 
                    self.output_labels.append(tk.Entry(self.output_frame, textvariable=unit_var))
                    self.output_labels[-1].insert(0, unit)
                    self.output_labels[-1].grid(row=i+4, column=3)

                    self.new_object_dict["outputs"].append([label, shortcut_var, value_var, unit_var])

            # files frame
            self.file_frame = tk.Frame(self.frame.interior, bg='white')
            self.file_frame.grid(row=7, column=0, columnspan=5)
            self.file_label = tk.Label(self.file_frame, text="Files", font=("Arial", 16), bg='white')
            self.file_label.grid(row=0, column=0, columnspan=3)
            
            self.add_file_button = ttk.Button(self.file_frame, image=self.new_img, command=self.add_file, bootstyle='light')
            self.add_file_button.grid(row=1, column=0, columnspan=3)
            Tooltip(self.add_file_button, "Add File")
            self.delete_file_button = ttk.Button(self.file_frame, image=self.delete_img, command=self.delete_file, bootstyle='light')
            self.delete_file_button.grid(row=2, column=0, columnspan=3)
            Tooltip(self.delete_file_button, "Delete File")

            if self.object_dict["files"]:
                for i, label in enumerate(self.object_dict["files"]):
                    # choose file button
                    self.choose_file_buttons.append(ttk.Button(self.file_frame, image=self.open_file_img, bootstyle='light', command=self.choose_file))
                    self.choose_file_buttons[-1].grid(row=i+3, column=0)
                    Tooltip(self.choose_file_buttons[-1], "Choose file")
                    # label widget
                    self.file_labels.append(tk.Label(self.file_frame, text=label, bg='white'))
                    self.file_labels[-1].grid(row=i+3, column=1)
                    self.new_object_dict["files"].append(label)

                    file_list = os.listdir(os.path.join(self.directory, 'current', self.object_name)) # get list of files in object's directory
                    file_list_without_filetypes = [file.rsplit(".", 1)[0] for file in file_list] # remove endings
                    for i, file in enumerate(file_list_without_filetypes):
                        if file == self.new_object_dict["files"][-1]:
                            path = os.path.join(self.directory, 'current', self.object_name, file_list[i])
                            self.open_file_buttons.append(ttk.Button(self.file_frame, text=file_list[i], command=lambda: self.open_file(path), bootstyle='light'))
                            self.open_file_buttons[-1].grid(row=i+3, column=2)
                            Tooltip(self.open_file_buttons[-1], "Open file")
                            break

            # Reference frame
            self.reference_frame = tk.Frame(self.frame.interior, bg='white')
            self.reference_frame.grid(row=8, column=0, columnspan=5)
            self.reference_label = tk.Label(self.reference_frame, text="References", font=("Helvetiva", 14), bg='white')
            self.reference_label.grid(row=0, column=0, sticky="w")
            self.add_reference_button = ttk.Button(self.reference_frame, image=self.new_img, command=self.add_reference, bootstyle='light')
            self.add_reference_button.grid(row=1, column=0, columnspan=2)
            Tooltip(self.add_reference_button, "Add Reference")
            self.delete_reference_button = ttk.Button(self.reference_frame, image=self.delete_img, command=self.delete_reference, bootstyle='light')
            self.delete_reference_button.grid(row=2, column=0, columnspan=2)
            Tooltip(self.delete_reference_button, "Delete Reference")
            for i, value in enumerate(self.object_dict["references"]):
                # create a label widget
                options = list(self.object_names.keys())
                value_var = tk.StringVar(self.reference_frame, self.object_dict["references"][i])
                self.reference_labels.append(ttk.Combobox(self.reference_frame, state="readonly", values=options, textvariable=value_var))
                ind = options.index(value)
                self.reference_labels[-1].current(ind)
                self.reference_labels[-1].grid(row = len(self.reference_labels)+3, column = 0)
                
                self.new_object_dict["references"].append(value_var)            

            # Subscribers frame
            self.subscriber_frame = tk.Frame(self.frame.interior, bg='white')
            self.subscriber_frame.grid(row=9, column=0, columnspan=5)
            self.subscriber_label = tk.Label(self.subscriber_frame, text="Subscribers", font=("Helvetica", 14), bg='white')
            self.subscriber_label.grid(row=0, column=0, columnspan=2)

            if self.object_dict["subscribers"]:
                for i, email in enumerate(self.object_dict["subscribers"]):
                    self.new_object_dict["subscribers"].append(email)
                    self.unsubscribe_buttons.append(ttk.Button(self.subscriber_frame, image=self.unsubscribe_img, bootstyle='light'))
                    self.unsubscribe_buttons[-1].grid(row=i+1, column=0)
                    Tooltip(self.unsubscribe_buttons[-1], "Unsubscribe")

                    self.subscriber_labels.append(tk.Label(self.subscriber_frame, text=email, bg='white'))
                    self.subscriber_labels[-1].grid(row=i+1, column=1)

                    self.unsubscribe_buttons[-1].configure(command=lambda: self.unsubscribe(email))

    def close(self): # protocol for closing window (x-button on window frame)
        # don't save changes --> don't update .txt file and use object_dict instead of new_object_dict for canvas
        obj = canvas.CanvasObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory, self.object_names,
                                           self.object_name, self.object_dict, self.back_button)
        self.object_names[self.object_name] = obj
        self.master.destroy()

    def delete_object(self):
        delete = messagebox.askyesno(title="Delete object", message = "Are you sure you want to delete this object?")
        if delete:
            folderpath = os.path.join(self.directory, 'current', self.object_name)
            if os.path.exists(folderpath):
                shutil.rmtree(folderpath)
            lb_index = self.tree.get(0, tk.END).index(self.object_name)
            self.tree.delete(lb_index)
            self.positions.pop(self.object_name)
            self.master.destroy()

    def save(self):
        # transform tkinter data types used for entry boxes to string values:
        for i in range(len(self.new_object_dict["objectives"])):
            self.new_object_dict["objectives"][i] = [self.new_object_dict["objectives"][i][0], self.new_object_dict["objectives"][i][1].get()]
        for i in range(len(self.new_object_dict["attributes"])):
            if self.new_object_dict["attributes"][i][4] == []:
                self.new_object_dict["attributes"][i] = [self.new_object_dict["attributes"][i][0], self.new_object_dict["attributes"][i][1].get(),
                                                     self.new_object_dict["attributes"][i][2].get(), self.new_object_dict["attributes"][i][3].get(), []]
            else:
                tols = [self.new_object_dict["attributes"][i][4][0].get(), self.new_object_dict["attributes"][i][4][1].get()]
                self.new_object_dict["attributes"][i] = [self.new_object_dict["attributes"][i][0], self.new_object_dict["attributes"][i][1].get(),
                                                     self.new_object_dict["attributes"][i][2].get(),self.new_object_dict["attributes"][i][3].get(), tols]
        for i in range(len(self.new_object_dict["inputs"])):
            self.new_object_dict["inputs"][i] = [self.new_object_dict["inputs"][i][0], self.new_object_dict["inputs"][i][1].get(),
                                                 self.new_object_dict["inputs"][i][2].get(), self.new_object_dict["inputs"][i][3].get()]
        for i in range(len(self.new_object_dict["outputs"])):
            self.new_object_dict["outputs"][i] = [self.new_object_dict["outputs"][i][0], self.new_object_dict["outputs"][i][1].get(),
                                                  self.new_object_dict["outputs"][i][2].get(), self.new_object_dict["outputs"][i][3].get()]
        """ for i in range(len(self.new_object_dict["files"])):
            self.new_object_dict["files"][i] = self.new_object_dict["files"][i].get() """
        for i in range(len(self.new_object_dict["references"])):
            self.new_object_dict["references"][i] = self.new_object_dict["references"][i].get()
        self.new_object_dict["folder"] = self.new_object_dict["folder"].get()

        # Define the name of the directory and the file to be opened
        directory_name = self.directory
        file_name = f"{self.object_name}.object.txt"

        # Create or open the file
        file_path = os.path.join(directory_name, 'current', self.object_name, file_name)

        object_dict = {
            "new_dict": self.new_object_dict,
            "old_dict": self.object_dict
        }

        with open(file_path, "w") as f:
            f.write(str(object_dict))

        obj = canvas.CanvasObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory, self.object_names,
                                           self.object_name, self.new_object_dict, self.back_button)
        self.object_names[self.object_name] = obj
        self.tree.delete(self.object_name)
        parent = self.new_object_dict['folder']
        self.tree.insert(parent, 'end', text=self.object_name, iid = self.object_name)

        if self.directly2canvas == False:
            deleted_refs = [ref for ref in self.object_dict["references"] if ref not in self.new_object_dict["references"]] # get deleted references
            for ref in deleted_refs:
                file_name = f'{ref}.object.txt'
                file_path = os.path.join(self.directory, 'current', ref, file_name)
                old_dict = {}

                # open dict of deleted reference:
                with open(file_path, 'r') as f:
                    object_info = f.read()
                    object_info = object_info.replace("'", "\"")
                    object_info = object_info.replace("(", "[")
                    object_info = object_info.replace(")", "]")
                    json_dict = json.loads(object_info)
                    old_dict = json_dict["new_dict"]
                
                # remove object name form dict of deleted reference:
                if self.object_name in old_dict["references"]:
                    new_dict = old_dict
                    new_dict["references"].remove(self.object_name)

                    object_dict = {
                        "new_dict": new_dict,
                        "old_dict": old_dict
                    }

                    # save changes in dict of deleted reference:
                    with open(file_path, "w") as f:
                        f.write(str(object_dict))

                    # refresh object on canvas
                    self.object_names[ref].object_frame.destroy()
                    ob = canvas.CanvasObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory, self.object_names,
                                            ref, new_dict, self.back_button)
                    self.object_names[ref] = ob

            new_refs = [ref for ref in self.new_object_dict["references"] if ref not in self.object_dict["references"]] # get list of newly added references
            for ref in new_refs:
                file_name = f'{ref}.object.txt'
                file_path = os.path.join(self.directory, 'current', ref, file_name)
                old_dict = {}

                # read dict of new reference:
                with open(file_path, 'r') as f:
                    object_info = f.read()
                    object_info = object_info.replace("'", "\"")
                    object_info = object_info.replace("(", "[")
                    object_info = object_info.replace(")", "]")
                    json_dict = json.loads(object_info)
                    old_dict = json_dict["new_dict"]
                
                # add object name to dict of new reference:
                if self.object_name not in old_dict["references"]:
                    new_dict = old_dict
                    new_dict["references"].append(self.object_name)

                    object_dict = {
                        "new_dict": new_dict,
                        "old_dict": old_dict
                    }

                    # save changes in dict of new reference:
                    with open(file_path, "w") as f:
                        f.write(str(object_dict))

                    # refresh object on canvas
                    self.object_names[ref].object_frame.destroy()
                    ob = canvas.CanvasObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory, self.object_names,
                                            ref, new_dict, self.back_button)
                    self.object_names[ref] = ob

            self.master.destroy()
    
    def save_publish(self):
        self.save()
        changements = {}
        object_folder = os.path.join(self.directory, 'current', self.object_name)
        changements[self.object_name] = object_changements(self.object_name, object_folder)
        for ref in self.new_object_dict["references"]:
            changements[ref] = object_changements(ref, os.path.join(self.directory, 'current', ref))
        current_folder = os.path.join(self.directory, 'current')
        publish(self.object_name, changements, current_folder)
    
    def add_subscriber(self):
        email = simpledialog.askstring("Add subscriber", "Enter e-mail address:")
        if email:
            self.new_object_dict["subscribers"].append(email)
            length = len(self.subscriber_labels)
            # self.unsubscribe_buttons.append(tk.Button(self.subscriber_frame, image=self.unsubscribe_img, bg='white'))
            self.unsubscribe_buttons.append(ttk.Button(self.subscriber_frame, image=self.unsubscribe_img, bootstyle='light'))
            self.unsubscribe_buttons[-1].grid(row=length+1, column=0)
            Tooltip(self.unsubscribe_buttons[-1], "Unsubscribe")

            self.subscriber_labels.append(tk.Label(self.subscriber_frame, text=email, bg='white'))
            self.subscriber_labels[-1].grid(row=length+1, column=1)

            self.unsubscribe_buttons[-1].configure(command=lambda: self.unsubscribe(email))

    def unsubscribe(self, email):
        pos = self.new_object_dict["subscribers"].index(email)
        self.new_object_dict["subscribers"].pop(pos)
        self.subscriber_labels.pop(pos).destroy()
        self.unsubscribe_buttons.pop(pos).destroy()

    def import_(self):
        import_data = {}
        options1 = ['txt', 'PDF', 'CSV', 'PNG/JPG']
        dialog1 = DropDown.DropdownDialog(self.frame.interior, 'Choose a file type for importing data:', options1)
        dialog2_res = str()
        if dialog1.result == 'CSV':
            options2 = ['Everything', 'Only defined elements']
            dialog2 = DropDown.DropdownDialog(self.frame.interior, 'Import:', options2)
            dialog2_res = dialog2.result
            files = [('CSV', '.csv')]
            import_directory = filedialog.askopenfilename(filetypes=files)
            if import_directory:
                import_data = data_from_csv(import_directory, dialog2.result, self.new_object_dict)
        elif dialog1.result == 'PDF':
            options2 = ['Everything', 'Only defined elements']
            dialog2 = DropDown.DropdownDialog(self.frame.interior, 'Import:', options2)
            dialog2_res = dialog2.result
            files = [('PDF', '.pdf')]
            import_directory = filedialog.askopenfilename(filetypes=files)
            if import_directory:
                import_data = data_from_pdf(import_directory, dialog2.result, self.new_object_dict)
        elif dialog1.result == 'txt':
            options2 = ['Everything', 'Only defined elements']
            dialog2 = DropDown.DropdownDialog(self.frame.interior, 'Import:', options2)
            dialog2_res = dialog2.result
            files = [('txt', '.txt')]
            import_directory = filedialog.askopenfilename(filetypes=files)
            if import_directory:
                import_data = data_from_txt(import_directory, dialog2.result, self.new_object_dict)
        elif dialog1.result == 'PNG/JPG':
            dialog2_res = 'Only defined elements'
            files = [('PNG', '.png'), ('JPG', '.jpg')]
            import_directory = filedialog.askopenfilename(filetypes=files)
            if import_directory:
                import_data = data_from_image(import_directory, self.new_object_dict)

        if import_data:
            self.insert_import_data(dialog2_res, import_data)
    
    def insert_import_data(self, dialog2, import_data):   
        if dialog2 == 'Only defined elements':
            for (ilabel, state) in import_data["objectives"]:
                for i, (label,_) in enumerate(self.new_object_dict["objectives"]):
                    if ilabel == label:
                        if state == 1:
                            self.objective_checkbuttons[i].select()
                        else:
                            self.objective_checkbuttons[i].deselect()
            for (ilabel, shortcut, value, unit, tol) in import_data["attributes"]:
                for i, (label,_,_,_,_) in enumerate(self.new_object_dict["attributes"]):
                    if ilabel == label:
                        self.attribute_labels[4*i+1].delete(0, tk.END) # insert shortcut, override if it already exists
                        self.attribute_labels[4*i+1].insert(0, shortcut)
                        self.attribute_labels[4*i+2].delete(0, tk.END) # insert value, override if it already exists
                        self.attribute_labels[4*i+2].insert(0, value)
                        self.attribute_labels[4*i+3].delete(0, tk.END) # insert unit, override if it already exists
                        self.attribute_labels[4*i+3].insert(0, unit)
                        # if an imported attribute has tolerances:
                        if tol:
                            # if there are not tolerances added yet, add tolerance entry boxes for every attribute
                            if not self.attribute_tol_plus.winfo_ismapped():
                                self.attributes_tol_button.config(image=self.hide_img)
                                Tooltip(self.attributes_tol_button, "Remove attribute tolerances")
                                self.attribute_tol_plus.grid(row=4, column=4)
                                self.attribute_tol_minus.grid(row=4, column=5)
                                for j in range(len(self.new_object_dict["attributes"])):
                                    plus_var = tk.StringVar(self.attribute_frame)
                                    self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                                    self.attribute_tol_labels[-1].grid(row=j+5, column=4)

                                    minus_var = tk.StringVar(self.attribute_frame)
                                    self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                                    self.attribute_tol_labels[-1].grid(row=j+5, column=5)
                                    self.new_object_dict["attributes"][j][4] = [plus_var, minus_var]
                            # append tolerances of the imported attribute:
                            self.attribute_tol_labels[2*i].insert(0, tol[0])
                            self.attribute_tol_labels[2*i+1].insert(0, tol[1])
            for (ilabel, shortcut, value, unit) in import_data["inputs"]:
                for i, (label,_,_,_) in enumerate(self.new_object_dict["inputs"]):
                    if ilabel == label:
                        self.input_labels[4*i+1].delete(0, tk.END)
                        self.input_labels[4*i+1].insert(0, shortcut)
                        self.input_labels[4*i+2].delete(0, tk.END)
                        self.input_labels[4*i+2].insert(0, value)
                        self.input_labels[4*i+3].delete(0, tk.END)
                        self.input_labels[4*i+3].insert(0, unit)
            for (ilabel, shortcut, value, unit) in import_data["outputs"]:
                for i, (label,_,_,_) in enumerate(self.new_object_dict["outputs"]):
                    if ilabel == label:
                        self.output_labels[4*i+1].delete(0, tk.END)
                        self.output_labels[4*i+1].insert(0, shortcut)
                        self.output_labels[4*i+2].delete(0, tk.END)
                        self.output_labels[4*i+2].insert(0, value)
                        self.output_labels[4*i+3].delete(0, tk.END)
                        self.output_labels[4*i+3].insert(0, unit)
            for (ilabel, value) in import_data["files"]:
                for i, (label,_) in enumerate(self.new_object_dict["files"]):
                    if ilabel == label:
                        self.file_labels[2*i+1].delete(0, tk.END)
                        self.file_labels[2*i+1].insert(0, value)
                    
        else: # option import "Everything"
            # current folder is overwritten:
            folders = self.tree.get_children()
            if import_data['folder'] in folders:
                ind = folders.index(import_data["folder"])
                self.folder_combobox.current(ind)

            # imported data for all other properties is appended:
            for ob in import_data["objectives"]:
                name, state = ob
                l = len(self.new_object_dict["objectives"])
                state_var = tk.IntVar(self.objective_frame)
                # self.objective_checkbuttons.append(tk.Checkbutton(self.objective_frame, text = name, variable=state_var, bg='white'))
                self.objective_checkbuttons.append(ttk.Checkbutton(self.objective_frame, text = name, variable=state_var))
                self.objective_checkbuttons[-1].grid(row=l+3, column=0)
                if state == 'True':
                    # self.objective_checkbuttons[-1].select()
                    self.objective_checkbuttons[-1].state(['selected'])
                self.new_object_dict["objectives"].append([name, state_var])

            for at in import_data["attributes"]:
                if not self.new_object_dict["attributes"]:
                    self.attribute_name_label.grid(row=4, column=0)
                    self.attribute_shortcut_label.grid(row=4, column=1)
                    self.attribute_value_label.grid(row=4, column=2)
                    self.attribute_unit_label.grid(row=4, column=3)
                name, shortcut, value, unit, tol = at
                length = len(self.new_object_dict["attributes"])
                self.attribute_labels.append(tk.Label(self.attribute_frame, text=name, bg='white'))
                self.attribute_labels[-1].grid(row=length+5, column=0)

                shortcut_var = tk.StringVar(self.master)
                self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=shortcut_var))
                self.attribute_labels[-1].grid(row=length+5, column=1)
                self.attribute_labels[-1].insert(0, shortcut)

                value_var = tk.StringVar(self.master) 
                self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=value_var))
                self.attribute_labels[-1].grid(row=length+5, column=2)
                self.attribute_labels[-1].insert(0, value)

                unit_var = tk.StringVar(self.master) 
                self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=unit_var))
                self.attribute_labels[-1].grid(row=length+5, column=3)
                self.attribute_labels[-1].insert(0, unit)

                self.new_object_dict["attributes"].append([name, shortcut_var, value_var, unit_var, []])
                # if tolerances are added, create entry boxes for new entries:
                if self.attribute_tol_plus.winfo_ismapped(): #self.attributes_tol_button.cget('text') == 'Remove attribute tolerances':
                    plus_var = tk.StringVar(self.attribute_frame)
                    self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                    self.attribute_tol_labels[-1].grid(row=length+5, column=4)

                    minus_var = tk.StringVar(self.attribute_frame)
                    self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                    self.attribute_tol_labels[-1].grid(row=length+5, column=5)
                    self.new_object_dict["attributes"][-1][4] = [plus_var, minus_var] # append tolerance variables to last entry of object dict
                    if tol:
                        self.attribute_tol_labels[-2].insert(0, tol[0])
                        self.attribute_tol_labels[-1].insert(0, tol[1])
                else:
                    if tol: # if imported data has tolerances, add tolerance entry boxes to every already existing attribute
                        self.attributes_tol_button.config(image=self.hide_img)
                        Tooltip(self.attributes_tol_button, "Remove attribute tolerances")
                        self.attribute_tol_plus.grid(row=3, column=4)
                        self.attribute_tol_minus.grid(row=3, column=5)
                        for i in range(len(self.new_object_dict["attributes"])):
                            plus_var = tk.StringVar(self.attribute_frame)
                            self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                            self.attribute_tol_labels[-1].grid(row=i+5, column=4)

                            minus_var = tk.StringVar(self.attribute_frame)
                            self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                            self.attribute_tol_labels[-1].grid(row=i+5, column=5)
                            self.new_object_dict["attributes"][i][4] = [plus_var, minus_var]
                        self.attribute_tol_labels[-2].insert(0, tol[0])
                        self.attribute_tol_labels[-1].insert(0, tol[1])

            for inp in import_data["inputs"]:
                if not self.new_object_dict["inputs"]:
                    self.input_name_label.grid(row=3, column=0)
                    self.input_shortcut_label.grid(row=3, column=1)
                    self.input_value_label.grid(row=3, column=2)
                    self.input_unit_label.grid(row=3, column=3)
                name, shortcut, value, unit = inp
                length = len(self.new_object_dict["inputs"])
                self.input_labels.append(tk.Label(self.input_frame, text=name, bg='white'))
                self.input_labels[-1].grid(row=length+4, column=0)

                shortcut_var = tk.StringVar(self.master) 
                self.input_labels.append(tk.Entry(self.input_frame, textvariable=shortcut_var))
                self.input_labels[-1].grid(row=length+4, column=1)
                self.input_labels[-1].insert(0, shortcut)

                value_var = tk.StringVar(self.master) 
                self.input_labels.append(tk.Entry(self.input_frame, textvariable=value_var))
                self.input_labels[-1].grid(row=length+4, column=2)
                self.input_labels[-1].insert(0, value)

                unit_var = tk.StringVar(self.master) 
                self.input_labels.append(tk.Entry(self.input_frame, textvariable=unit_var))
                self.input_labels[-1].grid(row=length+4, column=3)
                self.input_labels[-1].insert(0, unit)
                
                self.new_object_dict["inputs"].append([name, shortcut_var, value_var, unit_var])

            for ou in import_data["outputs"]:
                if not self.new_object_dict["outputs"]:
                    self.output_name_label.grid(row=3, column=0)
                    self.output_shortcut_label.grid(row=3, column=1)
                    self.output_value_label.grid(row=3, column=2)
                    self.output_unit_label.grid(row=3, column=3)
                name, shortcut, value, unit = ou
                length = len(self.new_object_dict["outputs"])
                self.output_labels.append(tk.Label(self.output_frame, text=name, bg='white'))
                self.output_labels[-1].grid(row=length+4, column=0)

                shortcut_var = tk.StringVar(self.master) 
                self.output_labels.append(tk.Entry(self.output_frame, textvariable=shortcut_var))
                self.output_labels[-1].grid(row=length+4, column=1)
                self.output_labels[-1].insert(0, shortcut)

                value_var = tk.StringVar(self.output_frame)
                self.output_labels.append(tk.Entry(self.output_frame, textvariable=value_var))
                self.output_labels[-1].grid(row=length+4, column=2)
                self.output_labels[-1].insert(0, value)
                
                unit_var = tk.StringVar(self.output_frame)
                self.output_labels.append(tk.Entry(self.output_frame, textvariable=unit_var))
                self.output_labels[-1].grid(row=length+4, column=3)
                self.output_labels[-1].insert(0, unit)
                
                self.new_object_dict["outputs"].append([name, shortcut_var, value_var, unit_var])

            for fi in import_data["files"]:
                length = len(self.new_object_dict["files"])
                # self.choose_file_buttons.append(tk.Button(self.file_frame, image=self.open_file_img, bg='white', command=self.choose_file))
                self.choose_file_buttons.append(ttk.Button(self.file_frame, image=self.open_file_img, command=self.choose_file, bootstyle='light'))
                self.choose_file_buttons[-1].grid(row=length+3, column=0)
                Tooltip(self.choose_file_buttons[-1], "Choose file")

                name = fi
                self.file_labels.append(tk.Label(self.file_frame, text=name, bg='white'))
                self.file_labels[-1].grid(row=length+3, column=1)
                self.new_object_dict["files"].append(name)

            for value in import_data["references"]:
                if value != self.object_name:
                    length = len(self.new_object_dict["references"])
                    options = list(self.object_names.keys())
                    #options.remove(self.object_name)
                    value_var = tk.StringVar(self.reference_frame, value)
                    self.reference_labels.append(ttk.Combobox(self.reference_frame, state="readonly", values=options, textvariable=value_var))
                    ind = options.index(value)
                    self.reference_labels[-1].current(ind)
                    self.reference_labels[-1].grid(row = len(self.reference_labels)+3, column = 0)
                    
                    self.new_object_dict["references"].append(value_var)

    # Objective functions:
    def add_objective(self):
        objective = simpledialog.askstring("Add objective", "Enter the objective:")
        if objective:
            l = len(self.new_object_dict["objectives"])
            state_var = tk.IntVar(self.objective_frame)
            # self.objective_checkbuttons.append(tk.Checkbutton(self.objective_frame, text = objective, variable=state_var, bg='white'))
            self.objective_checkbuttons.append(ttk.Checkbutton(self.objective_frame, text = objective, variable=state_var))
            self.objective_checkbuttons[-1].grid(row=l+3, column=0)

            self.new_object_dict["objectives"].append([objective, state_var])
            
    def delete_objective(self):
        if self.objective_checkbuttons:
            self.new_object_dict["objectives"].pop()
            self.objective_checkbuttons.pop().destroy()
            
    # Attribute functions:
    def add_attribute(self):
        attribute = simpledialog.askstring("Add attribute", "Enter the attribute:")
        if attribute:
            length = len(self.new_object_dict["attributes"])
            if self.new_object_dict["attributes"] == []:
                self.attribute_name_label.grid(row=4, column=0)
                self.attribute_shortcut_label.grid(row=4, column=1)
                self.attribute_value_label.grid(row=4, column=2)
                self.attribute_unit_label.grid(row=4, column=3)
            self.attribute_labels.append(tk.Label(self.attribute_frame, text=attribute, bg='white'))
            self.attribute_labels[-1].grid(row=length+5, column=0)

            shortcut_var = tk.StringVar(self.master)
            self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=shortcut_var))
            self.attribute_labels[-1].grid(row=length+5, column=1)

            value_var = tk.StringVar(self.master)
            self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=value_var))
            self.attribute_labels[-1].grid(row=length+5, column=2)

            unit_var = tk.StringVar(self.master)
            self.attribute_labels.append(tk.Entry(self.attribute_frame, textvariable=unit_var))
            self.attribute_labels[-1].grid(row=length+5, column=3)

            if self.attribute_tol_plus.winfo_ismapped():
                if self.new_object_dict["attributes"] == []:
                    self.attribute_tol_plus.grid(row=4, column=4)
                    self.attribute_tol_minus.grid(row=4, column=5)
                plus_var = tk.StringVar(self.attribute_frame)
                self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                self.attribute_tol_labels[-1].grid(row=length+5, column=4)

                minus_var = tk.StringVar(self.attribute_frame)
                self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                self.attribute_tol_labels[-1].grid(row=length+5, column=5)
                self.new_object_dict["attributes"].append([attribute, shortcut_var, value_var, unit_var, [plus_var, minus_var]])
            else:
                self.new_object_dict["attributes"].append([attribute, shortcut_var, value_var, unit_var, []])

    def delete_attribute(self):
        if self.attribute_labels:
            self.new_object_dict["attributes"].pop()
            for i in range(4):
                self.attribute_labels.pop().destroy()
            if self.attribute_tol_plus.winfo_ismapped():
                self.attribute_tol_labels.pop().destroy()
                self.attribute_tol_labels.pop().destroy()
            
            # remove Name, Symbol, Value, Unit, +, - if all attributes are removed
            if self.new_object_dict["attributes"] == []:
                self.attribute_name_label.grid_forget()
                self.attribute_shortcut_label.grid_forget()
                self.attribute_value_label.grid_forget()
                self.attribute_unit_label.grid_forget()
                if self.attribute_tol_plus: # forget tolerance labels
                    self.attribute_tol_plus.grid_forget()
                    self.attribute_tol_minus.grid_forget()

    # Input functions:
    def add_input(self):
        input_ = simpledialog.askstring("Add input", "Enter the input:")
        if input_:
            length = len(self.new_object_dict["inputs"])
            if self.new_object_dict["inputs"] == []: # create table structure if there aren't any entries already
                self.input_name_label.grid(row=3, column=0)
                self.input_shortcut_label.grid(row=3, column=1)
                self.input_value_label.grid(row=3, column=2)
                self.input_unit_label.grid(row=3, column=3)
            self.input_labels.append(tk.Label(self.input_frame, text=input_, bg='white')) # label
            self.input_labels[-1].grid(row=length+4, column=0)

            shortcut_var = tk.StringVar(self.master) # shortcut
            self.input_labels.append(tk.Entry(self.input_frame, textvariable=shortcut_var))
            self.input_labels[-1].grid(row=length+4, column=1)

            value_var = tk.StringVar(self.master) # value
            self.input_labels.append(tk.Entry(self.input_frame, textvariable=value_var))
            self.input_labels[-1].grid(row=length+4, column=2)

            unit_var = tk.StringVar(self.master) # value
            self.input_labels.append(tk.Entry(self.input_frame, textvariable=unit_var))
            self.input_labels[-1].grid(row=length+4, column=3)

            self.new_object_dict["inputs"].append([input_, shortcut_var, value_var, unit_var])

    def delete_input(self):
        if self.input_labels:
            self.new_object_dict["inputs"].pop()
            for i in range(4):
                self.input_labels.pop(-1).destroy()
            if self.new_object_dict["inputs"] == []:
                self.input_name_label.grid_forget()
                self.input_shortcut_label.grid_forget()
                self.input_value_label.grid_forget()
                self.input_unit_label.grid_forget()
            
    # Output functions:
    def add_output(self):
        output = simpledialog.askstring("Add output", "Enter the output:")
        if output:
            length = len(self.new_object_dict["outputs"])
            if self.new_object_dict["outputs"] == []:
                self.output_name_label.grid(row=3, column=0)
                self.output_shortcut_label.grid(row=3, column=1)
                self.output_value_label.grid(row=3, column=2)
                self.output_unit_label.grid(row=3, column=3)
            self.output_labels.append(tk.Label(self.output_frame, text=output, bg='white'))
            self.output_labels[-1].grid(row=length+4, column=0)

            shortcut_var = tk.StringVar(self.master)
            self.output_labels.append(tk.Entry(self.output_frame, textvariable=shortcut_var))
            self.output_labels[-1].grid(row=length+4, column=1)

            value_var = tk.StringVar(self.output_frame) 
            self.output_labels.append(tk.Entry(self.output_frame, textvariable=value_var))
            self.output_labels[-1].grid(row=length+4, column=2)

            unit_var = tk.StringVar(self.output_frame) 
            self.output_labels.append(tk.Entry(self.output_frame, textvariable=unit_var))
            self.output_labels[-1].grid(row=length+4, column=3)

            self.new_object_dict["outputs"].append([output, shortcut_var, value_var, unit_var])

    def delete_output(self):
        if self.output_labels:
            self.new_object_dict["outputs"].pop()
            for i in range(4):
                self.output_labels.pop(-1).destroy()
            if self.new_object_dict["outputs"] == []:
                self.output_name_label.grid_forget()
                self.output_shortcut_label.grid_forget()
                self.output_value_label.grid_forget()
                self.output_unit_label.grid_forget()

    # File functions:
    def add_file(self):
        file = simpledialog.askstring("Add file", "Enter the file:")
        if file:
            length = len(self.new_object_dict["files"])
            # self.choose_file_buttons.append(tk.Button(self.file_frame, image=self.open_file_img, bg='white', command=self.choose_file))
            self.choose_file_buttons.append(ttk.Button(self.file_frame, image=self.open_file_img, command=self.choose_file, bootstyle='light'))
            self.choose_file_buttons[-1].grid(row=length+3, column=0)
            Tooltip(self.choose_file_buttons[-1], "Choose file")
            self.file_labels.append(tk.Label(self.file_frame, text=file, bg='white'))
            self.file_labels[-1].grid(row=length+3, column=1)

            self.new_object_dict["files"].append(file)
    
    def choose_file(self):
        # check if there is already a file assigned to current file property and remove if so:
        file_list = os.listdir(os.path.join(self.directory, 'current', self.object_name)) # get list of files in object's directory
        file_list_without_filetypes = [file.rsplit(".", 1)[0] for file in file_list] # remove endings
        for i, file in enumerate(file_list_without_filetypes):
            if file == self.new_object_dict["files"][-1]:
                os.remove(os.path.join(self.directory, 'current', self.object_name, file_list[i]))
                self.open_file_buttons.pop(i).destroy()
                break

        # rename & copy new file into object's directory:
        file = filedialog.askopenfile()
        if file:
            source_file = file.name
            filetype = "."+source_file.rsplit(".", 1)[-1]
            new_file_name = self.new_object_dict["files"][-1]+filetype
            destination = os.path.join(self.directory, 'current', self.object_name, new_file_name)
            shutil.copy(source_file, destination)
            length = len(self.new_object_dict["files"])
            # self.open_file_buttons.append(tk.Button(self.file_frame, text=new_file_name, command=lambda: self.open_file(destination), bg='white'))
            self.open_file_buttons.append(ttk.Button(self.file_frame, text=new_file_name, command=lambda: self.open_file(destination), bootstyle='light'))
            self.open_file_buttons[-1].grid(row=length+2, column=2)
    
    def open_file(self, filepath):
        os.startfile(filepath)

    def delete_file(self):
        if self.file_labels:
            self.choose_file_buttons.pop(-1).destroy()
            self.file_labels.pop(-1).destroy() # pop() returns label to be deleted, destroy() destroys the label
            self.open_file_buttons.pop(-1).destroy()
            file_list = os.listdir(os.path.join(self.directory, 'current', self.object_name)) # get list of files in obejct's directory
            file_list_without_filetypes = [file.rsplit(".", 1)[0] for file in file_list] # remove endings
            for i, file in enumerate(file_list_without_filetypes):
                if file == self.new_object_dict["files"][-1]:
                    os.remove(os.path.join(self.directory, 'current', self.object_name, file_list[i]))
            self.new_object_dict["files"].pop()
    
    def add_reference(self):
        value_var = tk.StringVar(self.reference_frame)
        options = list(self.object_names.keys())
        current_refs = [ref.get() for ref in self.new_object_dict["references"]] # current references: get strings from tk.strings
        options = [ref for ref in options if ref not in current_refs] # only display objects that are not already referenced
        if options:
            self.reference_labels.append(ttk.Combobox(self.reference_frame, state="readonly", values=options, textvariable=value_var))
            self.reference_labels[-1].grid(row = len(self.reference_labels)+3, column = 0)
            self.new_object_dict["references"].append(value_var)
        else:
            messagebox.showinfo("No referenceable objects", "Currently, there are no refereceable objects.")

    def delete_reference(self):
        self.reference_labels.pop().destroy()
        self.new_object_dict["references"].pop()         

    def attribute_tol(self):
        # add tolerance entry boxes to every attribute:
        if not self.attribute_tol_plus.winfo_ismapped():
            if not self.new_object_dict["attributes"]:
                messagebox.showinfo("No attributes", "Add at least one attribute before addings tolerances")
            else:
                self.attributes_tol_button.config(image=self.hide_img)
                Tooltip(self.attributes_tol_button, "Remove attribute tolerances")
                self.attribute_tol_plus.grid(row=4, column=4)
                self.attribute_tol_minus.grid(row=4, column=5)
                if self.new_object_dict["attributes"]:
                    for i in range(len(self.new_object_dict["attributes"])):
                        plus_var = tk.StringVar(self.attribute_frame)
                        self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=plus_var))
                        self.attribute_tol_labels[-1].grid(row=i+5, column=4)

                        minus_var = tk.StringVar(self.attribute_frame)
                        self.attribute_tol_labels.append(tk.Entry(self.attribute_frame, textvariable=minus_var))
                        self.attribute_tol_labels[-1].grid(row=i+5, column=5)
                        self.new_object_dict["attributes"][i][4] = [plus_var, minus_var]
        # remove tolerances from every attribute:
        else:
            self.attributes_tol_button.config(image=self.show_img)
            Tooltip(self.attributes_tol_button, "Add attribute tolerances")
            self.attribute_tol_plus.grid_forget()
            self.attribute_tol_minus.grid_forget()
            if self.new_object_dict["attributes"]:
                l = len(self.new_object_dict["attributes"])
                for i in range(l):
                    self.attribute_tol_labels.pop().destroy()
                    self.attribute_tol_labels.pop().destroy()
                    self.new_object_dict["attributes"][i][4] = []