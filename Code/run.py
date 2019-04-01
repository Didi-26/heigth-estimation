"""
This file runs everything
"""

import argparse
import warnings
import numpy as np
from decimal import Decimal
from CenterMassTrajectory import trajectory
from Video2Photos import video_2_photo
from jsonfilereader import JsonReader, split_json, pixel_fall, height_person
from Position import compute_positions
from Acceleration import compute_acceleration_floor_method, compute_acceleration_minimum_method, compute_acceleration_diff, compute_curve
from helper import *


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--video",help="path to the image file")
    ap.add_argument("-j","--json",help="nameofjson or 0 if the json was already created or not")
    ap.add_argument("-c","--cv", help="Use opencv to compute the correction term. Default is not.")
    ap.add_argument("-o","--output", help="Show the points on the images when computing the correction term with opencv. Default is not.")
    ap.add_argument("-r","--randsac", help="Specify the number of iterations of randsac to use (a good value is 20000). Default is 0.")
    ap.add_argument("-v","--verbose",help="Secify if the output should be verbose or not. Default is not verbose.")
    ap.add_argument("-p","--jump",help="Specify the jump number (starting from 0). Default is 0. Note that you need to be sure that the jump exists otherwise the code will crash.")
    ap.add_argument("-n","--correction",help="Select the type of person you are examinating. 0 is for adults, 1 is for children, 2 is for all.")
    ap.add_argument("-s","--ratio",help="Specify the true ratio so that it can be compared to the one computed by the algorithm.")
    ap.add_argument("-w","--height",help="Specify the size of the subject in cm")
    ap.add_argument("-m","--method",help="Select which method you want to compute the height of the person. 0 is for the floor method, 1 is for the minimum method and 2 is for the difference method (default is the floor method) ")
    ap.add_argument("-y","--fps",help="Select the number of frame per second of your video (Default is 30 FPS). It must be an int.")
    ap.add_argument("-l","--matplotlib",help="Choose if you want to use matplotlib library or not. 1 is for using it and 0 is for not using it. Defautl is 1.")
    ap.add_argument("-t","--range",help="Specify the range for estimating the size of the person in pixel. Must have the format 'x,y', x<y. Default is '0,100'.")

    args = vars(ap.parse_args())


    # Definition of all the default values of the program
    randsac = 0 # Number of iterations for randsac
    jump = 0 # Jump number
    polynomial_fit = 0 #
    index_floor_before_jump = 0
    index_floor_after_jump = 0
    max_interval = 0
    frame_size = 1/30
    correction_factor = 1.16957678819
    correction_factor_choose = 0
    real_ratio = 0 # The real ratio for centimenters to pixel
    real_height = 0 # The real height in centimeters
    g = 9.81 # Gravity
    verbose = 0 # The code will not give all the print and will only return the final value
    output = 0
    method = 0 # The method used to compute the ratio centimeters/pixels
    matplot_use = 1
    range_size = range(0,100)
    index_fly = 0
    good_values = 0


    """ Argument parser """

    if (not args["video"] and args["json"] == "0"):
        ap.error("Not enough arguments: --video is required")
    #if (args["json"] != "1" and args["json"] != "0"):
    #    ap.error("You must either type 1 or 0 for the argument --json")
    if (args["video"] and args["json"] != "0"):
        warnings.warn("Warning: you used the argument --video and --json together. The first one will be ignored!")
    if (args["cv"] != None and args["cv"] != "1" and args["cv"] != "0"):
        warnings.warn("Warning: you must either type 1 or 0 for the argument --cv. The default will be used")
        args["cv"] = "0"
    if (args["cv"] == "0" and args["output"] == "1"):
        warnings.warn("Warning: you used the argument --cv equal to 0 and the argument --output == 1 together. The second one will have no effect!")
    if (args["cv"] == "1" and args["correction"] != None):
        warnings.warn("Warning: you used the argument --cv equal to 1 and the argument --correction != 0 together. The second one will have no effect!")
    if (args["output"] != None and args["output"] != "1" and args["output"] != "0"):
        warnings.warn("Warning: you must either type 1 or 0 for the argument --output. The default will be used")
        args["output"] = "0"
    if (args["randsac"] != None):
        try:
            randsac = int(args["randsac"])
        except:
            print("You didn't use an integer for the argument --randsac. RANDSAC will not be used.")
    if (args["output"] != None):
        try:
            output = int(args["output"])
        except:
            print("You didn't use an integer for the argument --output. The intermediate results will not be shown.")
    if (args["verbose"] != None):
        try:
            verbose = int(args["verbose"])
        except:
            print("You didn't use an integer for the argument --verbose. The output will not be verbose.")
    if (args["jump"] != None):
        try:
            jump = int(args["jump"])
        except:
            print("You didn't use an integer for the argument --jump. The first jump will be used.")
    if (args["correction"] != None):
        try:
            correction_factor_choose = int(args["correction"])
            if (correction_factor_choose != 0 and correction_factor_choose != 1 and correction_factor_choose != 2):
                print("You needed to specify either 0, 1, or 2 for the argument --correction. The correction ratio for the adults will be used.")
        except:
            print("You didn't use an integer for the argument --correction. The correction ratio for the adults will be used.")


    if (args["ratio"] != None):
        try:
            real_ratio = float(args["ratio"])
        except:

            print("You didn't use a float for the argument --ratio. This ratio will be ignore.")
    if (args["height"] != None):
        try:
            real_height = int(args["height"])
        except:
            print("You didn't use an integer for the argument --height. The height will be ignore and the error will not be calculated.")
    if (args["method"] != None):
        try:
            method = int(args["method"])
        except:
            print("You didn't use an integer for the argument --acceleration. The acceleration method will be use as default.")
    if (args["fps"] != None):
        try:
            frame_size = 1/int(args["fps"])
        except:
            print("You didn't use an integer for the argument --fps. The FPS will be set to 30.")
    if (args["matplotlib"] != None):
        try:
            matplot_use = int(args["matplotlib"])
        except:
            print("You didn't use an integer for the argument --matplotlib. Matplotlib library will be used.")
    if (args["range"] != None):
        try:
            range_size = range(int(args["range"].split(",")[0]),int(args["range"].split(",")[1]))
        except:
            print("You didn't use the correct for the argument --range. Default value will be used.")

    vprint = print if verbose else lambda *a, **k: None # Refining the print function


    """ Estimation of the size """

    name_video = args["video"]
    """ The json file was not already generated using Alphapose we prepare the images for alphapose"""
    if (args["json"] == '0'):
        vprint("Creating the photos from the video \n")
        video_2_photo(name_video)
        vprint("Done \n")
        print("Please generate the json file with alphapose and rerun the code with --json nameofjsonfile instead of --json 0")

    else:
        """ The json file was already generated using Alphapose we can compute the height"""
        vprint("Decomposition of the json file into multiple json files in the directory Jsonfiles \n")
        split_json(args["json"]) # We call it with the default argument, see jsonfilereader

        vprint("Decomposition done successfuly \n")

        vprint("Computing the trajectory of the person from the json files and saved in the directory Trajectory \n")
        trajectory() # Compute the trajectory of the person

        vprint("Computing the trajectory done successfully \n")


        vprint("Computing the different arrays for the rest of the program \n")
        position_center_mass_x,position_center_mass_y, position_nose, position_foot_L, position_foot_R, mean_position_bottom, size_person = compute_positions()

        file_cm = open("CMPosition.txt","w") # Save the center of mass for later use
        for cc in position_center_mass_y:
            file_cm.write(str(cc))
            file_cm.write(" ")
        file_cm.close()

        vprint("The different arrays are ready \n")



        vprint("Computing the acceleration in pixels \n")
        if (method == 0):
            index_fly,good_values = compute_acceleration_floor_method(-position_center_mass_y,jump)

        elif (method == 1):
            index_fly,good_values = compute_acceleration_minimum_method(-position_center_mass_y,randsac,jump)

        else:
            max_interval,index_floor_before_jump,index_floor_after_jump= compute_acceleration_diff(-position_center_mass_y,0,jump)

        if (method == 0 or method == 1):
            if (randsac):
                vprint("Using randsac \n")
                polynomial_fit= compute_curve(-position_center_mass_y,index_fly,good_values,randsac)
            else:
                polynomial_fit = compute_curve(-position_center_mass_y,index_fly,good_values,0)

        if (args["cv"] == "1"):
            from ComputeRatioFile import compute_median_ratio
            vprint("Computing the correction term")

            correction_factor = compute_median_ratio(output)
            vprint("Computing the correction term done successfuly \n")
        else:

            vprint("Using the precomputed correction term \n")
            if (correction_factor_choose == 1):
                correction_factor = 1.2234304709 #children
            elif (correction_factor_choose == 2):
                correction_factor = 1.18160518463 #all
        # Add a parameter to select the range for computing the size in pixel
        size_in_pixel_before_correction = np.median(size_person[range_size])
        size_in_pixel = size_in_pixel_before_correction*correction_factor

        if (method == 0 or method == 1):
            computed_ratio = np.median((1/2)*g/abs(polynomial_fit[0]/(frame_size**2)))

        else:
            time_flight_after = frame_size*(abs(index_floor_after_jump-max_interval))
            fall_meter_after = (1/2)*g*pow(time_flight_after,2) #Height of the fall in meters
            fall_pixel_after = (abs(position_center_mass_y[max_interval]-position_center_mass_y[index_floor_after_jump]))
            computed_ratio = fall_meter_after*(1/fall_pixel_after)

        # Display the curve of acceleration

        if (real_ratio != 0):
            print("Real ratio: " +str(real_ratio))
            print("The difference between the ratios is "+str(round(100*abs(real_ratio-computed_ratio)/real_ratio,2))+" %") # Uncomment if you want to compute the have relative error of the ratio cm/px
        size_m = computed_ratio*size_in_pixel

        vprint("Computing the acceleration in pixel done successfuly \n")


        estimated_height_cm = round(size_m,4)*100

        if (matplot_use and (method== 0 or method == 1)):
            import matplotlib.pyplot as plt
            plt.scatter(range(len(position_center_mass_y)),1080-position_center_mass_y,s=1,label="Trajectory")
            plot_index = np.linspace(index_fly[0],index_fly[-1],1000)

            poly_f = np.polyval(polynomial_fit,plot_index)
            plt.plot(plot_index,1080+poly_f,color="orange",label="polynomial fit")
            plt.legend()
            plt.title("Trajectory and polynomial fit")
            plt.show()

        print("The height of the person is: "+str(estimated_height_cm)+" centimeters")

        if (real_height != 0):
            print("The difference between the sizes is "+str(((real_height-estimated_height_cm))))
            print("The difference between the sizes is "+str(round(100*abs(real_height-estimated_height_cm)/real_height,2))+" %")

        # more info in verbose

if (__name__ == "__main__"):
    main()
