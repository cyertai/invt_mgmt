# Module used to write data to Json file

import json
import time
import string
import sys

def writeFile(listOfDicts, filename):
    startTime = time.time()
    print("Writing to json file...")
    json.dumps(listOfDicts)
    outFile = open(filename, 'w')
    jsonFormat = json.dumps(listOfDicts)
    outFile.write(jsonFormat)
    print("Done!")
    writeTime = time.time()-startTime
    print("Time to write json file = " + str(writeTime) + " seconds")
    return