import symbolClasses
import imagesGenerator
import boundingBoxes

def main():
    print('Starting to process dataset.')
    symbolClasses.generateClassToColorMapping()
    imageNameMapping = imagesGenerator.generateImages()
    boundingBoxes.generateBoundingBoxes(imageNameMapping)
    print('All processes finished!');

if __name__ == "__main__":
    main()

