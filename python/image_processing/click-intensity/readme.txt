ClickIntensity
By Ziqing Ye @ Trcek lab

See detailed instuctions in the pdf in this repository, or via this link: https://1drv.ms/b/s!AkQWSMjJWJr1gophVl1ftyjxgOau7g?e=H07dcE

Overview:
The program is used to record average pixel intensity data in target regions of interest. Here’s a brief summary of what it does: 
a.	You open the program and the image that you want to analyze opens up.
b.	You left click somewhere on the image
c.	A circle with a customized radius is generated there. It has a number on it.
a)	While the program is running, you can change the display brightness, zoom in and out, as well as adjust the radius of your circle
d.	The average* pixel intensity within that circle is calculated.
e.	This intensity information is saved into an excel spreadsheet
f.	You click somewhere else, and step b-e are repeated.
g.	Once you are done, you press esc to close the image.
h.	When you close it, the image with all those circles is saved to your folder for future reference， along with an excel spreadsheet that stores all of the pixel intensity data.
Some notable features:
1.	Can easily adjust the display brightness for seeing dimmer signals without causing fluctuations in the recorded intensity data
2.	Can freely adjust the radius of circular ROIs (region of interest) depending on the sample conditions
3.	Can zoom in and out and recenter while making accurate ROI selections.


Relevance & usage:
A tool to aid fluorescent image analysis. User open the image to be analysed using this application, and
then they will able to generate circular ROIs (region of interest) on the desired parts of the image, each with a single click.
The average pixel intensity within those ROIs will be automatically computed and wrote to an excel spreadsheet. Overall, this
is much easier compared to the traditional process in ImageJ which requires users to manually drag and create every single circle.
ClickIntensity V4 also allows users to adjust ROI radii, adjust display brightness, and zooming in/out.

Small note: I wrote this as an experimental project in Trcek Lab @ Johns Hopkins University. Dr. Tatjana Trcek suggested
some of its core features and enhancement features.
Personally, in the development process, I was also motivated by my own personal experiences with ImageJ and fluorescent
image analysis when I was a summer intern at Bradham Lab @ Boston University. Basically, knowing the cumbersomeness of the ROI-based
image analysis from my experience at Bradham lab makes me more motivated in pursuing this project, and guides a few of the 
design choices (e.g. the labeling of image and pair mode).
