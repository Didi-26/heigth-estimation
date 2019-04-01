"""
This file is useful to compute the acceleration of the person
"""
import numpy as np
import scipy.signal
import scipy.ndimage.filters
from randsacpolyfit import polyrandsac



def compute_acceleration_floor_method(position,jump_number=0):
    """
        Compute the acceleration in pixel of the person given the position, the number of points per frame interval and the jump number (which jump it is)
        This function uses the floor as a reference.
    """
    """ First find the indices that are not good due to a mistake with alphapose"""
    confidences = []
    with open("Trajectory/Confidences.txt") as file:
        for line in file:
            confidences.append(float(line))
    confidences = np.array(confidences)
    good_values = np.where(confidences >2)
    outliers = np.where(confidences <=2)

    index_floor_before_jump = 0
    index_floor_after_jump = 0

    # Keep only the indices that are correctly detected with Alphapose
    indices_kept_pos = []
    for index1 in range(0,len(position)):
        for index2 in good_values[0]:
            if index1==index2:
                indices_kept_pos.append(index1)

    """ Select the range 0:30 floor the floor position and find the maximum in the trajectory
     Compute the distance from floor to maximum """
    indices_values = 30
    floor = np.median(position[0:indices_values][np.where(np.array(indices_kept_pos)<indices_values)])

    total_max_index = scipy.signal.argrelmax(position[indices_kept_pos],order = len(position))[0] # Global maxium

    total_max_value = position[total_max_index]
    distance_floor_max = abs(total_max_value-floor)

    """ The threshold is useful to select the floor indices even if there is noise"""
    threshold = 0.15*distance_floor_max
    index_floor = np.where((position > floor-threshold) & (position < floor+threshold))[0]

    position[index_floor] = floor

    jump_positions = scipy.signal.argrelmax(position[indices_kept_pos],order = 10)[0]
    min_positions = scipy.signal.argrelmax(-position[indices_kept_pos],order = 10)[0]


    # We also need to remove the points that are not height enough (false true)
    index_to_delete = np.where(position[jump_positions] < floor+threshold*2)
    jump_positions = np.delete(jump_positions,index_to_delete) # remove the indices of the values that were wrongly detected

    # We have the maxima. Now we need to compute the values for the jump
    air_fly_time = np.where(position > floor)
    # First we get the index of the first element on the floor and take the next one, same for after the jump
    index_floor_before_jump = index_floor[np.where(index_floor < jump_positions[jump_number])][-1] +1
    index_floor_after_jump = index_floor[np.where(index_floor > jump_positions[jump_number])][0] -1

    # We can now fit a polynom of degree two to the curve.
    index_fly = range(index_floor_before_jump,index_floor_after_jump+1)

    return index_fly,good_values

def compute_curve(position,index_fly,good_values,RANDSAC):

    # Compute the polynom

    # In this case we will only keep the position detected by alphapose that are sufficiently well-detected.
    indices_kept = []
    for index1 in index_fly:
        for index2 in good_values[0]:
            if index1==index2:
                indices_kept.append(index1)

    # Polynomial fit with or without randsac
    if (RANDSAC):
        polynomial_fit = polyrandsac(indices_kept,position[indices_kept],int(len(position[indices_kept])-3),RANDSAC,degree = 2)
    else:
        polynomial_fit = np.polyfit(indices_kept,position[indices_kept],2)

    return polynomial_fit#index_floor_before_jump,index_floor_after_jump

