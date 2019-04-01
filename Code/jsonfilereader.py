import json
import os

class JsonReader:
    """
    [
     // for person_1 in image_1
     {
        "image_id" : string, image_1_name,
        "category_id" : int, 1 for person
        "keypoints" : [x1,y1,c1,...,xk,yk,ck],
        "score" : float,
     },
     // for person_2 in image_1
     {
        "image_id" : string, image_1_name,
        "category_id" : int, 1 for person
        "keypoints" : [x1,y1,c1,...,xk,yk,ck],
        "score" : float,
     },
     ...
     // for persons in image_2
    {
        "image_id" : string, image_2_name,
        "category_id" : int, 1 for person
        "keypoints" : [x1,y1,c1,...,xk,yk,ck],
        "score" : float,
     },
     ...
    ]

    Order of the keypoints:
        {0,  "Nose"},
        {1,  "LEye"},
        {2,  "REye"},
        {3,  "LEar"},
        {4,  "REar"},
        {5,  "LShoulder"},
        {6,  "RShoulder"},
        {7,  "LElbow"},
        {8,  "RElbow"},
        {9,  "LWrist"},
        {10, "RWrist"},
        {11, "LHip"},
        {12, "RHip"},
        {13, "LKnee"},
        {14, "Rknee"},
        {15, "LAnkle"},
        {16, "RAnkle"},
    """
    def __init__(self,JsonFile):
        self.JF = JsonFile
        os.path.exists(self.JF)
        try:
            with open(self.JF) as f:
                self.data = json.load(f)
            self.keypoints = self.data[0]['keypoints'] # Change the 0 when multiple persons on the image
            self.confidence = self.data[0]['score']
        except:
            raise ValueError('Impossible to read the file '+ self.JF)

    # Extract the keypoints!
    def nose(self):
        return {'x':self.keypoints[0],'y':self.keypoints[1]}
    def ltshoulder(self):
        return {'x':self.keypoints[5*3],'y':self.keypoints[5*3+1]}
    def rtshoulder(self):
        return {'x':self.keypoints[6*3],'y':self.keypoints[6*3+1]}
    def ltankle(self):
        return {'x':self.keypoints[15*3],'y':self.keypoints[15*3+1]}
    def rtankle(self):
        return {'x':self.keypoints[16*3],'y':self.keypoints[16*3+1]}
    def relbow(self):
        return {'x':self.keypoints[8*3],'y':self.keypoints[8*3+1]}
    def lelbow(self):
        return {'x':self.keypoints[7*3],'y':self.keypoints[7*3+1]}
    def rwrist(self):
        return {'x':self.keypoints[10*3],'y':self.keypoints[10*3+1]}
    def lwrist(self):
        return {'x':self.keypoints[9*3],'y':self.keypoints[9*3+1]}
    def rhip(self):
        return {'x':self.keypoints[12*3],'y':self.keypoints[12*3+1]}
    def lhip(self):
        return {'x':self.keypoints[11*3],'y':self.keypoints[11*3+1]}
    def rknee(self):
        return {'x':self.keypoints[14*3],'y':self.keypoints[14*3+1]}
    def lknee(self):
        return {'x':self.keypoints[13*3],'y':self.keypoints[13*3+1]}

    def body_parts(self):
        """Give all the body parts in a list easier to read"""
        body = []
        body.append(self.nose())
        body.append(self.ltshoulder())
        body.append(self.rtshoulder())
        body.append(self.lelbow())
        body.append(self.relbow())
        body.append(self.lwrist())
        body.append(self.rwrist())
        body.append(self.lhip())
        body.append(self.rhip())
        body.append(self.lknee())
        body.append(self.rknee())
        body.append(self.ltankle())
        body.append(self.rtankle())
        return body

    def confidence_value(self):
        """Return the confidence value"""
        return self.confidence



def split_json(json_file="alphapose-results.json",PATH="./"):
    """
    Given:
    JsonFile – the json file containing all the keypoints detected by alphapose
    PATH – the path of the json file

    Return:
    Nothing, it creates a directory containing one json file per images that we gave to alphapose

    Abstract:
    SPLITJSON takes a json file as input and tansform it in multiple json files,
    one per image, that can be read by the other programs
    """


    data = 0
    DIR = "JsonFiles/"
    os.system('rm -r '+ DIR) # Delete the directory if existing
    os.system("mkdir "+DIR)

    try:
        with open(PATH+json_file) as f:
            data = json.load(f)
        for i in range(0,len(data)):
            temp_out = data[i]['image_id'].split('.')
            name_json_out = DIR+temp_out[0]+".json"
            data_json = [data[i]]
            with open(name_json_out, 'w') as outfile:
                json.dump(data_json, outfile)
    except:
        raise ValueError('Impossible to read the file '+ json_file)

def pixel_fall(J1,J2):
    """
    Given:
    J1,J2 – Two JsonReader objects

    Return:
    The distance between the two noses of the two persons represented by the json files

    Abstract:
    PIXELFALL takes two different JsonReader objects and return the pixel fall between the two jsonfiles
    """

    return abs(J1.nose()['y']-J2.nose()['y'])

def height_person(J1):
    """
    Given:
    J1 – JsonReader objects

    Return:
    the height of the person represented by the JsonReader object

    Abstract:
    HEIGHTPERSON returns the height of the person represented by the JsonReader object
    """

    return abs(J1.nose()['y']-J1.ltankle()['y'])
