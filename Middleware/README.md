# SEkaseG Tool - Implementation
This README explains the structure of the code behind the SEkaseG tool. The user's manual can be found in the file "instructions.docx".

## 1 General Structure
The tool is implemented in Python using the libraries tkinter for creating the GUI and ttkbootstrap for enhancing the GUI in style. The main file is "objectCreateTool.py" where the root window of the GUI is implemented. In the files "object_template.py", "object2mainCanvas.py" and "change_object.py" are the main code the tool is implemented. The other files serve to provide specific functions for the tool.

## 2 Executable File
Before going into details of the code, the creation of the .exe file is explained. To bundle the code up into a compact app, PyInstaller is used. To install it, run this command in a terminal:
> pip install pyinstaller

 The following lines must be run from a command terminal inside the tool's directory:
> pyinstaller --onefile --windowed --add-data "Ionic-Ionicons-Home.32.png;." --add-data "Pictogrammers-Material-Forklift.ico;." --add-data "Microsoft-Fluentui-Emoji-Mono-New-Button.48.png;." --add-data "Ionic-Ionicons-Trash.32.png;." --add-data "Ionic-Ionicons-Eye-outline.32.png;." --add-data "Microsoft-Fluentui-Emoji-Mono-New-Button.32.png;." --add-data "Ionic-Ionicons-Megaphone-outline.32.png;." --add-data "Github-Octicons-Bell-24.32.png;." --add-data "Ionic-Ionicons-Save-outline.32.png;." --add-data "Github-Octicons-Bell-slash-24.32.png;." --add-data "Ionic-Ionicons-Enter-outline.32.png;." --add-data "Ionic-Ionicons-Pencil-outline.32.png;." --add-data "Ionic-Ionicons-Exit-outline.32.png;." --add-data "Ionic-Ionicons-Eye-off.32.png;." --add-data "Microsoft-Fluentui-Emoji-Mono-Open-File-Folder.32.png;." --add-data "Amitjakhu-Drip-Copy.32.png;." --add-data "Ionic-Ionicons-Trash.48.png;.” --add-data "Ionic-Ionicons-Arrow-back.32.png;." --add-data "Ionic-Ionicons-Arrow-forward.32.png;." sekaseg_tool.py

The --add-data commands are used to include all the icons that are used for the SEkaseG tool. When finished building, the .exe file can be found in the dist folder within the tool's directory. Sometimes building the .exe file doesn't work, then it might help to update PyInstaller using
> pip install --upgrade pyinstaller

Oftentimes, antivirus programs consider the .exe file a security threat and put it in quarantine. In this case, the file has to be removed from quarantine manually and/or the antivirus program must be switched off when building the .exe file.

## 3 Root Window
In the file "sekaseg_tool.py", the main window is implemented. After importing needed libraries, the class "Tool" is created. At the bottom of the file, an instance of the class is created and the application is run using the mainloop() function defined inside the class. The Tool class defines the root window of the application consisting of three elements: the canvas, the treeview and the button frame.

The layout of the root window is created using two ttk.PanedWindows, the 1st one containing the 2nd one and the canvas frame (horizontal orientation), the 2nd one containing the treeview and the button frame (vertical orientation). The contents of the PanedWindows are added including their respective weights to define the space they take up inside the root window (1:5 for the 1st one, 1:3 for the 2nd one).

At the top of the root window a menu bar containing the item "file" to choose a project file is placed. Upon clicking on it, a cascade with options for creating a new project file or opening an existing one appears. When creating a new project file, the folder "Projects" is created in the tool directory if not already existent. Within the projects folder, each project has its own folder. A project folder always consists of the three folders "current", "back" and "forth" to navigate between versions (see Section 7.2). Each of the three folders contains one folder for each object belonging to the respective version. They also contain a text file called "folders" that lists the names of the folders that exist within the version. When opening an already existing file, the project file is selected by the user via a filedialog. The treeview and the canvas are filled with folders and objects with the information fetched from the "current" folder.

### 3.1 Canvas Frame
For the canvas, horizontal and vertical scrollbars are created. They are packed onto the canvas frame as well as the canvas. The scrollbars and the canvas are connected together such that the canvas is moved when the scrollbars are used, using the "config" function on each scrollbar after having created the single elements.

In the upper right-hand corner of the canvas, the home button for resetting the canvas view and the version navigation buttons are placed.

### 3.2 Treeview Frame
On top of the treeview frame, a label is packed. It displays "/" if no project file is opened, otherwise it contains the name of the project.

For the overview of folders and objects, a ttk.Treeview widget is used. The show option of the treeview takes on the value "tree" for a hierarchical structure. Folders appear always in the 0th level of the treeview, whereas objects are placed on the 1st level. A vertical scrollbar is added and the function for highlighting objects on canvas when selected in the treeview is bound to it.

### 3.3 Button Frame
The button frame contains two subframes, one for the folder buttons and one for the object buttons. On each of the subframes, a label specifying the element the subframe refers to (folders or objects), a button for creating elements and a button for deleting elements are placed. A separator widget is placed between the two subframes. The buttons cannot be operated before a project file is opened, otherwise an error message will appear.

## 4 New Object
In the file "new_object.py" the class NewObject is implemented. An instance of the class is created every time the button for a new object is pressed. A tk.Toplevel window is created based on the root window. Various elements (e.g. the canvas, the treeview, the back_button) are handed over as arguments not because they are relevant for the new object window, but because they are passed on later, when the object is saved onto the canvas.

