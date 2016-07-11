import symbolClasses
import imagesGenerator
import boundingBoxes
import rcnnSplit

def main():
    print('Starting to process dataset.')
    symbolClasses.generateClassToColorMapping()
    (imageIndexToPath, startOfTestDataset) = imagesGenerator.generateImages()
    boundingBoxes.generateBoundingBoxes(imageIndexToPath)
    rcnnSplit.generateSplit(imageIndexToPath, startOfTestDataset)
    print('All processes finished!');

if __name__ == "__main__":
    main()

