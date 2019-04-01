"""
This file computes the file for the trajectory of the person
"""
import os
import re
from jsonfilereader import JsonReader, split_json, pixel_fall, height_person
from helper import *


def compute_cm(body_parts):
    """
    Given:
    body_parts – list of body parts position with the order nose, shoulder,elbow, wrist,hip,knee,ankle going from left to right

    Return:
    CM – the center of mass computed

    Abstract:
    COMPUTE takes a list of body parts position with the order nose, shoulder,elbow, wrist,hip,knee,ankle going from left to right
    and computes the center of mass of the person.
    """


    ratio = [0.073,0.026,0.016,0.507,0.103,0.043]#Head, upperarm, forarm, trunk, thigh,calf

    list_centers = []


    # compute_cm all the centers!

    chead = {'x' : body_parts[0]['x'],'y' : body_parts[0]['y']}

    cluparm = {'x' : (body_parts[1]['x'] + body_parts[3]['x'])/2,'y' : (body_parts[1]['y'] + body_parts[3]['y'])/2}
    cruparm = {'x' : (body_parts[2]['x'] + body_parts[4]['x'])/2,'y' : (body_parts[2]['y'] + body_parts[4]['y'])/2}

    clforarm = {'x' : (body_parts[3]['x'] + body_parts[5]['x'])/2,'y' : (body_parts[3]['y'] + body_parts[5]['y'])/2}
    crforarm = {'x' : (body_parts[4]['x'] + body_parts[6]['x'])/2,'y' : (body_parts[4]['y'] + body_parts[6]['y'])/2}

    cshoulder = {'x' : (body_parts[1]['x'] + body_parts[2]['x'])/2,'y' : (body_parts[1]['y'] + body_parts[2]['y'])/2}
    chip = {'x' : (body_parts[7]['x'] + body_parts[8]['x'])/2,'y' : (body_parts[7]['y'] + body_parts[8]['y'])/2}
    ctrunk = {'x' : (cshoulder['x'] + chip['x'])/2,'y' : (cshoulder['y'] + chip['y'])/2}

    clthigh = {'x' : (body_parts[7]['x'] + body_parts[9]['x'])/2,'y' : (body_parts[7]['y'] + body_parts[9]['y'])/2}
    crthigh = {'x' : (body_parts[8]['x'] + body_parts[10]['x'])/2,'y' : (body_parts[8]['y'] + body_parts[10]['y'])/2}

    clcalf = {'x' : (body_parts[9]['x'] + body_parts[11]['x'])/2,'y' : (body_parts[9]['y'] + body_parts[11]['y'])/2}
    crcalf = {'x' : (body_parts[10]['x'] + body_parts[12]['x'])/2,'y' : (body_parts[10]['y'] + body_parts[12]['y'])/2}

    list_centers.append(chead)
    list_centers.append(cluparm)
    list_centers.append(cruparm)
    list_centers.append(clforarm)
    list_centers.append(crforarm)
    list_centers.append(cshoulder)
    list_centers.append(chip)
    list_centers.append(ctrunk)
    list_centers.append(clthigh)
    list_centers.append(crthigh)
    list_centers.append(clcalf)
    list_centers.append(crcalf)
    # compute_cm the center of mass with the ratio
    xCM = (chead['x']*ratio[0] + (cluparm['x']+cruparm['x'])*ratio[1] + \
          (clforarm['x']+crforarm['x'])*ratio[2] + ctrunk['x']*ratio[3] + \
          (clforarm['x']+crforarm['x'])*ratio[2] + (clthigh['x']+crthigh['x'])*ratio[4] + \
          (clcalf['x']+crcalf['x'])*ratio[5])
    #xCM = chead['x'] * ratio[0]
    yCM = (chead['y']*ratio[0] + (cluparm['y']+cruparm['y'])*ratio[1] + \
          (clforarm['y']+crforarm['y'])*ratio[2] + ctrunk['y']*ratio[3] + \
          (clforarm['y']+crforarm['y'])*ratio[2] + (clthigh['y']+crthigh['y'])*ratio[4] + \
          (clcalf['y']+crcalf['y'])*ratio[5])
    #yCM = chead['y'] * ratio[0]
    CM = {'x':xCM,'y':yCM}

    list_centers.append(CM)

    return CM

def trajectory(PATHJSON="./JsonFiles/"):
    """

    """
    """
    Given:
    PATHJSON – Path for all the json files

    Return:
    Nothing, everything is saved in two files "Trajectory" for the trajectory of the center of mass, the nose, the left foot, the right foot
    and "Confidences" that will contain the confidence of the prediction of the position of the person with Alphapose

    Abstract:
    TRAJECTORY saves the trajectory of the center of mass, the nose and
    the feet in the y-axis

    The order is
        1) Center of mass
        2) Nose
        3) Left foot
        4) Right foot.
    It also saves the confidence of the prediction of the position of the person with Alphapose
    """

    DIR = "Trajectory"
    os.system('rm -r '+ DIR) # Remove the directory to be sure that everything is new
    os.system("mkdir " + DIR)
    center_x = []
    center_y = []
    nose_y = []
    foot_l = []
    foot_r = []
    confidences = []
    previous_number = 0
    total_values = 0
    for root, dirs,files in os.walk(PATHJSON): # Find all the files in the directory photos
        files.sort(key=natural_keys)
        for filename in files:
            total_values +=1
            """ Take the corresponding photo and json file and apply ratio computation """
            image = PATHJSON+filename
            number = natural_keys(filename.split('.')[0])[1]
            while (previous_number+1 != number):
                center_x.append(0)
                center_y.append(500)
                nose_y.append(500)
                foot_l.append(500)
                foot_r.append(500)
                confidences.append(0)
                previous_number +=1
            js = PATHJSON+"Photo"+str(format(number,"04"))+".json"
            js1 = JsonReader(js)
            body = js1.body_parts()
            # Add a line here for the confidence of the prediction
            conf = js1.confidence_value()
            CM = compute_cm(body)
            center_y.append(CM['y'])
            nose_y.append(js1.nose()['y'])
            foot_l.append(js1.ltankle()['y'])
            foot_r.append(js1.rtankle()['y'])
            center_x.append(CM['x'])
            confidences.append(conf)
            previous_number = number
    # Save in a file for later plot
    name_file = ".".join(("/".join((DIR,PATHJSON.split("/")[-2])),"txt"))

    f = open(name_file,"w")
    for i in range(len(center_x)):
        f.write(str(center_x[i])+" ")
    f.write("\n")
    for i in range(len(center_y)):
        f.write(str(center_y[i])+" ")
    f.write("\n")

    for i in range(len(nose_y)):
        f.write(str(nose_y[i])+" ")
    f.write("\n")
    for i in range(len(foot_l)):
        f.write(str(foot_l[i])+" ")
    f.write("\n")
    for i in range(len(foot_r)):
        f.write(str(foot_r[i])+" ")
    f.close()

    f2 = open(DIR+"/Confidences.txt","w")
    for i in range(len(confidences)):
        f2.write(str(confidences[i])+"\n")
    f2.close()
