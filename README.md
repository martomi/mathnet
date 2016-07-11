# mathnet

1. Download CROHME 2013 dataset and place it in the datasets folder
2. Execute the main.py script. (python main.py)
3. Once the script is finished the converted dataset is available in the output folder
4. Clone the py-faster-rcnn repository (mathnet branch) https://github.com/martomi/py-faster-rcnn/tree/mathnet
5. Follow the instruction there to set it up
6. Link the files produced by script above as follows:
```py-faster-rcnn/data/mathnet/data/Annotations
py-faster-rcnn/data/mathnet/data/Images
py-faster-rcnn/data/mathnet/data/rcnn-split/test.txt
py-faster-rcnn/data/mathnet/data/rcnn-split/trainval.txt```
7. Now you should be able to train the network on the CROHME dataset
