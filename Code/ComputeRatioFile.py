#Compute ratio
import cv2
import numpy as np
import os
import math
import re
from jsonfilereader import JsonReader, split_json
from helper import *

def diff_dict(d1,d2):
    return math.sqrt((d1['y']-d2['y'])**2+(d1['x']-d2['x'])**2)

def compute_ratio(image,js,OUT):

    """
    This function computes the ratio for one image
    """
    img = cv2.imread(image) # Read image
    js_points = JsonReader(js)
    nose = js_points.nose()
    lankle = js_points.ltankle()
    rankle = js_points.rtankle()

    threshold = 600
    """ First solution"""

    found = np.where(np.sum(img,axis = 2)< threshold)
    top = {'x':found[1][0],'y':found[0][0]}

    bottom = {'x':found[1][-1],'y':found[0][-1]} # This value change in the second version

    """ Second solution (take into account the position of the ankle)"""
    # Right ankle
    yR=int(rankle['y'])


    while (np.sum(img[yR,int(rankle['x'])]) <threshold):
        yR +=1

    yL=int(lankle['y'])
    while (np.sum(img[yL,int(lankle['x'])]) <threshold):
        yL +=1

    # Select the min between yR and yL
    if (yR <= yL):
        bottom = {'x':int(rankle['x']),'y':yR}
        alphaPosebottom = js_points.rtankle()
    else:
        bottom = {'x':int(lankle['x']),'y':yL}
        alphaPosebottom = js_points.ltankle()

    cv2.circle(img, (top['x'], top['y']), 5, (0, 255, 0), -1)
    cv2.circle(img, (bottom['x'], bottom['y']), 5, (0, 255, 0), -1)
    imgS= cv2.resize(img,(500,800))
    if (OUT):
        cv2.imshow(image,imgS)
        print("Please press the Enter key")
        cv2.waitKey(0)

    nose = js_points.nose()
    #lankle = js_points.ltankle()
    size_alpha = diff_dict(nose,alphaPosebottom)
    size = diff_dict(top,bottom)
    ratio = size/size_alpha
    return ratio


def compute_median_ratio(OUT = 0):

    PATHPHOTOS = "./All/" # To adapt in case you use this feature
    PATHJSON = "./JS/All/"

    ratio_list = []
    for root, dirs,files in os.walk(PATHPHOTOS):# Find all the files in the directory photos
        files.sort(key=natural_keys)
        for filename in files:
            if ("A" in filename): # Take the photos that were created by alphapose
                """ Take the corresponding photo and json file and apply ratio computation """
                image = PATHPHOTOS+filename
                number = natural_keys(filename.split('.')[0])[1]
                js = PATHJSON+"Body"+str(number)+"A.json"
                ratio_list.append(compute_ratio(image,js,OUT))

    return np.median(ratio_list)
