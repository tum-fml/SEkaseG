import csv
from datetime import datetime
import os
# from reportlab.platypus import Table, SimpleDocTemplate
from reportlab import platypus

def data2csv(filepath, object_name, object_dict):
    d = datetime.now()

    with open(filepath, "w", newline='') as f:
        writer = csv.writer(f, delimiter=";")

        writer.writerow([str(d)])
        writer.writerow(['Object name', 'Category', 'Name', 'Shortcut', 'Value', 'Unit', '+', '-'])
        for (key, value) in object_dict["objectives"]:
            if value == 0:
                writer.writerow([object_name, 'Objectives', key,'', 'False'])
            else:
                writer.writerow([object_name, 'Objectives', key,'', 'True'])
        for (key, shortcut, value, unit, tol) in object_dict["attributes"]:
            if tol:
                writer.writerow([object_name, 'Attributes', key, shortcut, value, unit, tol[0], tol[1]])
            else:
                writer.writerow([object_name, 'Attributes', key, shortcut, value, unit])
        for key, shortcut, value, unit in object_dict["inputs"]:
            writer.writerow([object_name, 'Inputs', key, shortcut, value, unit])
        for key, shortcut, value, unit in object_dict["outputs"]:
            writer.writerow([object_name, 'Outputs', key, shortcut, value, unit])
        for key in object_dict["files"]:
            writer.writerow([object_name, 'Files', key, '', ''])
        writer.writerow([object_name, 'Folder', '', '', object_dict["folder"]])
        for value in object_dict["references"]:
            writer.writerow([object_name, 'References', '', '', value])
    os.startfile(filepath)

def data2csv_for_simulink(filepath, object_dict):
    #d = datetime.now()
    shortcut_list = []
    value_list = []
    unit_list = []
    for (_, shortcut, value, unit, _) in object_dict["attributes"]:
        shortcut_list.append(shortcut)
        value_list.append(value)
        unit_list.append(unit)
    for (_, shortcut, value, unit) in object_dict["inputs"]:
        shortcut_list.append(shortcut)
        value_list.append(value)
        unit_list.append(unit)
    for (_, shortcut, value, unit) in object_dict["outputs"]:
        shortcut_list.append(shortcut)
        value_list.append(value)
        unit_list.append(unit)
    
    with open(filepath, "w", newline='') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(shortcut_list)
        writer.writerow(value_list)
        writer.writerow(unit_list)

        #writer.writerow([str(d)]) --> brauchen wir Zeitangabe?
        #writer.writerow(['Object name', 'Category', 'Name', 'Shortcut', 'Value', '+', '-'])
    os.startfile(filepath)

# function built following instructions on:
# https://www.blog.pythonlibrary.org/2010/09/21/reportlab-tables-creating-tables-in-pdfs-with-python/

def data2pdf(filepath, object_name, object_dict):
    d = datetime.now()
    pdf = platypus.SimpleDocTemplate(filepath)
    elements = []
    data = [[d], ['Object name', 'Category', 'Name', 'Shortcut', 'Value', 'Unit', '+', '-']]
    for (name, state) in object_dict["objectives"]:
        objective_data = [object_name, 'Objectives', str(name), '']
        if state == 0:
            objective_data.append(str(False))
        else:
            objective_data.append(str(True))
        data.append(objective_data)
    for (name, shortcut, value, unit, tol) in object_dict["attributes"]:
        attribute_data = [object_name, 'Attributes', str(name), str(shortcut), str(value), str(unit)]
        if tol:
            attribute_data.append(str(tol[0]))
            attribute_data.append(str(tol[1]))
        data.append(attribute_data)
    for (name, shortcut, value, unit) in object_dict["inputs"]:
        data.append([object_name, 'Inputs', str(name), str(shortcut), str(value), str(unit)])
    for (name, shortcut, value, unit) in object_dict["outputs"]:
        data.append([object_name, 'Outputs', str(name), str(shortcut), str(value), str(unit)])
    for name in object_dict["files"]:
        data.append([object_name, 'Files', str(name), '', ''])
    data.append([object_name, 'Folder', '', '', str(object_dict["folder"])])
    for value in object_dict["references"]:
        data.append([object_name, 'References', '', '', str(value)])

    t = platypus.Table(data)
    elements.append(t)
    
    pdf.build(elements)
    os.startfile(filepath)

def data2txt(filepath, object_name, object_dict):
    # Define the name of the directory and the file to be opened
    export_dict = object_dict.copy()
    d = datetime.now()
    for i, (name, state) in enumerate(export_dict["objectives"]):
        if state == 0:
            export_dict["objectives"][i] = [name, 'False']
        else:
            export_dict["objectives"][i] = [name, 'True']

    # don't export references, subscribers, position
    export_dict.pop("subscribers")
    export_dict.pop("position")
    
    with open(filepath, "w+") as f:
        f.write(str(d)+'\n\n')
        f.write(str(export_dict))
    os.startfile(filepath)