The structure for saving the properties of an object is a dictionary. The dictionary's keys are the object's properties and its position on canvas. The position is initialized when pressing the new object button and later modified when the object is pushed around the canvas. The values of the dictionary are lists containing the elements of the respective property. Each element consists of several values that are again stored in lists. E.g. for every objective, the name of the objective and its value ("done" or "in progress") is stored as a list within the list belonging to the key "objectives" in the dictionary. While the window for a new object is open, each input field of each property is stored in a separate list (e.g. checkbuttons for objectives and labels for attributes). Before the window is closed, the values are read from the input fields and stored in the dictionary.

The layout of this windows is as follows: at the top, the name of the object followed by buttons for saving, deleting, subscribing etc. are located. In the lower part, each property has an individual frame in which elements can be added and deleted with buttons.

When the object is saved, the values for each element of each property are extracted from the input fields and stored in the dictionary. Each object has a folder in the file system. For storing, a new dictionary with the keys "new_dict" and "old_dict" is created. The value for both keys is the dictionary containing the object values. When the object is modified later on, the old dictionary contains the old version of the object and the new dictionary the new one to keep track of the changes made. The object is handed over to the CanvasObject class. The object name is inserted under the respective folder in the treeview and referenced objects are updated in the file system as well as on canvas (references are mutual). Finally, the window is destroyed.

## 5 Canvas
The class CanvasObject is implemented in the file "canvas.py". Each time an object is saved (after having created or modified an object), an instance of CanvasObject is created. A CanvasObject is a rectangle on canvas at the position handed over at the instantiation of the class. The input fields are again stored in seperate lists as well as the tooltips. The properties of the object can be folded in and out using the show/hide buttons. For this function, the frames that can be shown or hidden are stored in the frames list when created. The tkinter function pack_forget() is used to temporarily hide a frame.

The different frames of the CanvasObject are as follows:
- the **basic frame** contains the object name in a label on top, various buttons for interacting with the object and the property frame
- the **property frame** contains a show/hide button for the properties and the individual frames for each property containing their details
- each property has a separate frame (**property details frames**) that is only created and filled with values if there is at least one element of the property defined. Each frame has a show/hide button to make its contents visible/unvisible. The input fields of a property element are filled with values but they are disabled as they can only be altered in the change object window.

## 6 Change Object
The class ChangeObject in the file "change_object.py" is similar to the class NewObject. However, there are two main differences:

1. The existing values for each property are placed in the input fields and can be modified in the change object window. To keep track of the changes made, there are two dictionaries. One stores the old values, the other one the modified new values. The structure for both is the same as the dictionary for new objects.

2. The ChangeObject class is used for updating the references of objects. If a user defines object 1 as a reference in object 2, object 1 must also contain object 2 as a reference (references are always mutual). For this purpose, upon saving object 2, object 1 is removed from canvas and an instance of ChangeObject is created with the parameter "directly2canvas" set to True. In this case, no window is created, only object 1's dictionary in the file system is updated. Then, a new CanvasObject for object 1 is created with the new reference value.

## 7 Other Files
### 7.1 Tooltips
All of the buttons in the application are explained using tooltips, which are implemented as a class in the seperate "tooltips.py" file. The tooltips are implemented as a ttk.Toplevel that is bound to the hovering over a widget. To create an instance of the class the respective widget and the text for the tooltip must be handed over.

### 7.2 Version Navigation
In the file "navigate_versions.py" the functions for going back and forth between versions are implemented. They are called from the root window file and from the canvas file. 

**Save a current version** If a version of the project is changed, the back folder is emptied, the contents of the current folder are shifted into the back folder, the new version is stored in the current folder and the back button is enabled (if it is not already active). 

Actions that trigger the old version to be saved in the back folder
- folder or object is created or deleted
- an object is changed
- a subscriber is added or removed

**Go back** When the back button is pressed, the contents in the forth folder (if there are any) are removed and the contents of current are copied into forth. The current folder is emptied and the contents of the back folder are moved to current. Finally, the back folder is emptied, the back button is disabled and the the forth button is enabled.

**Go forth** If the forth button is pressed, the same procedure as for the back button happens in reversed order.

### 7.3 Publish Change
In the windows for new objects and changing an object, the changes made to the object and to its references can be sent via e-mail to the subscribers of an object. A dictionary called "changements" is initialized. Its keys are the objects' names and its values are the properties that are changed.

In the file "object_changements.py", the changes made to the objects are extracted. For this purpose, the text file of each considered object stored in the file system is used. The two dictionaries "old_dict" and "new_dict" are compared to each other. All properties except position, subscribers, references and folder are considered. If at least one element of a property differs in the two dictionaries, the property is stored in the changements dictionary.

The publishing of the e-mail is implemented in the file "publish_change.py". The e-mail is sent to all subscribers of the object and to the subscribers of the referenced objects. The e-mail addresses are collected in the subscribers list.

The subject of the e-mail consists of the names of the project and the object. The text is put together by adding part by part to a string which is the content of the e-mail. First, the changes in the considered object are added, the changes in the referenced objects follow.

### 7.4 Export and Import of Object Values
**Export** The values of objects can be exported from canvas via the export button. After having chosen the export format, the respective function from the file "export2.py" is called. On each file, the date and time of creation of the file is written. The values of the object follow in tabular form.

**Import** The import of values for objects can be done in the windows for creating/modifying an object via the import button. Besides choosing the format of the import file, the user has to choose as well between two import modes: (a) every value in the import file is imported (option for import files that were created using the SEkaseG tool) or (b) the import file is being searched for the names of property elements that have already been defined in the object; only the values of those elements are imported. For PDF, CSV and text files both options are available. For image files, only option (b) is applicable since the tool can't generate image files. The image import mode is intended to be used for PNG/JPG files created with CAD programs, that contain data of an object. The library uses an AI model for optical character recognition, however it doesn't work reliable on all images.