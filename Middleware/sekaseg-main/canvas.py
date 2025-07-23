'''
This file is a function to save the created object to the main tool window 
and achieve required functions like showing the object informations and moveable bbox
'''

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, font, simpledialog, messagebox
import os, sys
import json
from PIL import ImageTk, Image
import shutil
from tooltips import Tooltip

from change_object import ChangeObject
import DropDown
from export2 import data2csv, data2csv_for_simulink, data2pdf, data2txt
#from export2csv_for_simulink import data2csv_for_simulink
from vertical_scrolled_frame import VerticalScrolledFrame
from navigate_versions import save_version

class CanvasObject:
    def __init__(self, canvas, scrollregion, tree, positions, directory, object_names, object_name, object_dict, back_button):
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family = "Helvetica", size = 10)
        self.gnome_desktops = ['X-Cinnamon', 'XFCE']

        self.canvas = canvas
        self.scrollregion = scrollregion
        self.tree = tree
        self.positions = positions
        self.directory = directory
        self.object_names = object_names
        self.object_name = object_name
        self.object_dict = object_dict
        self.back_button = back_button
        
        self.objective_checkbuttons = []
        self.attribute_labels = []
        self.attribute_tol_labels = []
        self.input_labels = []
        self.output_labels = []
        self.file_labels = []
        self.open_file_buttons  = []
        self.copy_file_buttons = []
        self.reference_labels = []
        self.subscriber_labels = []

        self.frames = []
        self.tooltips = []

        # for creating exe file via pyinstaller: images have to be added separately (command line) & current path has to be set
        application_path = str()
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)

        # Images:
        self.change_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Pencil-outline.32.png")))
        self.export2_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Exit-outline.32.png")))
        self.delete_image = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Trash.32.png")))
        self.subscribe_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Github-Octicons-Bell-24.32.png")))
        self.unsubscribe_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Github-Octicons-Bell-slash-24.32.png")))
        self.show_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Eye-outline.32.png")))
        self.hide_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Ionic-Ionicons-Eye-off.32.png")))
        self.copy_img = ImageTk.PhotoImage(Image.open(os.path.join(application_path, "Amitjakhu-Drip-Copy.32.png")))

        # create a bbox for object:
        self.x = self.object_dict["position"][0]
        self.y = self.object_dict["position"][1]

        self.create_basic_frame()
        self.create_properties_frame()
        self.create_label_value()
        self.create_show_hide_buttons()

    def create_basic_frame(self):
        ##################################################
        # create basic frame for object
        ##################################################
        self.object_frame = tk.Frame(self.canvas, bd=1, relief='solid', bg = 'white')
        self.object_frame.place(x=self.x, y=self.y)
        # link window to frame so that frame moves with scrollbar:
        self.canvas.create_window(self.x, self.y, window=self.object_frame, anchor='n')

        self.object_name_label = tk.Label(self.object_frame, text=self.object_name, font = ("Helvetica", 14, "bold"), bg = 'white')
        self.object_name_label.grid(row=0, column=0, columnspan=4)

        self.object_folder = tk.Label(self.object_frame, text='Folder: '+self.object_dict["folder"], font = ("Helvetica", 10), bg = 'white')
        self.object_folder.grid(row=1, column=0, columnspan=4)

        self.change_button = ttk.Button(self.object_frame, image=self.change_img, command=self.change_object, bootstyle = 'light')
        self.change_button.grid(row=3, column=0)
        Tooltip(self.change_button, 'Change object')

        self.export2_button = ttk.Button(self.object_frame, image=self.export2_img, command=self.export, bootstyle = 'light')
        self.export2_button.grid(row=3, column=1)
        Tooltip(self.export2_button, 'Export object to ...')

        self.subscribe_button = ttk.Button(self.object_frame, image=self.subscribe_img, command=self.subscribe, bootstyle = 'light')
        self.subscribe_button.grid(row=3, column=2)
        Tooltip(self.subscribe_button, 'Subscribe')
        self.unsubscribe_buttons = []

        self.delete_button = ttk.Button(self.object_frame, image= self.delete_image, command=self.delete_object, bootstyle = 'light')
        self.delete_button.grid(row=3, column=3)
        Tooltip(self.delete_button, 'Delete Object')

        c = 0 # count un-checked objectives, to track row number
        open_objectives = False
        if self.object_dict["objectives"]:
            for objective, o_state in self.object_dict['objectives']:
                if o_state == 0:
                    open_objectives = True
                    break
        if open_objectives:
            label = tk.Label(self.object_frame, text = "Open objectives", font=('Helvetica', 10, 'bold'), bg = 'white', fg = "#e37222")
            label.grid(row=4+c, columnspan=4)
            c+=1
            for objective, o_state in self.object_dict['objectives']:
                if o_state == 0:
                    # Label widget
                    """ checkbutton = tk.Label(self.object_frame, text = f'- {objective}', font=('Helvetica', 10, 'bold'),
                                           bg = 'white', fg = "#e37222") """
                    checkbutton = ttk.Label(self.object_frame, text = f'- {objective}', bootstyle = "danger")
                    checkbutton.grid(row=4+c, column=0, columnspan=4)
                    c+=1

        # create property frame
        self.properties_frame = tk.Frame(self.object_frame, bg = 'white')
        self.properties_frame.grid(row = 5+c, column=0, columnspan=4)
        self.frames.append(self.properties_frame)

        # show/hide properties
        self.properties_button = ttk.Button(self.properties_frame, image = self.show_img, command=self.show_properties, bootstyle = ('light', 'outline'))
        self.properties_button.pack(side="top", padx=3, pady=3)
        Tooltip(self.properties_button, 'Show object properties')

        # property details frame
        self.property_details_frame = tk.Frame(self.properties_frame, bg = 'white')
        self.frames.append(self.property_details_frame)
        self.property_details_frame.pack()
        self.property_details_frame.pack_forget()

    def create_properties_frame(self):
        # objectives frame
        if self.object_dict["objectives"]:
            self.objectives_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.objectives_frame.pack(expand=False)
            self.frames.append(self.objectives_frame)

            self.objectives_frame_label = tk.Label(self.objectives_frame, text="Objectives", font=("Helvetica", 12), bg = 'white')
            self.objectives_frame_label.pack()

            self.objective_details_frame = tk.Frame(self.objectives_frame, bg = 'white')
            self.objective_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # attributes frame
        if self.object_dict["attributes"]:
            self.attributes_frame = tk.Frame(self.property_details_frame, bg = 'white')

            self.attributes_frame.pack(expand=False)
            self.attributes_frame_label = tk.Label(self.attributes_frame, text="Attributes", font=("Helvetica", 12), bg = 'white')

            self.attributes_frame_label.pack()
            self.frames.append(self.attributes_frame)

            self.attribute_details_frame = tk.Frame(self.attributes_frame, bg = 'white')
            self.attribute_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # input frame
        if self.object_dict["inputs"]:
            self.inputs_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.inputs_frame.pack(expand=False)
            self.inputs_frame_label = tk.Label(self.inputs_frame, text="Inputs", font=("Helvetica", 12), bg = 'white')

            self.inputs_frame_label.pack()
            self.frames.append(self.inputs_frame)

            self.input_details_frame = tk.Frame(self.inputs_frame, bg = 'white')
            self.input_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # output frame
        if self.object_dict["outputs"]:
            self.outputs_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.outputs_frame.pack(expand=False)

            self.outputs_frame_label = tk.Label(self.outputs_frame, text="Outputs", font=("Helvetica", 12), bg = 'white')
            self.outputs_frame_label.pack()
            self.frames.append(self.outputs_frame)

            self.output_details_frame = tk.Frame(self.outputs_frame, bg = 'white')
            self.output_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # file frame
        if self.object_dict["files"]:          
            self.files_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.files_frame.pack(expand=False)

            self.files_frame_label = tk.Label(self.files_frame, text="Files", font=("Helvetica", 12), bg = 'white')
            self.files_frame_label.pack()
            self.frames.append(self.files_frame)

            self.file_details_frame = tk.Frame(self.files_frame, bg = 'white')
            self.file_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # reference frame
        if self.object_dict["references"]:
            self.reference_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.reference_frame.pack(expand=False)

            self.reference_frame_label = tk.Label(self.reference_frame, text="References", font=("Helvetica", 12), bg = 'white')
            self.reference_frame_label.pack()
            self.frames.append(self.reference_frame)

            self.reference_details_frame = tk.Frame(self.reference_frame, bg = 'white')
            self.reference_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

        # create subscriber frame
        if self.object_dict["subscribers"]:
            self.subscribers_frame = tk.Frame(self.property_details_frame, bg = 'white')
            self.subscribers_frame.pack(expand=False)

            self.subscribers_frame_label = tk.Label(self.subscribers_frame, text="Subscribers", font=("Helvetica", 12), bg = 'white')
            self.subscribers_frame_label.pack()
            self.frames.append(self.subscribers_frame)

            self.subscriber_details_frame = tk.Frame(self.subscribers_frame, bg = 'white')
            self.subscriber_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)

    def create_label_value(self):
        ##################################################
        # create labels and values
        ##################################################
        # Use a loop to create the labels and values for objectives
        # Use a loop to display objectives
        if self.object_dict['objectives']:
            for objective, o_state in self.object_dict['objectives']:
                # Label widget
                self.objective_checkbuttons.append(tk.Checkbutton(self.objective_details_frame, text = objective, state = 'disabled', bg = 'white')) #variable=o_state, 

                # Checkbutton with state
                if o_state == 1:
                    self.objective_checkbuttons[-1].select()
                else:
                    self.objective_checkbuttons[-1].deselect()
                self.objective_checkbuttons[-1].pack()

            self.objective_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.objectives_frame) + 1, self.objective_details_frame)

        # Use a loop to create the labels and values for attribute
        if self.object_dict['attributes']:
            # Table layout
            self.attribute_name_label = tk.Label(self.attribute_details_frame, text='Name', bg = 'white')
            self.attribute_name_label.grid(row=0, column=0)
            self.attribute_shortcut_label = tk.Label(self.attribute_details_frame, text='Symbol', bg = 'white')
            self.attribute_shortcut_label.grid(row=0, column=1)
            self.attribute_value_label = tk.Label(self.attribute_details_frame, text='Value', bg = 'white')
            self.attribute_value_label.grid(row=0, column=2)
            self.attribute_unit_label = tk.Label(self.attribute_details_frame, text='Unit', bg = 'white')
            self.attribute_unit_label.grid(row=0, column=3)
            if self.object_dict['attributes'][0][4] != []: # if the first attribute tuple has tols, add tolerance column
                self.attribute_plus_label = tk.Label(self.attribute_details_frame, text='+', bg = 'white')
                self.attribute_plus_label.grid(row=0, column=4)
                self.attribute_minus_label = tk.Label(self.attribute_details_frame, text='-', bg = 'white')
                self.attribute_minus_label.grid(row=0, column=5)
            for i, (label, shortcut, value, unit, tol) in enumerate(self.object_dict['attributes']):
                # Label widget
                self.attribute_labels.append(tk.Label(self.attribute_details_frame, text=label, bg = 'white'))
                self.attribute_labels[-1].grid(row=i+1, column=0)

                # Shortcut widget
                self.attribute_labels.append(tk.Entry(self.attribute_details_frame))
                self.attribute_labels[-1].insert(0, shortcut)
                self.attribute_labels[-1].config(state = 'disabled')
                self.attribute_labels[-1].grid(row=i+1, column=1)

                # Value widget
                self.attribute_labels.append(tk.Entry(self.attribute_details_frame))
                self.attribute_labels[-1].insert(0, value)
                self.attribute_labels[-1].config(state = 'disabled')
                self.attribute_labels[-1].grid(row=i+1, column=2)

                # Unit widget
                self.attribute_labels.append(tk.Entry(self.attribute_details_frame))
                self.attribute_labels[-1].insert(0, unit)
                self.attribute_labels[-1].config(state = 'disabled')
                self.attribute_labels[-1].grid(row=i+1, column=3)

                # Tolerance widget
                if tol != []:
                    self.attribute_tol_labels.append(tk.Entry(self.attribute_details_frame))
                    self.attribute_tol_labels[-1].insert(0, tol[0])
                    self.attribute_tol_labels[-1].config(state = 'disabled')
                    self.attribute_tol_labels[-1].grid(row=i+1, column=4)
                    self.attribute_tol_labels.append(tk.Entry(self.attribute_details_frame))
                    self.attribute_tol_labels[-1].insert(0, tol[1])
                    self.attribute_tol_labels[-1].config(state = 'disabled')
                    self.attribute_tol_labels[-1].grid(row=i+1, column=5)
                
            self.attribute_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.attributes_frame) + 1, self.attribute_details_frame)

        # Use a loop to create the labels and values for inputs
        if self.object_dict['inputs']:
            self.input_name_label = tk.Label(self.input_details_frame, text='Name', bg = 'white')
            self.input_name_label.grid(row=0, column=0)
            self.input_shortcut_label = tk.Label(self.input_details_frame, text='Symbol', bg = 'white')
            self.input_shortcut_label.grid(row=0, column=1)
            self.input_value_label = tk.Label(self.input_details_frame, text='Value', bg = 'white')
            self.input_value_label.grid(row=0, column=2)
            self.input_unit_label = tk.Label(self.input_details_frame, text='Unit', bg = 'white')
            self.input_unit_label.grid(row=0, column=3)
            for i, (label, shortcut, value, unit) in enumerate(self.object_dict['inputs']):
                # Label widget
                self.input_labels.append(tk.Label(self.input_details_frame, text=label, bg = 'white'))
                self.input_labels[-1].grid(row=i+1, column=0)

                # Shortcut widget
                self.input_labels.append(tk.Entry(self.input_details_frame))
                self.input_labels[-1].insert(0, shortcut)
                self.input_labels[-1].config(state = 'disabled')
                self.input_labels[-1].grid(row=i+1, column=1)

                # Value widget
                self.input_labels.append(tk.Entry(self.input_details_frame))
                self.input_labels[-1].insert(0, value)
                self.input_labels[-1].config(state = 'disabled')
                self.input_labels[-1].grid(row=i+1, column=2)

                # Unit widget
                self.input_labels.append(tk.Entry(self.input_details_frame))
                self.input_labels[-1].insert(0, unit)
                self.input_labels[-1].config(state = 'disabled')
                self.input_labels[-1].grid(row=i+1, column=3)

            self.input_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.inputs_frame) + 1, self.input_details_frame)

        # Use a loop to create the labels and values for outputs
        if self.object_dict['outputs']:
            self.output_name_label = tk.Label(self.output_details_frame, text='Name', bg = 'white')
            self.output_name_label.grid(row=0, column=0)
            self.output_shortcut_label = tk.Label(self.output_details_frame, text='Symbol', bg = 'white')
            self.output_shortcut_label.grid(row=0, column=1)
            self.output_value_label = tk.Label(self.output_details_frame, text='Value', bg = 'white')
            self.output_value_label.grid(row=0, column=2)
            self.output_unit_label = tk.Label(self.output_details_frame, text='Unit', bg = 'white')
            self.output_unit_label.grid(row=0, column=3)
            for i, (label, shortcut, value, unit) in enumerate(self.object_dict['outputs']):
                # Label widget
                self.output_labels.append(tk.Label(self.output_details_frame, text=label, bg = 'white'))
                self.output_labels[-1].grid(row=i+1, column=0)

                # Shortcut widget
                self.output_labels.append(tk.Entry(self.output_details_frame))
                self.output_labels[-1].insert(0, shortcut)
                self.output_labels[-1].config(state = 'disabled')
                self.output_labels[-1].grid(row=i+1, column=1)

                # Value widget
                self.output_labels.append(tk.Entry(self.output_details_frame))
                self.output_labels[-1].insert(0, value)
                self.output_labels[-1].config(state = 'disabled')
                self.output_labels[-1].grid(row=i+1, column=2)

                # Unit widget
                self.output_labels.append(tk.Entry(self.output_details_frame))
                self.output_labels[-1].insert(0, unit)
                self.output_labels[-1].config(state = 'disabled')
                self.output_labels[-1].grid(row=i+1, column=3)

            self.output_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.outputs_frame) + 1, self.output_details_frame)
        
        # Use a loop to display the files
        if self.object_dict['files']:
            for i, label in enumerate(self.object_dict['files']):
                file_list = os.listdir(os.path.join(self.directory, 'current', self.object_name)) # get list of files in object's directory
                file_list_without_filetypes = [file.rsplit(".", 1)[0] for file in file_list] # remove endings
                for j, file in enumerate(file_list_without_filetypes):
                    if file == label:
                        # Copy file button
                        # self.copy_file_buttons.append(tk.Button(self.file_details_frame, image=self.copy_img, bg='white', command=lambda: self.copy_file(path)))
                        self.copy_file_buttons.append(ttk.Button(self.file_details_frame, image=self.copy_img, bootstyle=('light'), command=lambda: self.copy_file(path)))
                        self.copy_file_buttons[-1].grid(row=i, column=0)
                        Tooltip(self.copy_file_buttons[-1], 'Copy file')

                        # Label widget
                        self.file_labels.append(tk.Label(self.file_details_frame, text=label, bg = 'white'))
                        self.file_labels[-1].grid(row=i, column=1)

                        # Open file button
                        path = os.path.join(self.directory, 'current', self.object_name, file_list[j])
                        # self.open_file_buttons.append(tk.Button(self.file_details_frame, text=file_list[j], command=lambda: self.open_file(path), bg='white'))
                        self.open_file_buttons.append(ttk.Button(self.file_details_frame, text=file_list[j], command=lambda: self.open_file(path), bootstyle = 'light'))
                        self.open_file_buttons[-1].grid(row=i, column=2)
                        Tooltip(self.open_file_buttons[-1], 'Open file')
                        break
                
            self.file_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.files_frame) + 1, self.file_details_frame)

        if self.object_dict["references"]:
            for i, value in enumerate(self.object_dict["references"]):
                self.reference_labels.append(tk.Entry(self.reference_details_frame))
                self.reference_labels[-1].insert(0, value)
                self.reference_labels[-1].config(state = 'disabled')
                self.reference_labels[-1].grid(row=i, column=0)

            self.reference_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.reference_frame) + 1, self.reference_details_frame)

        # Use a loop to create the labels and values for subscribers
        if self.object_dict['subscribers']:
            for i, email in enumerate(self.object_dict['subscribers']):
                # Unsubscribe button:
                # self.unsubscribe_buttons.append(tk.Button(self.subscriber_details_frame, image=self.unsubscribe_img, bg='white'))
                self.unsubscribe_buttons.append(ttk.Button(self.subscriber_details_frame, image=self.unsubscribe_img, bootstyle = 'light'))
                self.unsubscribe_buttons[-1].grid(row=i, column=0)
                self.unsubscribe_buttons[-1].configure(command=lambda: self.unsubscribe(email))
                Tooltip(self.unsubscribe_buttons[-1], 'Unsubscribe')

                # Create a value widget
                self.subscriber_labels.append(tk.Label(self.subscriber_details_frame, text=email, bg = 'white'))
                self.subscriber_labels[-1].grid(row=i, column=1)

            self.subscriber_details_frame.pack_forget()
            self.frames.insert(self.frames.index(self.subscribers_frame) + 1, self.subscriber_details_frame)
    
    # https://stackoverflow.com/questions/75259338/how-to-copy-a-file-to-clipboard-in-python
    def copy_file(self, filepath):
        command = f"powershell Set-Clipboard -LiteralPath {filepath}"
        os.system(command)

    def open_file(self, filepath):
        os.startfile(filepath)

    def create_show_hide_buttons(self):
        ##################################################
        # create show/hide buttons
        ##################################################
        # objectives
        if self.object_dict["objectives"]:
            # self.objective_button = tk.Button(self.objectives_frame, text=" Objectives", image = self.show_img, compound = "left", command=self.show_objective_details, bg = 'white')
            self.objective_button = ttk.Button(self.objectives_frame, image = self.show_img, compound = "left", command=self.show_objective_details, bootstyle = ('light'))
            self.objective_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.objective_button, 'Show objective details')
        
        # attributes
        if self.object_dict["attributes"]:
            # self.attribute_button = tk.Button(self.attributes_frame, text=" Attributes", image=self.show_img, compound="left", command=self.show_attribute_details, bg = 'white')
            self.attribute_button = ttk.Button(self.attributes_frame, image=self.show_img, compound="left", command=self.show_attribute_details, bootstyle = ('light'))
            self.attribute_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.attribute_button, 'Show attribute details')

        # inputs
        if self.object_dict["inputs"]:
            # self.input_button = tk.Button(self.inputs_frame, text=" Inputs", image=self.show_img, compound="left", command=self.show_input_details, bg = 'white')
            self.input_button = ttk.Button(self.inputs_frame, image=self.show_img, compound="left", command=self.show_input_details, bootstyle = ('light'))
            self.input_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.input_button, 'Show input details')

        # outputs
        if self.object_dict["outputs"]:
            # self.output_button = tk.Button(self.outputs_frame, text=" Outputs", image=self.show_img, compound="left", command=self.show_output_details, bg = 'white')
            self.output_button = ttk.Button(self.outputs_frame, image=self.show_img, compound="left", command=self.show_output_details, bootstyle = ('light'))
            self.output_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.output_button, 'Show output details')

        # files
        if self.object_dict["files"]:
            # self.file_button = tk.Button(self.files_frame, text=" Files", image=self.show_img, compound="left", command=self.show_file_details, bg = 'white')
            self.file_button = ttk.Button(self.files_frame, image=self.show_img, compound="left", command=self.show_file_details, bootstyle = ('light'))
            self.file_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.file_button, 'Show file details')

        # references:
        if self.object_dict["references"]:
            # self.reference_button = tk.Button(self.reference_frame, text="References", image=self.show_img, compound="left", command=self.show_reference_details, bg = 'white')
            self.reference_button = ttk.Button(self.reference_frame, image=self.show_img, compound="left", command=self.show_reference_details, bootstyle = ('light'))
            self.reference_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.reference_button, 'Show reference details')

        # subscribers
        if self.object_dict["subscribers"]:
            # self.subscriber_button = tk.Button(self.subscribers_frame, text="Subscribers", image=self.show_img, compound="left",command=self.show_subscriber_details, bg = 'white')
            self.subscriber_button = ttk.Button(self.subscribers_frame, image=self.show_img, compound="left", command=self.show_subscriber_details, bootstyle = ('light'))
            self.subscriber_button.pack(side="top", padx=3, pady=3)
            Tooltip(self.subscriber_button, 'Show subscriber details')

        self.bind_events()

    def export(self):
        options = ['CSV', 'PDF', 'txt', 'CSV for Simulink']
        dialog = DropDown.DropdownDialog(self.object_frame, 'Choose an export option:', options)
        if dialog.result == 'CSV':
            files = [('CSV', '.csv'), ('PDF', '.pdf'), ('txt', '.txt')]
            export_directory = filedialog.asksaveasfilename(filetypes = files)
            if export_directory:
                export_directory += '.csv'
                data2csv(export_directory, self.object_name, self.object_dict)
        elif dialog.result == 'PDF':
            files = [('PDF', '.pdf'), ('CSV', '.csv'), ('txt', '.txt')]
            export_directory = filedialog.asksaveasfilename(filetypes = files)
            if export_directory:
                export_directory += '.pdf'
                data2pdf(export_directory, self.object_name, self.object_dict)
        elif dialog.result == 'txt':
            files = [('txt', '.txt'), ('CSV', '.csv'), ('PDF', '.pdf')]
            export_directory = filedialog.asksaveasfilename(filetypes = files)
            if export_directory:
                export_directory +='.txt'
                data2txt(export_directory, self.object_name, self.object_dict)
        elif dialog.result == 'CSV for Simulink':
            files = [('CSV', '.csv'), ('PDF', '.pdf'), ('txt', '.txt')]
            export_directory = filedialog.asksaveasfilename(filetypes = files)
            if export_directory:
                export_directory += '.csv'
                data2csv_for_simulink(export_directory, self.object_dict)

    def change_object(self):
        save_version(self.directory, self.back_button)
        # un-highight referenced objects:
        for ob in self.object_dict["references"]:
            if ob in self.object_names.keys():
                self.object_names[ob].object_frame.config(highlightthickness = 0)
        # change object:
        self.object_frame.destroy()
        self.object_names.pop(self.object_name)
        ChangeObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory, self.object_names, self.object_name, self.object_dict, self.back_button)

    def subscribe(self):
        save_version(self.directory, self.back_button)
        email = simpledialog.askstring("Add subscriber", "Enter e-mail address:")
        if email:
            if not self.object_dict["subscribers"]:
                self.subscribers_frame = tk.Frame(self.property_details_frame, bg = 'white')
                self.subscribers_frame.pack(expand=False)

                self.subscribers_frame_label = tk.Label(self.subscribers_frame, text="Subscribers", font=("Helvetica", 12), bg = 'white')
                self.subscribers_frame_label.pack()
                self.frames.append(self.subscribers_frame)

                self.subscriber_details_frame = tk.Frame(self.subscribers_frame, bg = 'white')
                self.subscriber_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
                self.subscriber_details_frame.pack_forget()

                self.subscriber_button = ttk.Button(self.subscribers_frame, image=self.show_img, compound="left", command=self.show_subscriber_details, bootstyle = 'light')
                self.subscriber_button.pack(side="top", padx=3, pady=3)
                Tooltip(self.subscriber_button, 'Show subscriber details')

            self.object_dict["subscribers"].append(email)
            length = len(self.subscriber_labels)

            self.subscriber_labels.append(tk.Label(self.subscriber_details_frame, text=email, bg='white'))
            self.subscriber_labels[-1].grid(row=length+1, column=1)

            self.unsubscribe_buttons.append(ttk.Button(self.subscriber_details_frame, image=self.unsubscribe_img, bootstyle = 'light'))
            self.unsubscribe_buttons[-1].grid(row=length+1, column=0)
            self.unsubscribe_buttons[-1].configure(command=lambda: self.unsubscribe(email))
            Tooltip(self.unsubscribe_buttons[-1], 'Unsubscribe')

            # update subscriber list in object file:
            file_name = f'{self.object_name}.object.txt'
            file_path = os.path.join(self.directory, 'current', self.object_name, file_name)
            new_dict = {}

            with open(file_path, 'r') as f:
                object_info = f.read()
                object_info = object_info.replace("'", "\"")
                object_info = object_info.replace("(", "[")
                object_info = object_info.replace(")", "]")
                json_dict = json.loads(object_info)
                new_dict = json_dict["new_dict"]

            object_dict = {
                "new_dict": self.object_dict,
                "old_dict": new_dict
            }

            with open(file_path, "w") as f:
                f.write(str(object_dict))

    def unsubscribe(self, email):
        save_version(self.directory, self.back_button)
        pos = self.object_dict["subscribers"].index(email)
        self.object_dict["subscribers"].pop(pos)
        self.subscriber_labels.pop(pos).destroy()
        self.unsubscribe_buttons.pop(pos).destroy()
        
        # update subscriber list in object file
        file_name = f'{self.object_name}.object.txt'
        file_path = os.path.join(self.directory, 'current', self.object_name, file_name)
        new_dict = {}
        with open(file_path, 'r') as f:
            object_info = f.read()
            object_info = object_info.replace("'", "\"")
            object_info = object_info.replace("(", "[")
            object_info = object_info.replace(")", "]")
            json_dict = json.loads(object_info)
            new_dict = json_dict["new_dict"]

        new_dict['subscribers'].pop(pos)

        object_dict = {
            "new_dict": self.object_dict,
            "old_dict": new_dict
        }

        with open(file_path, "w") as f:
            f.write(str(object_dict))
        
        if not self.object_dict["subscribers"]:
            self.subscribers_frame.destroy()

    def delete_object(self):
        save_version(self.directory, self.back_button)
        delete = messagebox.askyesno(title="Delete object", message = "Are you sure you want to delete this object?")
        if delete:
            # un-highlight referenced objects:
            for ob in self.object_dict["references"]:
                if ob in self.object_names.keys():
                    # remove current object's name from dict of referenced objects:
                    self.object_names[ob].object_frame.destroy()
                    file_name = f'{ob}.object.txt'
                    file_path = os.path.join(self.directory, 'current', ob, file_name)
                    old_dict = {}

                    with open(file_path, 'r') as f:
                        object_info = f.read()
                        object_info = object_info.replace("'", "\"")
                        object_info = object_info.replace("(", "[")
                        object_info = object_info.replace(")", "]")
                        json_dict = json.loads(object_info)
                        old_dict = json_dict["new_dict"]
                    
                    new_dict = old_dict
                    new_dict["references"].remove(self.object_name)

                    ref_dict = {
                        "new_dict": new_dict,
                        "old_dict": old_dict
                    }

                    with open(file_path, "w") as f:
                        f.write(str(ref_dict))
                    ChangeObject(self.canvas, self.scrollregion, self.tree, self.positions, self.directory,
                           self.object_names, ob, new_dict, self.back_button, directly2canvas=True)

            # delete object:
            folderpath = os.path.join(self.directory, 'current', self.object_name)
            if os.path.exists(folderpath):
                shutil.rmtree(folderpath)

            self.tree.delete(self.object_name)
            self.positions.pop(self.object_name)
            self.object_names.pop(self.object_name)
            self.object_frame.destroy()

    def show_properties(self):
        if self.property_details_frame.winfo_ismapped():
            self.property_details_frame.pack_forget()
            self.properties_button.config(image = self.show_img)
            Tooltip(self.properties_button, "Show object properties")
        else:
            self.object_frame.tkraise()
            self.property_details_frame.pack(fill="both", expand=True, padx=3, pady=3)
            self.properties_button.config(image = self.hide_img)
            Tooltip(self.properties_button, "Hide object properties")

    def show_objective_details(self):
        if self.objective_details_frame.winfo_ismapped():
            self.objective_details_frame.pack_forget()
            self.objective_button.config(image = self.show_img, compound = "left")
            Tooltip(self.objective_button, 'Show objective details')
        else:
            self.objective_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.objective_button.config(image = self.hide_img)
            Tooltip(self.objective_button, 'Hide objective details')

    def show_attribute_details(self):
        if self.attribute_details_frame.winfo_ismapped():
            self.attribute_details_frame.pack_forget()
            self.attribute_button.config(image=self.show_img)
            Tooltip(self.attribute_button, 'Show attribute details')
        else:
            self.attribute_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.attribute_button.config(image=self.hide_img)
            Tooltip(self.attribute_button, 'Hide attribute details')

    def show_input_details(self):
        if self.input_details_frame.winfo_ismapped():
            self.input_details_frame.pack_forget()
            self.input_button.config(image=self.show_img)
            Tooltip(self.input_button, 'Show input details')
        else:
            self.input_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.input_button.config(image=self.hide_img)
            Tooltip(self.input_button, 'Hide input details')

    def show_output_details(self):
        if self.output_details_frame.winfo_ismapped():
            self.output_details_frame.pack_forget()
            self.output_button.config(image=self.show_img)
            Tooltip(self.output_button, 'Show output details')
        else:
            self.output_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.output_button.config(image=self.hide_img)
            Tooltip(self.output_button, 'Hide output details')

    def show_file_details(self):
        if self.file_details_frame.winfo_ismapped():
            self.file_details_frame.pack_forget()
            self.file_button.config(image=self.show_img)
            Tooltip(self.file_button, 'Show file details')
        else:
            self.file_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.file_button.config(image=self.hide_img)
            Tooltip(self.file_button, 'Hide file details')
    
    def show_reference_details(self):
        if self.reference_details_frame.winfo_ismapped():
            self.reference_details_frame.pack_forget()
            self.reference_button.config(image=self.show_img)
            Tooltip(self.reference_button, 'Show reference details')
        else:
            self.reference_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.reference_button.config(image=self.hide_img)
            Tooltip(self.reference_button, 'Hide reference details')
    
    def show_folder_details(self):
        if self.folder_details_frame.winfo_ismapped():
            self.folder_details_frame.pack_forget()
            self.folder_button.config(image=self.show_img)
            Tooltip(self.folder_button, 'Show folder details')
        else:
            self.folder_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.folder_button.config(image=self.hide_img)
            Tooltip(self.folder_button, 'Hide folder details')

    def show_subscriber_details(self):
        if self.subscriber_details_frame.winfo_ismapped():
            self.subscriber_details_frame.pack_forget()
            self.subscriber_button.config(image=self.show_img)
            Tooltip(self.subscriber_button, 'Show subscriber details')
        else:
            self.subscriber_details_frame.pack(side="top", fill="both", expand=True, padx=3, pady=3)
            self.subscriber_button.config(image=self.hide_img)
            Tooltip(self.subscriber_button, 'Hide subscriber details')

    def bind_events(self):
        self.object_frame.bind('<Button-1>', self.on_press)
        self.object_frame.bind('<B1-Motion>', self.on_move)
        self.object_frame.bind('<ButtonRelease-1>', self.on_release)
        self.object_frame.bind('<Enter>', self.hover_enter)
        self.object_frame.bind('<Leave>', self.hover_leave)

    def on_press(self, event):
        self.offset_x = event.x - self.x
        self.offset_y = event.y - self.y

    def on_move(self, event):
        self.x = event.x - self.offset_x
        self.y = event.y - self.offset_y
        self.object_frame.place(x=self.x, y=self.y)
        self.canvas.create_window(self.x, self.y, window=self.object_frame, anchor='n')
        self.positions[self.object_name] = (self.x, self.y)
        self.object_dict["position"] = [self.x, self.y]

        # update current position in object file:
        file_name = f'{self.object_name}.object.txt'
        file_path = os.path.join(self.directory, 'current', self.object_name, file_name)
        new_dict = {}
        old_dict = {}

        with open(file_path, 'r') as f:
            object_info = f.read()
            object_info = object_info.replace("'", "\"")
            object_info = object_info.replace("(", "[")
            object_info = object_info.replace(")", "]")
            json_dict = json.loads(object_info)
            new_dict = json_dict["new_dict"]
            old_dict = json_dict["old_dict"]

        new_dict['position'] = (self.x, self.y)
        old_dict['position'] = (self.x, self.y)

        object_dict = {
            "new_dict": new_dict,
            "old_dict": old_dict
        }

        with open(file_path, "w") as f:
            f.write(str(object_dict))

        # expand canvas, when objects are moved:
        if self.scrollregion[0] < self.x+100:
            self.canvas.config(scrollregion = (0, 0, self.x+150, self.scrollregion[1]))
            self.scrollregion = (self.x+150, self.scrollregion[1])
            self.canvas.xview_moveto(1)
        if self.scrollregion[1] < self.y+250:
            self.canvas.config(scrollregion = (0, 0, self.scrollregion[0], self.y+300))
            self.scrollregion = (self.scrollregion[0], self.y+300)
            self.canvas.yview_moveto(1)

    def on_release(self, event):
        pass

    def hover_enter(self, event):
        self.object_frame.config(highlightbackground = '#0065bd', highlightthickness = 5)
        # self.tree.selection_set([self.object_name])
        for ob in self.object_dict["references"]:
            if ob in self.object_names.keys():
                self.object_names[ob].object_frame.config(highlightbackground = '#98c6ea', highlightthickness = 5)

    def hover_leave(self, event):
        self.object_frame.config(highlightthickness = 0)
        # self.tree.selection_remove([self.object_name])
        for ob in self.object_dict["references"]:
            if ob in self.object_names.keys():
                self.object_names[ob].object_frame.config(highlightthickness = 0)


