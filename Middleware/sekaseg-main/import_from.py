import csv
import pytesseract
import cv2
import numpy as np
import re
from PyPDF2 import PdfReader
import json

def data_from_csv(directory, dialog2, object_dict):
    new_dict = {
        "objectives": [],
        "attributes": [],
        "inputs": [],
        "outputs": [],
        "files": [],
        "references": [],
        "subscribers": [],
        "folder": '',
        "position": object_dict["position"]
    }
    if dialog2 == 'Only defined elements':
        with open(directory) as f:
            reader = csv.reader(f, delimiter = ';')
            line = 0
            for row in reader:
                if line == 0 or line == 1:
                    line += 1
                else:
                    for i in range(len(object_dict["objectives"])):
                        if row[2] == object_dict["objectives"][i][0]:
                            if row[4] == 'True':
                                new_dict["objectives"].append([row[2], 1])
                            elif row[4] == 'False':
                                new_dict["objectives"].append([row[2], 0])
                    for i in range(len(object_dict["attributes"])):
                        if row[2] == object_dict["attributes"][i][0]:
                            new_dict["attributes"].append([row[2], row[3], row[4], row[5], []])
                            if not row[6] == '' and not row[7] == '':
                                new_dict["attributes"][-1][4] = [row[6], row[7]] # insert tolerances
                    for i in range(len(object_dict["inputs"])):
                        if row[2] == object_dict["inputs"][i][0]:
                            new_dict["inputs"].append([row[2], row[3], row[4], row[5]])
                    for i in range(len(object_dict["outputs"])):
                        if row[2] == object_dict["outputs"][i][0]:
                            new_dict["outputs"].append([row[2], row[3], row[4], row[5]])
                    for i in range(len(object_dict["files"])):
                        if row[2] == object_dict["files"][i][0]:
                            new_dict["files"].append(row[2])
                    # no reference or folder import because can't be predefined
    else: # "Everything" option
        with open(directory) as f:
            reader = csv.reader(f, delimiter = ';')
            line = 0
            for row in reader:
                if line == 0 or line == 1:
                    line += 1
                else:
                    if row[1] == "Objectives":
                        state = 0
                        if row[4] == 'True':
                            state = 1
                        new_dict["objectives"].append([row[2], state])
                    if row[1] == "Attributes":
                        if len(row) > 6:
                            new_dict["attributes"].append([row[2], row[3], row[4], row[5], [row[6], row[7]]])
                        else:
                            new_dict["attributes"].append([row[2], row[3], row[4], row[5], []])
                    if row[1] == "Inputs":
                        new_dict["inputs"].append([row[2], row[3], row[4], row[5]])
                    if row[1] == "Outputs":
                        new_dict["outputs"].append([row[2], row[3], row[4], row[5]])
                    if row[1] == "Files":
                        new_dict["files"].append(row[2])
                    if row[1] == "Folder":
                        new_dict["folder"] = row[4]
                    if row[1] == "References":
                        new_dict["references"].append(row[4])
    return(new_dict)

def data_from_image(directory, object_dict): # only import of predefined properties
    # pytesseract uses tesseract
    # for windows download of tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    # if necessary relocate Tesseract-OCR to C:\Program Files
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe" #Version 5.3.1

    # Read image with opencv
    img = cv2.imread(directory)
    # convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1,1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Apply threshold to get image with only black and white
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    t = pytesseract.image_to_string(img)
    text = re.split('\n', t)

    new_dict ={
        "objectives": [],
        "attributes": [],
        "inputs": [],
        "outputs": [],
        "files": [],
        "references": [],
        "subscribers": [],
        "folder": '',
        "position": object_dict["position"]
    }

    for row in text:
        # objectives are not imported via jpg/png
        for i in range(len(object_dict["attributes"])):
            if row.startswith(object_dict["attributes"][i][0]):
                s = row.split(' ')
                if "=" in s:
                    s.remove('=')
                    unit = " ".join(s[2:])
                    new_dict["attributes"].append([s[0], '', s[1], unit, []])
        for i in range(len(object_dict["inputs"])):
            if row.startswith(object_dict["inputs"][i][0]):
                s = row.split(' ')
                if "=" in s:
                    s.remove('=')
                    unit = " ".join(s[2:])
                    new_dict["inputs"].append([s[0], '', s[1], unit, []])
        for i in range(len(object_dict["outputs"])):
            if row.startswith(object_dict["outputs"][i][0]):
                s = row.split('= ')
                if "=" in s:
                    s.remove('=')
                    unit = " ".join(s[2:])
                    new_dict["outputs"].append([s[0], '', s[1], unit, []])
        # no objective, file, reference, folder import
    return new_dict

