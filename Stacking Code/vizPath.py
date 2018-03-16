#this program vizualizes a json file created by the inventory cameras
from tkinter import *
import json
import time
import string
import sys
import math

sdebug = 0 #script debug make 1 to enable debug console prints, 0 otherwise
gdebug = 1 #game debug make 
startTime = time.time() 


#######################
###### debug code #####
#######################

# db is a debut print statement that we can turn off when the code is good
def db(text):
	#debug function
	if sdebug:
		print(text)

def gdb(text):
	#game debug function
	if gdebug:
		print(text)

#########################
### database handling ###
#########################
# we import the sql database, parse it, and sort it

#####################
def removeNonJson(inputString):
	#this function removes leading c style comments and other bs
	#also fixes the non string nulls from the database
	gdb("Fixing json file....")
	returnString =""
	dataStart = 0;
	dataLength = len(inputString)
	db("in removeNonJson!")
	db(dataLength)
	for i in range(dataLength):
		db(inputString[i])
		if (inputString[i]=="[") or (inputString[i]=="{"):
			dataStart = 1
		if dataStart:
			#check if unquoted null
			#first check if near EOF
			if ((i+4)<dataLength) and (i > 4):
				nextFour = inputString[i:i+4]
				lastFour = inputString[i-4:i]
				db(nextFour)
				if (nextFour == "null") or (lastFour == "null"):
					returnString += "\""	
			returnString += inputString[i]
	gdb("done!")
	return returnString

#######################	

fileOptions = ["stackingData.json","inventry_location.json","med_length_debug.json","vizTestData.json"]	
dataFile = fileOptions[0] #enables rapid switching of input files for debug 
#if sdebug:
#	dataFile = "vizTestData.json"

jsonData=open(dataFile,"r")

##here we need to parse the txt file so that it only has the list of dicts from json

#1 remove leading characters before start of the json
#2 put all nulls in quotes 
jsonData = removeNonJson(jsonData.read())
db(" ")
db(" ")
db(jsonData)

listOfDicts = json.loads(jsonData) #using json.loads becayse jsonData is already a string

if sdebug:
	for obj in listOfDicts:
		#db(obj)
		db(obj["c_ts"])

fixTime = time.time()-startTime


##################################################################
############ DATA PARSING CODE BELOW #############################
##################################################################
#Code in this section will parse the list of dictionaries
#and extract data about specific parts/ markers

#here we are going to create a list of markers and then for each marker in 
#out list we are going to create the marker history for them
gdb("Parsing Data....")
markers = []
markerHistories = []
class markerHistory(object):
	def __init__(self):
		self.init()
	
	def init(self):
		self.timeStamps = []
		self.timeStampIndex = 0 #index of most recently used timeStamp in viz
		self.xValues = []
		self.yValues = []
		self.zValues = []
		self.observationCount = 0
		self.name = "empty name"
		self.entries = 0

	def printMyData(self):
		print("-----------------------------------------------------")
		print("timeStamp                 xValues   yValues   zValues")
		print(" ")
		for i in range(self.observationCount):
			print(self.timeStamps[i]," ",self.xValues[i]," ",self.yValues[i]," ",self.zValues[i],"         marker_id = ",self.name)

for obj in listOfDicts:
	if obj["m_id"] not in markers:
		markers.append(obj["m_id"])
		
for item in markers:
	db(item)
	newMarkerHistory = markerHistory()
	newMarkerHistory.name = item
	markerHistories.append(newMarkerHistory)
	
def fillValues(names,structs):
	#this function takes a list of marker IDs and fills out the 
	#data associated with them
	
	#loop through the objects in list of dicts and prepare the data for display

	for obj in listOfDicts:
		markerName = obj["m_id"]
		index = names.index(markerName)
		activeH = structs[index] #activeH ~ active History: which history we modify
		if activeH.name != markerName:
			print("DATABASE ERROR")
			raise ValueError('the name of the obj class did not meet the associated name') #throw error. This should never happen.
		#here we add the co-ordinates to the co-ordinate file
		#and convert them to floats to avoid problems later
		activeH.xValues.append(float(obj["w_x"])) 
		activeH.yValues.append(float(obj["w_y"]))  
		activeH.zValues.append(float(obj["w_z"])) 
		activeH.timeStamps.append(obj["p_ts"]) 
		activeH.observationCount += 1 #we added another observation. Value may be helpful in the future
		structs[index] = activeH #put our thing back where we got it
	
	for history in markerHistories:
		history.entries = len(history.timeStamps)

