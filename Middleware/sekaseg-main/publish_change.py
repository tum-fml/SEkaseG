'''
This function is to publish the current object changements to subscribers via outlook
'''

import win32com.client as win32
import json
import os

def publish(object_name, object_changements, directory):
    # directory: path to the current folder
    email_list = []
    filename = f"{object_name}.object.txt"
    path = os.path.join(directory, object_name, filename)
    references = []

    # get subscriber e-mails:
    with open(path, 'r') as f:
        object_info = f.read()
        object_info = object_info.replace("'", "\"")
        object_info = object_info.replace("(", "[")
        object_info = object_info.replace(")", "]")

        json_dict = json.loads(object_info)
        new_dict = json_dict["new_dict"]

        for email in new_dict["subscribers"]:
            if email not in email_list:
                email_list.append(email)
        
        # fill list of references to get their subscribers as well:
        for ref in new_dict["references"]:
            if ref not in references:
                references.append(ref)
    
    # get e-mail addresses from subscribers of referenced objects:
    for ref in references:
        filename = f"{ref}.object.txt"
        path = os.path.join(directory, ref, filename)
        with open(path, 'r') as f:
            object_info = f.read()
            object_info = object_info.replace("'", "\"")
            object_info = object_info.replace("(", "[")
            object_info = object_info.replace(")", "]")

            json_dict = json.loads(object_info)
            new_dict = json_dict["new_dict"]

            for email in new_dict["subscribers"]:
                if email not in email_list:
                    email_list.append(email)

    if email_list:
        # Create Outlook application object
        outlook = win32.Dispatch('outlook.application')

        # Create new email message
        mail = outlook.CreateItem(0)
        mail.Subject = f"Project {directory.split('/')[-1]} - Changements in Object {object_name}"
        mail_text = f"Changements in Object {object_name}:\n"
        current_dict = object_changements[object_name]
        if current_dict:
            for key in current_dict.keys():
                if key == "objectives": # change state [0, 1] to ["in progress", "done"]
                    new = str()
                    old = str()
                    # current_dict[key][0]: new content of dict
                    new_properties, old_properties = current_dict[key]
                    for prop in new_properties:
                        if prop[1] == 0:
                            new += '\t\t' + str(prop[0]) + ':\t' +'in progress\n'
                        else:
                            new += '\t\t' + str(prop[0]) + ':\t' +'done\n'
                    for prop in old_properties:
                        if prop[1] == 0:
                            old += '\t\t' + str(prop[0]) + ':\t' + 'in progress\n'
                        else:
                            old += '\t\t' + str(prop[0]) + ':\t' + 'done\n'
                    mail_text += f"\nObjectives:\n\tNew values:\n{new}\n\tOld values:\n{old}"

                elif key == "attributes":
                    new = str()
                    old = str()
                    new_properties, old_properties = current_dict[key]
                    for prop in new_properties:
                        new += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2])
                        if prop[4]: # add tolerances if any
                            new += '\t' + str(prop[4])
                        new += '\n'
                    for prop in old_properties:
                        old += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2])
                        if prop[4]: # add tolerances if any
                            old += '\t' + str(prop[4])
                        old += '\n'
                    mail_text += f"\nAttributes:\n\tNew values:\n{new}\n\tOld values:\n{old}\n"

                elif key == "inputs":
                    new = str()
                    old = str()
                    new_properties, old_properties = current_dict[key]
                    for prop in new_properties:
                        new += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2]) + '\t' + str(prop[3])
                        new += '\n'
                    for prop in old_properties:
                        old += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2]) + '\t' + str(prop[3])
                        old += '\n'
                    mail_text += f"\nInputs:\n\tNew values:\n{new}\n\tOld values:\n{old}"

                elif key == "outputs":
                    new = str()
                    old = str()
                    new_properties, old_properties = current_dict[key]
                    for prop in new_properties:
                        new += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2]) + '\t' + str(prop[3])
                        new += '\n'
                    for prop in old_properties:
                        old += '\t\t' + str(prop[0]) + ':\t' + str(prop[1]) + '\t' + str(prop[2]) + '\t' + str(prop[3])
                        old += '\n'
                    mail_text += f"\nOutputs:\n\tNew values:\n{new}\n\tOld values:\n{old}"
                
                elif key == "files":
                    new = str()
                    old = str()
                    new_properties, old_properties = current_dict[key]
                    for prop in new_properties:
                        new += '\t\t' + str(prop)
                        new += '\n'
                    for prop in old_properties:
                        old += '\t\t' + str(prop)
                        old += '\n'
                    mail_text += f"\nFiles:\n\tNew values:\n{new}\n\tOld values:\n{old}"
        else:
            mail_text += "No changements\n\n"
        
        del object_changements[object_name]
        mail_text += f"\nChangements in Referenced Objects:\n"
        if bool(object_changements):
            for obj in object_changements.keys():
                mail_text += f"Changements in Object {obj}:"
                current_dict = object_changements[obj]
                if current_dict:
                    for key in current_dict.keys():
                        if key == "objectives": # change state [0, 1] to ["in progress", "done"]
                            new = str()
                            old = str()
                            for i in range(len(current_dict[key][0])): # iterate over new values
                                if current_dict[key][0][i][1] == 0:
                                    new += '\t\t' + str(current_dict[key][0][i][0]) + ':\t' +'in progress\n'
                                else:
                                    new += '\t\t' + str(current_dict[key][0][i][0]) + ':\t' +'done\n'
                            for i in range(len(current_dict[key][1])): # iterate over old values
                                if current_dict[key][1][i][1] == 0:
                                    old += '\t\t' + str(current_dict[key][1][i][0]) + ':\t' + 'in progress\n'
                                else:
                                    old += '\t\t' + str(current_dict[key][1][i][0]) + ':\t' + 'done\n'
                            mail_text += f"\nObjectives:\n\tNew values:\n{new}\n\tOld values:\n{old}"

                        elif key == "attributes":
                            new = str()
                            old = str()
                            for i in range(len(current_dict[key][0])): # iterate over new values
                                new += '\t\t' + str(current_dict[key][0][i][0]) + ':\t' + str(current_dict[key][0][i][1]) + '\t' + str(current_dict[key][0][i][2])
                                if current_dict[key][0][i][3]: # add tolerances if any
                                    new += '\t' + str(current_dict[key][0][i][3])   
                                new += '\n'
                            for i in range(len(current_dict[key][1])): # iterate over old values
                                old += '\t\t' + str(current_dict[key][1][i][0]) + ':\t' + str(current_dict[key][1][i][1]) + '\t' + str(current_dict[key][1][i][2])
                                if current_dict[key][1][i][3]: # add tolerances if any
                                    old += '\t' + str(current_dict[key][1][i][3])
                            mail_text += f"\nAttributes:\n\tNew values:\n{new}\n\tOld values:\n{old}\n"

                        elif key == "inputs":
                            new = str()
                            old = str()
                            for i in range(len(current_dict[key][0])):
                                new += '\t\t' + str(current_dict[0][i][0]) + ':\t' + str(current_dict[0][i][1] + '\t' + str(current_dict[0][i][2])) + '\n'
                            for i in range(len(current_dict[key][1])):
                                old += '\t\t' + str(current_dict[1][i][0]) + ':\t' + str(current_dict[1][i][1] + '\t' + str(current_dict[1][i][2])) + '\n'
                            mail_text += f"\nInputs:\n\tNew values:\n{new}\n\tOld values:\n{old}"

                        elif key == "outputs":
                            new = str()
                            old = str()
                            for i in range(len(current_dict[key][0])):
                                new += '\t\t' + str(current_dict[0][i][0]) + ':\t' + str(current_dict[0][i][1] + '\t' + str(current_dict[0][i][2])) + '\n'
                            for i in range(len(current_dict[key][1])):
                                old += '\t\t' + str(current_dict[1][i][0]) + ':\t' + str(current_dict[1][i][1] + '\t' + str(current_dict[1][i][2])) + '\n'
                            mail_text += f"\nOutputs:\n\tNew values:\n{new}\n\tOld values:\n{old}"
                        
                        elif key == "files":
                            new = str()
                            old = str()
                            for i in range(len(current_dict[key][0])):
                                new += '\t\t' + str(current_dict[0][i][0]) + ':\t' + str(current_dict[0][i][1] + '\t') + '\n'
                            for i in range(len(current_dict[key][1])):
                                old += '\t\t' + str(current_dict[1][i][0]) + ':\t' + str(current_dict[1][i][1] + '\t') + '\n'
                            mail_text += f"\nOutputs:\n\tNew values:\n{new}\n\tOld values:\n{old}"
                else:
                    mail_text += "No changements\n\n"
        else:
            mail_text += "No references\n\n"

        mail.Body = mail_text
        mail.To = ";".join(email_list)
        # Send message
        mail.Send()
