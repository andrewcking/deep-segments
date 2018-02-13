# DeepSegments
DeepSegments is a tool for generating ground-truth segmentations for use in deep learning segmentation models. It provides a simple method for researchers to quickly segment their datasets. Users can choose from a two different segmentation methods, SLIC or graph cuts. The program will make label suggestions by propagating user-given labels to unlabeled portions. Label suggestions can be given by an unsupervised k-means algorithm or a user-supplied pre-trained model.

![DeepSegments Screenshot](http://andrewking.io/wp-content/uploads/2017/09/deep-segments-screenshot.jpg)

## Download
You can download versions of DeepSegments for mac and windows at the following link:

[DeepSegments Download](http://andrewking.io/#/portfolio/deep-segments/)


## Usage Instructions
After running the executable you can set your dataset classes by clicking on the class labels button. Enter one class per line. Load your image using the load button. The image will appear in the window. Use scroll wheel (two finger scroll on mac) to zoom in and out or use the buttons. Next select your annotation suggestion mode (use manual if you do not want annotation suggestions) and your segmentation method (SLIC or graph cuts). Finally press the segment button. The segment button will blink while the segmentation is running. 

Large images can take a couple minutes, you may want to consider downsizing your photos and then upscaling your segmentation images later. After the segmentation takes place select a label class from the list at the bottom. Right click on a segment in the image to color it. 

Annotation suggestions are shown as filled circles in a segment. It is important to note that these suggestions affect the segmentation image. In other words, if you have incorrect suggestions in the image and you save the segmentation image out, you will have incorrectly labeled segments. This also means that you do not need to fill the suggestion segments if the suggestions are correct.

Also note that you can switch back and forth between unsupervised and manual mode if you want label suggestions to stop propagating.

To save a segmentation image press the save button. The image will be automatically saved to the same folder your image was loaded from with the suffix, '_mask'.

You can toggle the segmentation overlay with the 'Toggle Segment' button and you can change the number of segments using the 'Number of Segs' input field. Note that this is exact for SLIC and approximate for graph cuts.


## Dependencies
The project was built with the following. In all likelihood it will still work with newer versions but no guarantees. I would advise that you use the listed version of TK due to some compatability issues with the latest version of Mac OS.

Python 3.5

Numpy 1.121

OpenCV 3.1

Scikit-image 0.13

Scikit-learn 0.18.1

Pyinstaller 3.2.1

tk 8.5.19