#now lets fill in all those values!!

fillValues(markers,markerHistories)	


parseTime = time.time()-fixTime-startTime


if gdebug:
	for historyIndex in range(len(markerHistories)):
		history = markerHistories[historyIndex]
		print(" ")
		print("Marker ID = ",markers[historyIndex])
		history.printMyData()
	
printTime = time.time()-fixTime-parseTime-startTime


gdb("Done parsing data!")
if gdebug: #some output for debugging.....
	print(" ")
	print("Time to fix json file = ",fixTime, "seconds")
	print("Time to parse data = ", parseTime ,"seconds")
	print("Time to print data = ", printTime ,"seconds")
	print("Database entries parsed = ",len(listOfDicts))
##################################################################
############ VISUALIZATION PROGRAMMING BELOW ##################### 
##################################################################

class Viz(object):
	#creating an instance of this class initalizes the vizualization,
	#canvas, and calls timerFired 

	def __init__(self):
		self.root = Tk()
		self.root.resizable(width=False,height=False)
		self.canvasWidth = 800
		self.canvasHeight = 300
		self.canvas = Canvas(self.root,width=self.canvasWidth,height=self.canvasHeight)
		self.canvas.pack()
		self.root.canvas = self.canvas.canvas = self.canvas
		class Struct: pass
		self.canvas.data = Struct()
		self.init()
		self.root.bind("<Button-1>",self.mouse1Pressed)
		self.root.bind("<Button-3>",self.mouse3Pressed)
		self.root.bind("<Motion>",self.mouseMotion)
		self.root.bind("<ButtonRelease-1>",self.mouse1Released)
		self.root.bind("<ButtonRelease-3>",self.mouse3Released)
		self.root.bind("<Key>",self.keyPressed)
		self.root.bind("<KeyRelease>",self.keyReleased)
		self.timerFired()
		self.root.mainloop()

	def init(self):
		#loads and initializes all the variables/files needed by
		#the vizualization
		self.framerate = 5 #50 #frames per second
		self.initImages() #loads all the images/maps/etc
		self.initMenuBools()
		self.initVizVars()
		self.initDataWindowVars()		

	def  initImages(self):
		#loads all the images/files needed by the vizualization
		#self.canvas.data.PHDmap = PhotoImage(file="PHDmap.gif")
		print("Images Loaded!")

	def initMenuBools(self):
		#menu programming booleans than can be used to add complexity
		self.inViz = True

	def initVizVars(self):
		#self.displayTime will be used by updateCurrentMarkerLocations() 
		#and make those the most recent time of each marker that is 
		#before the current displayTime

            self.displayTime = "1999-12-31 23:59:59.999"  #most recent displayTime
            self.backGroundPosition = 0	
            self.Button1 = False
            self.Button3 = False
            self.keysPressed = set()
            self.trackMarker = str(input("What marker do you want to track?"))

	def initDataWindowVars(self):
		#This function finds the mean, xrange, and yrange of the data
		#in the histories so that we can display it correctly

		minX = 99999
		minY = 99999
		maxX = -99999
		maxY = -99999
		meanX = 0;
		meanY = 0;
		for history in markerHistories:
			for index in range(len(history.timeStamps)):
				x = history.xValues[index]
				y = history.yValues[index]
				meanX += float(x)
				meanY += float(y)
				if x < minX:
					minX = x
				if x > maxX:
					maxX = x
				if y < minY:
					minY = y
				if y > maxY:
					maxY = y
			meanX = meanX/len(listOfDicts)
			meanY = meanY/len(listOfDicts)	
		#subtract the x and y shifts from the point cloud to center them on the 
		#middle of the window, nominally 400,300 where the origin is the 
		#top left corner 0,0			
		self.xShift = self.canvasWidth/2.0 - meanX   
		self.yShift = self.canvasHeight/2.0 - meanY
		#scale tells us how much to expand the data, converting from meters
		#to pixels by multiplying before mean shifting
		xScale = self.canvasWidth/(maxX-minX)
		yScale = self.canvasHeight/(maxY-minY)
		self.scale = min(xScale,yScale) #This keeps the data square
		
  

	def timerFired(self):
		#this is the clock for the program
		if self.inViz:
			#do all the vizualization things that change draw to 
			#draw
			self.updateCurrentMarkerLocations()
			self.updateTime()
			self.redrawAll()
			delay = 1000//self.framerate #miliseconds
			db(delay)
			db(self.framerate)	
		self.executeKeys()
		self.canvas.after(delay,self.timerFired)

	def updateCurrentMarkerLocations(self):
		#update the marker locations
		gdb("updating current marker locations!")


	def updateTime(self):
		#advance time by the time step, updates history.timeStampIndex's too
		gdb("advancing the time!")
		for history in markerHistories:
			if history.timeStampIndex < (history.entries-1):
				history.timeStampIndex += 1



