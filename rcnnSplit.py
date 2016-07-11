import random
import constants
import functions

def generateSplit(imageIndexToPath, startOfTestDataset):
	with open(str(constants.TARGET_PATH + 'rcnn-split/trainval.txt'), 'w') as trainval, 
	open(str(constants.TARGET_PATH + 'rcnn-split/test.txt'), 'w') as test:
		for imageIndex in imageIndexToPath:
			if imageIndex < startOfTestDataset:
				trainval.write(str(imageIndex).zfill(5) + '\n')
			else:
				test.write(str(imageIndex).zfill(5) + '\n')
