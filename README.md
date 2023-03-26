# ComputerVisionProject
Application for recognizing and classifying Sockets Type

All of our code is written in Python. The only libraries we used are cv2, numpy and math.
For the user interface we used tkinter.

The main steps:
1. resize the image.
2. recognize the object (the socket) and blank the wall behind.
3. find a threshold that marks the holes of the socket and erases noises on the sockets (such as shading etc).
4. for each hole detected, crop the hole from the original image.
5. for each cropped hole classify whether it is a circle or a rectangle.
6. given the set of circles and rectangles of one socket, find the relations between the holes and classify the type of the socket.
