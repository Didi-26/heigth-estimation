import numpy as np
from tqdm import tqdm

def polyrandsac(indices,data,min_datapoints,max_iter,degree = 2):
    """
    source : https://en.wikipedia.org/wiki/Random_sample_consensus
    Given:
    indices – the indices corresponding to the data
    data – a set of observations
    min_datapoints – minimum number of data points required to estimate model parameters
    max_iter – maximum number of iterations allowed in the algorithm
    degree – degree of the polynomial we want to fit

    Return:
    best_fit – model parameters which best fit the data (or null if no good model is found)
    """

    indices = np.array(indices)

    best_fit = 0
    best_err = np.inf

    for iterations in tqdm(range(max_iter)):
        temp = np.arange(len(indices))
        np.random.shuffle(temp)
        maybe_inliners = temp[:min_datapoints]#np.random.randint(len(x),size=n)##
        maybe_model = np.polyfit(indices[maybe_inliners],data[maybe_inliners],degree)

        current_err = np.sum(np.abs(np.polyval(maybe_model, indices[maybe_inliners])-data[maybe_inliners]))
        if (current_err < best_err):
                best_fit =  maybe_model
                best_err = current_err

    return best_fit
