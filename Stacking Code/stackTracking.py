# Module that returns timestamps, locations, and ids of detected stacks

import readJson
import writeJson
import partOperations
import string
import time

def trackStacks(filename):
    listOfDicts = readJson.readFile(filename)
    #print(listOfDicts)
    # Number of entries to slide by for each scan
    timeSlide = 10
    # Number of entries contained within the sliding window
    timeWidth = 10
    # Physical separation in meters to be considered stacked
    distance = .25
    numEntries = len(listOfDicts)
    i = 0
    # Returned list of dicts
    newList = []
    # Running list of all currently observed 
    observedIds = []
    listId = 0
    while i < numEntries:
        currentEntries = [] #Stores dicts of current markers in window
        currentIds = [] #Stores current marker IDs in window
        for e in range(timeWidth):
            if (i + e) < numEntries: #Prevent out of bounds error
                currentDict = listOfDicts[i+e]
                currentMarker = currentDict['m_id']
                if currentMarker not in currentIds:
                    currentEntries.append(currentDict)
                    currentIds.append(currentMarker)
        stack = [] # Current parameters of the stack detected
        stackIds = []
        currentCenter = [0,0,0]
        for part in currentEntries:
            numIds = len(currentEntries)
            if numIds == 0:
                stack.append(part)
                stackIds.append(part['m_id'])
                currentCenter = partOperations.calculateCenter(stack)

            elif (numIds > 0 and partOperations.centroidDistance(currentCenter,part) < distance):
                stack.append(part)
                stackIds.append(part['m_id'])
                currentCenter = partOperations.calculateCenter(stack)
        finalId = ''.join(stackIds)
        Rxyz = [0,0,0] # Dummy parameters to be passed into json file
        abc = [0,0,0,0,0,0]
        finalTimes = partOperations.lastTimeStamp(stack)
        #print(currentCenter)
        finalStack = partOperations.createPart(finalId,str(listId),'0',currentCenter,Rxyz,finalTimes,'null',abc)
        newList.append(finalStack)
        i += timeSlide
        listId += 1
    return newList

def main():
    writeJson.writeFile(trackStacks("stackingData.json"), "stackedItems.json")
    print("Passed!")
    return

main()