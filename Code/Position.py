"""
This file computes the array of the postions of the different body parts
"""
import numpy as np

def compute_positions(FILENAME="Trajectory/JsonFiles.txt"):
    """
    Given:
    FILENAME – a file name containing the position of the the center of mass, the nose, the left foot and the right foot on 4 different lines

    Return:
    positionCenterMass – numpy array containing the position of the center of mass
    positionNose – numpy array containing the position of the nose
    positionFootL – numpy array containing the position of the left foot
    positionFootR – numpy array containing the position of the right foot
    meanPositionBottom – numpy array containing the position of mean of the right foot and left foot positions
    sizePerson – numpy array containing the size of the person for each index of the array of position

    Abstract:
    Given a text file containing the positions of the center of mass, nose, left foot and right foot, this function returns the corresponding numpy arrays,
    the array containing the mean of the right foot and left foot positions and the size of the person for each index of the array of position
    """
    try:
        with open(FILENAME) as f:
            lines = f.readlines()
    except:
        raise ValueError('Impossible to read the file '+ FILENAME)

    centersXstr = lines[0].split(" ")
    centersYstr = lines[1].split(" ")
    noseYstr = lines[2].split(" ")
    footLstr = lines[3].split(" ")
    footRstr = lines[4].split(" ")

    centersX = []
    centersY = []
    noseY = []
    footL = []
    footR = []
    for i in range(len(centersYstr)-1):
        centersX.append(float(centersXstr[i]))
        centersY.append(float(centersYstr[i]))
        noseY.append(float(noseYstr[i]))
        footL.append(float(footLstr[i]))
        footR.append(float(footRstr[i]))

    positionCenterMassX = np.array(centersX)
    positionCenterMassY = np.array(centersY)
    positionNose = np.array(noseY)
    positionfootL = np.array(footL)
    positionfootR = np.array(footR)

    meanPositionBottom = (positionfootL + positionfootR)/2

    sizePerson = abs(positionNose - meanPositionBottom)

    return positionCenterMassX, positionCenterMassY, positionNose, positionfootL, positionfootR, meanPositionBottom, sizePerson
