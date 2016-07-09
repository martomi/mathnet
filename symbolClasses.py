import untangle
import functions

def findAllClasses():
    filePaths = functions.getAllFilePaths()
    classes = {}

    for filePath in filePaths:
        inkml = untangle.parse(filePath)
        traceGroups = inkml.ink.traceGroup.traceGroup
        for traceGroup in traceGroups:
            symbol = traceGroup.annotation.cdata
            if symbol in classes:
                classes[symbol] += 1
            else:
                classes[symbol] = 1
    print(str(len(classes)) + " symbol classes found.")
    functions.saveDictToFile(symbolClasses, "classes.txt")
    return classes

def generateClassToColorMapping():
    classes = findAllClasses();
    color = 1
    for key, val in sorted(classes.items()):
        classes[key] = color
        color += 1
    functions.saveDictToFile(classes, "classColor.txt")
    return