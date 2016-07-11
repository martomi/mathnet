import csv
import constants

def saveDictToFile(dict, filename):
    w = csv.writer(open(filename, "w"), delimiter=" ")
    for key, val in sorted(dict.items()):
        w.writerow([key, val])
    return

def loadDictFromFile(fileName):
    dict = {}
    for key, val in csv.reader(open(fileName), delimiter=" "):
        dict[key] = val
    return dict

def indexToImageName(index):
    return "image" + str(index).zfill(5) + ".pbm"

def getFilePathsForDataset(datasetName):
    filePaths = []
    with open("datasets/" + datasetName + ".txt") as f:
        for line in f:
            if datasetName == "testGT":
                filePath = constants.TEST_PATH + line.rstrip("\n")
            else:
                filePath = constants.TRAIN_PATH + datasetName + "/" + line.rstrip("\n")
            filePaths.append(filePath)
    return filePaths

def getAllFilePaths():
    datasets = ["expressmatch", "extension", "HAMEX", "KAIST", "MathBrush", "MfrDB"]
    filePaths = []
    for dataset in datasets:
        filePaths += getFilePathsForDataset(dataset)
    return filePaths

def getAllFilePathsTestDataset():
    return getFilePathsForDataset("testGT")