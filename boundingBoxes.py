from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import functions
import constants
import untangle

def scaleNormalize(traceGroupBoundingBox, avgStrokeHeight, withAntialias, xmax, xmin, ymax, ymin):
    
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

    for traceGroup in traceGroupBoundingBox:
        traceGroupBoundingBox[traceGroup]['xmin'] = int((traceGroupBoundingBox[traceGroup]['xmin']-xmin)*horizontalNormalize) + horizontalPadding
        traceGroupBoundingBox[traceGroup]['xmax'] = int((traceGroupBoundingBox[traceGroup]['xmax']-xmin)*horizontalNormalize) + horizontalPadding

        traceGroupBoundingBox[traceGroup]['ymin'] = int((traceGroupBoundingBox[traceGroup]['ymin']-ymin)*verticalNormalize) + verticalPadding
        traceGroupBoundingBox[traceGroup]['ymax'] = int((traceGroupBoundingBox[traceGroup]['ymax']-ymin)*verticalNormalize) + verticalPadding

    return

def generateXmlWithAnnotations(forImage, pathToInkml):
    inkml = untangle.parse(pathToInkml)
    traceGroups = inkml.ink.traceGroup.traceGroup

    traceGroupBoundingBox = {}
    strokeIdToSymbolName = {}
    strokeIdToTraceGroup = {}
    traceGroupToSymbolName = {}

    for traceGroup in traceGroups:
            symbolName = traceGroup.annotation.cdata.strip('\\')
            traceGroupToSymbolName[traceGroup['xml:id']] = symbolName
            traceGroupBoundingBox[traceGroup['xml:id']] = {'xmin': float("inf"), 'xmax': -float("inf"), 'ymin': float("inf"), 'ymax': -float("inf")}
            try:
                if isinstance(traceGroup.traceView, list):
                    for elem in traceGroup.traceView:
                        strokeId = int(elem['traceDataRef'])
                        strokeIdToTraceGroup[strokeId] = traceGroup['xml:id']
                        strokeIdToSymbolName[strokeId] = symbolName
                else:
                    strokeId = int(traceGroup.traceView['traceDataRef'])
                    strokeIdToTraceGroup[strokeId] = traceGroup['xml:id']
                    strokeIdToSymbolName[strokeId] = symbolName
            except:
                print("Tracewarning on: " + forImage)
                del traceGroupBoundingBox[traceGroup['xml:id']]
                del traceGroupToSymbolName[traceGroup['xml:id']]

    if not any(traceGroupToSymbolName):
        print(pathToInkml)

    # Extract strokes and find bounding box of the expression
    xmin = float("inf")
    xmax = -float("inf")
    ymin = float("inf")
    ymax = -float("inf")

    strokeBoundingBox = {}
    strokeHeights = []

    for strokeEntry in inkml.ink.trace:
        strokeId = int(strokeEntry["id"])
        if strokeId in strokeIdToSymbolName:
            symbolName = strokeIdToSymbolName[strokeId]
            strokeBoundingBox[strokeId] = {'xmin': float("inf"), 'xmax': -float("inf"), 'ymin': float("inf"), 'ymax': -float("inf")}
            stroke = strokeEntry.cdata.replace("\n", "").split(",")
            for point in stroke:
                point = point.split()
                pointX = float(point[0])
                pointY = float(point[1])
                if pointX > strokeBoundingBox[strokeId]['xmax']:
                    strokeBoundingBox[strokeId]['xmax'] = pointX
                    if pointX > traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['xmax']:
                        traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['xmax'] = pointX
                        if(pointX > xmax): xmax = pointX
                if pointX < strokeBoundingBox[strokeId]['xmin']:
                    strokeBoundingBox[strokeId]['xmin'] = pointX
                    if pointX < traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['xmin']:
                        traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['xmin'] = pointX
                        if(pointX < xmin): xmin = pointX
                if pointY > strokeBoundingBox[strokeId]['ymax']:
                    strokeBoundingBox[strokeId]['ymax'] = pointY
                    if pointY > traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['ymax']:
                        traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['ymax'] = pointY
                        if(pointY > ymax): ymax = pointY
                if pointY < strokeBoundingBox[strokeId]['ymin']:
                    strokeBoundingBox[strokeId]['ymin'] = pointY
                    if pointY < traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['ymin']:
                        traceGroupBoundingBox[strokeIdToTraceGroup[strokeId]]['ymin'] = pointY
                        if(pointY < ymin): ymin = pointY

            strokeHeight = strokeBoundingBox[strokeId]['ymax'] - strokeBoundingBox[strokeId]['ymin']
            strokeWidth = strokeBoundingBox[strokeId]['xmax'] - strokeBoundingBox[strokeId]['xmin']
            # Avoid taking strokes into consideration which are mainly horizontal (like in "-", "=", '.', etc)
            if (strokeWidth < 2*strokeHeight) and (len(stroke) > 8):
                strokeHeights.append(strokeHeight)
        else:
            print("Warning on for image: " + forImage + " strokeId: " + str(strokeId))

    sortedHeights = sorted(strokeHeights)
    strokeHeightsLength = len(strokeHeights)

    # Filter out the strokes with the biggest/smallest height
    if strokeHeightsLength >= 2:
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

    scaleNormalize(traceGroupBoundingBox, avgStrokeHeight, False, xmax, xmin, ymax, ymin)

    annotation = Element('annotation')
    for traceGroup in traceGroupBoundingBox:

        xmin = traceGroupBoundingBox[traceGroup]['xmin']
        xmax = traceGroupBoundingBox[traceGroup]['xmax']
        ymin = traceGroupBoundingBox[traceGroup]['ymin']
        ymax = traceGroupBoundingBox[traceGroup]['ymax']

        height = ymax - ymin
        width = xmax - xmin

        # Add padding on bounding boxes to a minimal height / width of 16
        paddingH = 0
        paddingW = 0

        if (height < 16):
            paddingH = (16 - height) / 2 + (16 - height) % 2
        if (width < 16):
            paddingW = (16 - width) / 2 + (16 - width) % 2

        object = SubElement(annotation, 'object')

        name = SubElement(object, 'name')
        name.text = traceGroupToSymbolName[traceGroup]

        bndbox = SubElement(object, 'bndbox')
        xmin = SubElement(bndbox, 'xmin')
        xmin.text = str(max(traceGroupBoundingBox[traceGroup]['xmin'] - paddingW, 0))
        xmax = SubElement(bndbox, 'xmax')
        xmax.text = str(min(traceGroupBoundingBox[traceGroup]['xmax'] + paddingW, 1000))
        ymin = SubElement(bndbox, 'ymin')
        ymin.text = str(max(traceGroupBoundingBox[traceGroup]['ymin'] - paddingH, 0))
        ymax = SubElement(bndbox, 'ymax')
        ymax.text = str(min(traceGroupBoundingBox[traceGroup]['ymax'] + paddingH, 200))

    return prettify(annotation)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def generateBoundingBoxes(imageNameMapping):
    for imageName in imageNameMapping:
        print('Generating annotations for ' + imageName)
        xml = boundingboxes.generateXmlWithAnnotations(imageName, inkmlLocation[imageName])
        with open(str(constants.TARGET_PATH + "Annotations/" + imageName[5:10] + ".xml"), "w") as f:
            f.write(xml)