##############################################################
################ CONTROL PROGRAMMING BELOW ###################	
##############################################################


	def mouseControls(self):
		gdb("in mouse controls")

	def mouse1Pressed(self,event):
		gdb("in mouse1Pressed")

	def mouse3Pressed(self,event):
		gdb("in mouse3Pressed")
	
	def mouseMotion(self,event):
		gdb("in mouseMotion")
		self.mousePosition=(event.x,event.y)

	def mouse1Released(self,event):
		self.Button1 = False
		pass

	def mouse3Released(self,event):
		self.Button3 = False
		pass

	def keyPressed(self,event):
		gdb("in keyPressed")
		if event not in self.keysPressed:
			self.keysPressed.add(event)
		
	
	def executeKeys(self):
		#goes through the list of pressed keys
		#and does something for each of them; this allows
		#multiple keys to pressed at once

		for event in self.keysPressed:
			db("a pressed key is")
			db(event.keysym)		
			if event.keysym == 'Escape':
				self.quit()

	def keyReleased(self,event):
		#removes the pressed key from the list of keys pressed
		returnSet = set()
		self.keysPressedKS = []
		for item in self.keysPressed:
			self.keysPressedKS += set([item.keysym])
		#this baloney just makes it faster because
		#we dont look at all the events, just the ones
		#we need to
		if event.keysym in self.keysPressedKS:
			for item in self.keysPressed:
				if item.keysym != event.keysym:
					returnSet.add(item)
			self.keysPressed = set(returnSet)





##############################################################
################ VIZ DISPLAY PROGRAMMING BELOW ###############
##############################################################


	def redrawAll(self):
		db("redrawing everything")
		self.canvas.delete(ALL)
		self.drawMap()
		self.drawMarkerPositions()
		self.drawTime()
	
	def drawMap(self):
            x = 800-353
            y = 133
            #self.canvas.create_image(x,y,image=self.canvas.data.PHDmap)


	def drawMarkerPositions(self):
		for history in markerHistories:
                    if history.name == self.trackMarker:
                        self.drawMostRecentPosition(history)

	def drawMostRecentPosition(self,history):
        #need to map phd lounge space to image space
            xmin = -.0508
            xmax = 12.192
            ymin =  -1.3335 
            ymax = 3.60045
            xminPix = 800-706 
            xmaxPix = 800
            yminPix = 0 
            ymaxPix = 277
            aRatio = (xmax-xmin)/(ymax-ymin)
            pRatio = 704/12.24

        #meanshift, scale, unmeanshift
            
            drawTime = history.timeStampIndex
            for i in range(drawTime-1):
                if (1):             
                    x1Raw = float(history.xValues[i])
                    y1Raw = float(history.yValues[i])
                    x2Raw = float(history.xValues[i+1])
                    y2Raw = float(history.yValues[i+1])
                
                    x1 =  (x1Raw-xmin)*pRatio + xminPix
                    y1 = (y1Raw-ymin)*pRatio + yminPix
                    x2 =  (x2Raw-xmin)*pRatio + xminPix
                    y2 = (y2Raw-ymin)*pRatio + yminPix
                    
                    self.canvas.create_line(x1,y1,x2,y2,fill = "red")
                    if gdebug:print("x = ",x2," y = ",y2)
            if (drawTime>2):self.canvas.create_text(x2,y2,anchor=W,text = history.name, font = ("fixedSysi",12),fill="black")

	def drawTime(self):
		maxTimeIndex = 0
		maxHistoryIndex = 0;
		for historyIndex in range(len(markerHistories)):
			if markerHistories[historyIndex].timeStampIndex > maxTimeIndex:
				maxTimeIndex = markerHistories[historyIndex].timeStampIndex
				maxHistoryIndex = historyIndex
		self.canvas.create_text(50,250,anchor = W, text = markerHistories[maxHistoryIndex].timeStamps[maxTimeIndex], font = ("FixedSys",12),fill="black")



##############################################################
############### OTHER PROGRAMMING BELOW ######################
##############################################################
	
	def quit(self):
		#quits the visualization loop
		db("NICE KNOWNING YA!")
		self.root.destroy()

Viz()


