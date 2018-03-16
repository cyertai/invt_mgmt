import string

def centroidDistance(center, part):
    # Calculate separation distance (in meters) between a part and a center coordinate
    # Center is stored as [x,y,z]
    Cx = center[0]
    Cy = center[1]
    Cz = center[2]

    Px = float(part['l_x'])
    Py = float(part['l_y'])
    Pz = float(part['l_z'])

    distance = ((Cx-Px)**2+(Cy-Py)**2+(Cz-Pz)**2)**.5
    return distance


def partDistance(partA, partB):
    # Calculate separation distance (in meters) between 2 parts stored as dicts
    Ax = float(partA['l_x'])
    Ay = float(partA['l_y'])
    Az = float(partA['l_z'])

    Bx = float(partB['l_x'])
    By = float(partB['l_y'])
    Bz = partB['l_z']

    distance = ((Ax-Bx)**2+(Ay-By)**2+(Az-Bz)**2)**.5
    return distance

def calculateCenter(parts):
    # Calculate centroid location of an arbitrary amount of parts
    numParts = len(parts)
    if numParts == 0: 
        print("No parts in stack")
        return None
    elif numParts == 1:
        return [float(parts[0]['l_x']),float(parts[0]['l_y']),float(parts[0]['l_z'])]
    totalX = 0
    totalY = 0
    totalZ = 0
    
    for i in range(numParts):
        part = parts[i]
        print(part)
        Px = float(part['l_x'])
        Py = float(part['l_y'])
        Pz = float(part['l_z'])
        totalX += Px
        totalY += Py
        totalZ += Pz

    Cx = totalX / numParts
    Cy = totalY / numParts
    Cz = totalZ / numParts
    center = [0]*3
    center[0] = Cx
    center[1] = Cy
    center[2] = Cz
    return center


def lastTimeStamp(listOfParts):
    # Returns the latest time stamp from a given list of parts
    if len(listOfParts) == 0: 
        print("No parts in stack")
        return None
    lastPart = listOfParts[-1]
    times = ['']*2
    times[0] = lastPart['p_ts']
    times[1] = lastPart['c_ts']
    return times

def createPart(m_id, l_id, c_id, xyz, Rxyz, times, i_url, abc):
    #xyz- [l_x, l_y, l_z]
    #Rxyz- [w_x, w_y, w_z]
    #times- [p_ts, c_ts]
    #abc- [l_a, l_b, l_c, w_a, w_b, w_c]
    # Creates a part dictionary using the supplied attributes
    newPart = dict()
    newPart['m_id'] = m_id
    newPart['l_id'] = l_id
    newPart['c_id'] = c_id

    newPart['l_x'] = str(xyz[0])
    newPart['l_y'] = str(xyz[1])
    newPart['l_z'] = str(xyz[2])

    newPart['w_x'] = str(Rxyz[0])
    newPart['w_y'] = str(Rxyz[1])
    newPart['w_z'] = str(Rxyz[2])

    newPart['p_ts'] = times[0]
    newPart['c_ts'] = times[1]
    newPart['i_url'] = i_url

    newPart['l_a'] = str(abc[0])
    newPart['l_b'] = str(abc[1])
    newPart['l_c'] = str(abc[2])
    newPart['w_a'] = str(abc[3])
    newPart['w_b'] = str(abc[4])
    newPart['w_c'] = str(abc[5])

    return newPart


