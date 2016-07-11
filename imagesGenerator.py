from PIL import Image, ImageDraw, ImageFilter
import cv2
import numpy as np
import untangle
import functions
import constants

def scaleNormalize(strokes, avgStrokeHeight, withAntialias, xmax, xmin, ymax, ymin):

    # Normalize height and keep aspect ratio
    H = constants.get_MAX_H(withAntialias) - constants.get_LINE(withAntialias)
    W = H*(xmax-xmin)/(ymax-ymin)
    if W > constants.get_MAX_W(withAntialias):
        W = constants.get_MAX_W(withAntialias) - constants.get_LINE(withAntialias)
        H = W*(ymax-ymin)/(xmax-xmin)

    xNormalizeConstant = W/(xmax-xmin)
    yNormalizeConstant = H/(ymax-ymin)

    if avgStrokeHeight != 0:
        normalizedAvgStrokeHeight = avgStrokeHeight*yNormalizeConstant
    else:
        normalizedAvgStrokeHeight = 1
    if normalizedAvgStrokeHeight > constants.STROKE_HEIGHT:
        globalNormalizationConstant = constants.STROKE_HEIGHT/normalizedAvgStrokeHeight
    else:
        globalNormalizationConstant = 1

    horizontalPadding = int((constants.get_MAX_W(withAntialias) - W*globalNormalizationConstant)/2)
    verticalPadding = int((constants.get_MAX_H(withAntialias) - H*globalNormalizationConstant)/2)
    horizontalNormalize = xNormalizeConstant*globalNormalizationConstant
    verticalNormalize = yNormalizeConstant*globalNormalizationConstant

    for strokeId in strokes:
        scaledStroke = []
        for coordinates in strokes[strokeId]:
            coordinates[0] = int((coordinates[0]-xmin)*horizontalNormalize) + horizontalPadding
            coordinates[1] = int((coordinates[1]-ymin)*verticalNormalize) + verticalPadding
            scaledStroke.append(coordinates)
        strokes[strokeId] = scaledStroke
    return

def generateImage(src, dest, withAntialias=False):
    inkml = untangle.parse(src)
    traceGroups = inkml.ink.traceGroup.traceGroup

    # Extract strokes and find bounding box of the expression
    xmin = float("inf")
    xmax = -float("inf")
    ymin = float("inf")
    ymax = -float("inf")

    strokes = {}
    strokeBoundingBox = {}
    strokeHeights = []

    for strokeEntry in inkml.ink.trace:
        strokeId = int(strokeEntry["id"])
        strokes[strokeId] = []
        strokeBoundingBox[strokeId] = {'xmin': float("inf"), 'xmax': -float("inf"), 'ymin': float("inf"), 'ymax': -float("inf")}
        stroke = strokeEntry.cdata.replace("\n", "").split(",")
        for point in stroke:
            point = point.split()
            pointX = float(point[0])
            pointY = float(point[1])
            if pointX > strokeBoundingBox[strokeId]['xmax']:
                strokeBoundingBox[strokeId]['xmax'] = pointX
                if(pointX > xmax): xmax = pointX
            if pointX < strokeBoundingBox[strokeId]['xmin']:
                strokeBoundingBox[strokeId]['xmin'] = pointX
                if(pointX < xmin): xmin = pointX
            if pointY > strokeBoundingBox[strokeId]['ymax']:
                strokeBoundingBox[strokeId]['ymax'] = pointY
                if(pointY > ymax): ymax = pointY
            if pointY < strokeBoundingBox[strokeId]['ymin']:
                strokeBoundingBox[strokeId]['ymin'] = pointY
                if(pointY < ymin): ymin = pointY
            strokes[strokeId].append([pointX, pointY])
        strokeHeight = strokeBoundingBox[strokeId]['ymax'] - strokeBoundingBox[strokeId]['ymin']
        strokeWidth = strokeBoundingBox[strokeId]['xmax'] - strokeBoundingBox[strokeId]['xmin']
        # Avoid taking strokes into consideration which are mainly horizontal (like in "-", "=", '.', etc)
        if (strokeWidth < 2*strokeHeight) and (len(stroke) > 8):
            strokeHeights.append(strokeHeight)

    sortedHeights = sorted(strokeHeights)
    strokeHeightsLength = len(strokeHeights)

    if strokeHeightsLength >= 2:
        # Filter out the strokes with the biggest/smallest height
        if isinstance(traceGroups, list):
            strokeHeights = sortedHeights[int((1.0/5.0)*strokeHeightsLength):int((4.0/5.0)*strokeHeightsLength)]

    # Find the average stroke height
    if len(strokeHeights) > 0:
        sumOfStrokeHeights = 0
        for strokeHeight in strokeHeights:
            sumOfStrokeHeights += strokeHeight
        avgStrokeHeight = sumOfStrokeHeights/len(strokeHeights)
    else:
        avgStrokeHeight = 0

    scaleNormalize(strokes, avgStrokeHeight, withAntialias, xmax, xmin, ymax, ymin)

    # Draw lines & save image
    width, height = int(constants.get_MAX_W(withAntialias)), int(constants.get_MAX_H(withAntialias))  # picture's size
    img = np.zeros((height, width), np.uint8)
    for strokeId in strokes:
        pts = np.array(strokes[strokeId], dtype=np.int32)
        cv2.polylines(img, [pts], False, 255, thickness=2)
    cv2.imwrite(dest, img)

    return

def generateImages():
    filePaths = functions.getAllFilePaths()
    imageIndexToPath = {}
    counter = 0
    for filePath in filePaths:
        imageIndex = counter
        imageIndexToPath[imageIndex] = filePath
        print(filePath + " -> " + imageIndex)
        generateImage(filePath, str(constants.TARGET_PATH + "Images/" + imageIndex))
        counter += 1
    startOfTestDataset = counter
    filepaths = functions.getAllFilePathsTestDataset()
    for filePath in filePaths:
        imageIndex = counter
        imageIndexToPath[imageIndex] = filePath
        print(filePath + " -> " + imageIndex)
        generateImage(filePath, str(constants.TARGET_PATH + "Images/" + imageIndex))
        counter += 1

    functions.saveDictToFile(imageIndexToPath, str(constants.TARGET_PATH + "imageIndexToPath.txt"))
    print("Dataset generation complete!")
    return (imageIndexToPath, startOfTestDataset)