def compute_acceleration_minimum_method(position,RANDSAC=0,jump_number=0):
    """
        Compute the acceleration in pixel of the person given the position, the number of points per frame interval and the jump number (which jump it is)
        This function uses the minimum of the trajectory
    """
    """ First find the indices that are not good due to a mistake with alphapose"""
    confidences = []
    with open("Trajectory/Confidences.txt") as file:
        for line in file:
            confidences.append(float(line))
    confidences = np.array(confidences)
    good_values = np.where(confidences >2)
    outliers = np.where(confidences <=2)

    index_floor_before_jump = 0
    index_floor_after_jump = 0

    # Keep only the indices that are correctly detected with Alphapose
    indices_kept_pos = []
    for index1 in range(0,len(position)):
        for index2 in good_values[0]:
            if index1==index2:
                indices_kept_pos.append(index1)

    #Select the range 0:30 floor the floor position
    indices_values = 30
    floor = np.median(position[0:indices_values][np.where(np.array(indices_kept_pos)<indices_values)])

    total_max_index = scipy.signal.argrelmax(position[indices_kept_pos],order = len(position))[0] # Global maxium


    max_min_triples = []
    positions_good = position
    maxima = scipy.signal.argrelmax(positions_good,order = 10)[0]
    minima = scipy.signal.argrelmax(-positions_good,order = 5, mode= "wrap")[0]

    # Select the triplets [index before jump,maximum,index after jump]
    for ma in maxima:
        if ma > minima[0]:
            indexLastBefore = minima[np.where(minima<ma)[0][-1]]
            if ma < minima[-1]:
                index_first_after = minima[np.where(minima>ma)[0][0]]
                max_min_triples.append([indexLastBefore, ma, index_first_after])

    heights = [min((positions_good[ma]-positions_good[l]), (positions_good[ma]-positions_good[r])) for l,ma,r in max_min_triples]
    max_height = max(heights)
    max_min_triples = np.array(max_min_triples)

    # Remove too small jumps
    minimal_relative_jump_height = 0.5
    flight_phase_ratio = 0.5
    high_jump_indices = np.where(heights > max_height*minimal_relative_jump_height)[0]
    high_jump_triples = max_min_triples[high_jump_indices]

    left, max_peak, right = high_jump_triples[jump_number]

    height = max(abs(positions_good[max_peak]-positions_good[left]), abs(positions_good[max_peak]-positions_good[right]))
    height_treshold = positions_good[max_peak] - flight_phase_ratio*height

    # Get the frames range that respect the different thresholds
    candidate_frames = np.where(positions_good[range(left, right)] > height_treshold)[0]

    index_floor_before_jump, index_floor_after_jump = left+candidate_frames[0], left+candidate_frames[-1]



    # We get the fly indices
    index_fly = range(index_floor_before_jump,index_floor_after_jump+1)

    return index_fly,good_values



def compute_acceleration_diff(position,RANDSAC=0,jump_number=0):
    """
        Compute the acceleration in pixel of the person given the position, the number of points per frame interval and the jump number (which jump it is)
    """
    """ First find the indices that are not good due to a mistake with alphapose"""

    confidences = []
    with open("Trajectory/Confidences.txt") as file:
        for line in file:
            confidences.append(float(line))
    confidences = np.array(confidences)
    good_values = np.where(confidences >2)
    outliers = np.where(confidences <=2)

    index_floor_before_jump = 0
    index_floor_after_jump = 0

    indices_kept_pos = []
    for index1 in range(0,len(position)):
        for index2 in good_values[0]:
            if index1==index2:
                indices_kept_pos.append(index1)

    # Find the floor value and compute the indices of the floor
    indices_values = 100
    floor = np.median(position[0:indices_values][np.where(np.array(indices_kept_pos)<indices_values)])

    total_max_index = scipy.signal.argrelmax(position[indices_kept_pos],order = len(position))[0] # Global maxium


    total_max_value = position[total_max_index]
    distance_floor_max = abs(total_max_value-floor)

    # Create a threshold based on the distance from floor to maximum to remove "jumps" that are only noise
    threshold = 0.15*distance_floor_max
    index_floor = np.where((position > floor-threshold) & (position < floor+threshold))[0]

    position[index_floor] = floor


    jump_positions = scipy.signal.argrelmax(position[indices_kept_pos],order = 10)[0] # This is the position of the jumps
    min_positions = scipy.signal.argrelmax(-position[indices_kept_pos],order = 10)[0]

    # We also need to remove the points that are not height enough (false true)
    index_to_delete = np.where(position[jump_positions] < floor+threshold*2)
    jump_positions = np.delete(jump_positions,index_to_delete) # remove the indices of the values that were wrongly detected

    # We have the maxima. Now we need to compute the values for the jump
    air_fly_time = np.where(position > floor)

    # First we get the index of the first element on the floor and take the next one, same for after the jump
    index_floor_before_jump = index_floor[np.where(index_floor < jump_positions[jump_number])][-1] +1
    index_floor_after_jump = index_floor[np.where(index_floor > jump_positions[jump_number])][0] -1

    index_fly = range(index_floor_before_jump,index_floor_after_jump+1)

    indices_kept = []
    for index1 in index_fly:
        for index2 in good_values[0]:
            if index1==index2:
                indices_kept.append(index1)

    # Return the good interval
    max_interval = jump_positions[jump_number]


    return max_interval, index_floor_before_jump,index_floor_after_jump