def data_from_pdf(directory, dialog2, object_dict):
    new_dict = {
            "objectives": [],
            "attributes": [],
            "inputs": [],
            "outputs": [],
            "files": [],
            "references": [],
            "subscribers": [],
            "folder": '',
            "position": object_dict["position"]
        }
    if dialog2 == 'Only defined elements':
        reader = PdfReader(directory)
        for page in reader.pages:
            t = page.extract_text()
            text = re.split('\n', t)
            while text:
                word = text[0]
                for i in range(len(object_dict["objectives"])):
                    name = object_dict["objectives"][i][0]
                    if word == name:
                        new_dict["objectives"].append([name, text[1]])
                for i in range(len(object_dict["attributes"])):
                    name = object_dict["attributes"][i][0]
                    if word == name:
                        new_dict["attributes"].append([name, text[1], text[2], text[3], []]) # no tolerances import
                for i in range(len(object_dict["inputs"])):
                    name = object_dict["inputs"][i][0]
                    if word == name:
                        new_dict["inputs"].append([name, text[1], text[2], text[3]])
                for i in range(len(object_dict["outputs"])):
                    name = object_dict["outputs"][i][0]
                    if word == name:
                        new_dict["outputs"].append([name, text[1], text[2], text[3]])
                for i in range(len(object_dict["files"])):
                    name = object_dict["files"][i][0]
                    if word == name:
                        new_dict["files"].append(name)
                text.remove(word)
                # no reference or folder import because can't be predefined
    else: # option "Everything"
        reader = PdfReader(directory)
        for page in reader.pages:
            t = page.extract_text()
            text = re.split('\n| ', t) # get list with rows as strings
            remove = text[10]
            text = [i for i in text if i != remove]
            while text:
                p = text[0]
                if p == "Objectives":
                    new_dict["objectives"].append([text[1], text[2]])
                elif p == "Attributes":
                    if text[6] not in ['Inputs', 'Attributes']: # if there are no tolerances
                        new_dict["attributes"].append([text[1], text[2], text[3], text[4], (text[5], text[6])])
                    else: # if there are no tolerances
                        new_dict["attributes"].append([text[1], text[2], text[3], text[4], []])
                elif p == "Inputs":
                    new_dict["inputs"].append([text[1], text[2], text[3], text[4]])
                elif p == 'Outputs':
                    new_dict["outputs"].append([text[1], text[2], text[3], text[4]])
                elif p == 'Files':
                    new_dict["files"].append(text[1])
                elif p == 'Folder':
                    new_dict["folder"] = text[1]
                elif p == 'References':
                    new_dict["references"].append(text[1])
                text.pop(0)
    return(new_dict)

def data_from_txt(directory, dialog2, object_dict):
    if dialog2 == 'Only defined elements':
        new_dict = {
            "objectives": [],
            "attributes": [],
            "inputs": [],
            "outputs": [],
            "files": [],
            "references": [],
            "subscribers": [],
            "folder": '',
            "position": object_dict["position"]
        }
        # read txt file and store content in new_dict:
        json_dict = {}
        with open(directory, 'r') as f:
            object_info = f.read()
            object_info = object_info[object_info.find('{') : object_info.find('}')+1]
            object_info = object_info.replace("'", "\"")
            object_info = object_info.replace("(", "[")
            object_info = object_info.replace(")", "]")
            json_dict = json.loads(object_info)
        
        # compare import file to existing object dict:
        for i, (name,_) in enumerate(object_dict["objectives"]):
            for j, jname in enumerate(json_dict["objectives"]):
                if name == jname:
                    new_dict["objectives"].append(json_dict["objectives"][j])
        for i, (name,_,_,_,_) in enumerate(object_dict["attributes"]):
            for j, (jname,_,_,_,_) in enumerate(json_dict["attributes"]):
                if name == jname:
                    new_dict["attributes"].append(json_dict["attributes"][j])
        for i, (name,_,_,_) in enumerate(object_dict["inputs"]):
            for j, (jname,_,_,_) in enumerate(json_dict["inputs"]):
                if name == jname:
                    new_dict["inputs"].append(json_dict["inputs"][j])
        for i, (name,_,_,_) in enumerate(object_dict["outputs"]):
            for j, (jname,_,_,_) in enumerate(json_dict["outputs"]):
                if name == jname:
                    new_dict["outputs"].append(json_dict["outputs"][j])
        # no reference, file or folder import because can't be predefined
    else: # "Everything" option
        json_dict = {}
        with open(directory, 'r') as f:
            object_info = f.read()
            object_info = object_info[object_info.find('{') : object_info.find('}')+1]
            object_info = object_info.replace("'", "\"")
            object_info = object_info.replace("(", "[")
            object_info = object_info.replace(")", "]")
            json_dict = json.loads(object_info)
            new_dict = json_dict
    return new_dict
