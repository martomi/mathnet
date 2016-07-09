# Configuration constants
DATASETS_PATH = "datasets/CROHME2013_data/" # Make sure to download and place CROHME2013 dataset in that folder
TRAIN_PATH = DATASETS_PATH + "TrainINKML/"
TEST_PATH = DATASETS_PATH + "TestINKMLGT/"
TARGET_PATH = "datasets/mathnet/"
ANTIALIAS_FACTOR = 2
STROKE_HEIGHT = 25 * ANTIALIAS_FACTOR
MAX_H = 200.0
MAX_W = 1000.0
LINE = 3

# Do not modify
def get_MAX_H(antialias):
    if antialias:
        return MAX_H * ANTIALIAS_FACTOR
    return MAX_H

def get_MAX_W(antialias):
    if antialias:
        return MAX_W * ANTIALIAS_FACTOR
    return MAX_W

def get_LINE(antialias):
    if antialias:
        return LINE * ANTIALIAS_FACTOR
    return LINE