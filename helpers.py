#Imports from python built-in modules
import random

#Imports from 3rd parties
import numpy as np

from torch      import manual_seed
from torch.cuda import manual_seed_all



def actual_bbox_string(box, width, length):
    """
        This function is taken from layoutlm repository. Put the box coordinates and image dimension into a known formatted string

        Parameters:
            box     : list
                The coordinates of the box
            width   : int
                The width of the image
            length  : int
                The length of the image
        
        Return
            string
                The formatted string containing box coordiantes and the width and length of the image
    """
    return (
        str(box[0])
        + " "
        + str(box[1])
        + " "
        + str(box[2])
        + " "
        + str(box[3])
        + "\t"
        + str(width)
        + " "
        + str(length)
    )

def bbox_string(box, width, length):
    """
        This function is taken from layoutlm repository. Convert the absolute coordinates of the box into relative coordinate to the image dimension

        Parameters:
            box     : list
                The coordinates of the box
            width   : int
                The width of the image
            length  : int
                The length of the image
        
        Return
            string
                The formatted string containing relative box coordiantes
    """
    return (
        str(int(1000 * (box[0] / width)))
        + " "
        + str(int(1000 * (box[1] / length)))
        + " "
        + str(int(1000 * (box[2] / width)))
        + " "
        + str(int(1000 * (box[3] / length)))
    )

def get_labels(path):
    """
        Put all the possible labels from the labels file into a list

        Parameters:
            path : string
                Path to the file containing all possible labels
        
        Return
            list
                List containing all the possible labels
    """

    with open(path, "r") as f:
        labels = f.read().splitlines()
    if "O" not in labels:
        labels = ["O"] + labels
    return labels

def set_seed(args):
    """
        Set the random seed to ensure reproducible result for the random generator of python, numpy, pytorch, and cuda

        Parameters:
            args : int
                Random seed to set
    """
    random.seed(args)
    np.random.seed(args)
    manual_seed(args)
    manual_seed_all(args)