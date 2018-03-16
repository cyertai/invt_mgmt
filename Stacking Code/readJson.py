# Module for reading data from Json file
# Code created by Glenn Philen

import json
import time
import string
import sys

sdebug = 0 #script debug make 1 to enable debug console prints, 0 otherwise
gdebug = 1 #game debug make 

# db is a debut print statement that we can turn off when the code is good
def db(text):
    #debug function
    if sdebug:
        print(text)

def gdb(text):
    #game debug function
    if gdebug:
        print(text)

def fixJson(inputString):
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

def readFile(filename):
    startTime = time.time() 
    
    jsonData=open(filename,"r")
    jsonData = fixJson(jsonData.read())
    db(" ")
    db(" ")
    db(jsonData)

    listOfDicts = json.loads(jsonData) #using json.loads becayse jsonData is already a string
    if sdebug:
        for obj in listOfDicts:
            #db(obj)
            db(obj["c_ts"])

    fixTime = time.time()-startTime
    print("Time to fix json file = ",fixTime, "seconds")
    return listOfDicts

