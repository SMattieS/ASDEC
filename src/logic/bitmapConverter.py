############################################################################
# File:			bitmapConverter.py
# Organization:	University of twente
# Group:		CAES
# Date:			31-07-2021
# Version:		1.0.0
# Author:		Matthijs Souilljee, s2211246
# Education:	EMSYS msc.
############################################################################
# File consists of one function which is responsible for the conversion
# from the ms output.txt file to a grayscale .png format
# This .png image forms the input for the Convolutional Neural Network
############################################################################

# region import packages
import numpy as np
from PIL import Image
import re
import math
# endregion

############################################################################
# Only function within this file in this function
# all conversions take place
############################################################################


def ImageConversion(path, outPath, windowMode, stepRows, windowsSize,
                    extractionEnb, extractionOffset, extractionPoint,
                    multiplyPosition, startPop, endPop):

    ########################################################################
    # open the defined file which contains the genome information
    ########################################################################
    msfile = open(path, 'r')

    ########################################################################
    # get the numbered elements from the first line
    # check which type of simulation is being run
    # reading the first line of the txt file generated by ms/mssel
    # provides us with necessary information how to handle the remainder
    # of the file.
    ########################################################################
    for lineIndex, line in enumerate(msfile):
        if lineIndex == 0:
            compileInformation = [
                int(lineIndex) for lineIndex in line.split() if
                lineIndex.isdigit()]
            if (line.find('mbs') != -1):
                numberOfRows = compileInformation[0]
                endPopRead = compileInformation[len(compileInformation)-1]
                offset = 0
                multiplyPosition = multiplyPosition/100000
            elif (line.find('msHOT') != -1):
                numberOfRows = compileInformation[0]
                endPopRead = compileInformation[1]
                offset = 1
            elif (line.find('ms') != -1 or line.find('mssel') != -1):
                numberOfRows = compileInformation[0]
                endPopRead = compileInformation[1]
                if line.find("-t") != -1 and line.find("-s") != -1:
                    offset = 1
                elif line.find("-t") != -1 or line.find("-s") != -1:
                    offset = 0
                else:
                    print("not supported input parameters")
                    return
            else:
                print("not supproted software package")
                return
            break
        elif lineIndex > 0:
            break
    #####################################################################
    # skipping through a certain amount of populations
    # also check the range
    #####################################################################
    if endPop == 0:
        endPop = endPopRead
    if startPop < 0 or endPop > endPopRead:
        print("start population: " + str(startPop))
        print("end population: " + str(endPop))
        print("file information: " + str(endPopRead))
        print("ERROR: start population and/or end population incorrect")
        return
    for lineIndex, line in enumerate(msfile):
        if lineIndex >= (numberOfRows + offset + 4) * startPop:
            break
    ########################################################################
    # Now we start looping over all the array's present in the file
    # we have this information from the first line of the ms/mssel file.
    # We look for the // line, because this indicates the start of the
    # information we would like to obtain
    ########################################################################
    for itter in range(startPop, endPop):
        # print("itteration number in the same file--> " + str(itter))
        for lineIndex, line in enumerate(msfile):
            if line.find('//') != -1:
                break
            elif lineIndex > 15:
                print("LineIndex time out more then 15 seperator lines")
                return

        #####################################################################
        # read the amount of segsites
        #####################################################################
        for lineIndex, line in enumerate(msfile):
            if line.find('segsites') != -1:
                sizeFirstMatrix = [int(lineIndex)
                           for lineIndex in line.split()
                           if lineIndex.isdigit()]
                numberSegsites = sizeFirstMatrix[0]
                break
            elif lineIndex > 15:
                print("LineIndex time out more then 15 segsites lines")
                return

        #####################################################################
        # read the line with probabilites if possible
        # We do not use this so we just skip the line determined by if
        # the data was generated with the -t and -s flags within
        # ms and/or mssel
        #####################################################################
        if offset == 1:
            for lineIndex, line in enumerate(msfile):
                if lineIndex >= 0:
                    break

        #####################################################################
        # get the numbered elements (floats) from the fifth line which are
        # the positions and convert the list of positions to floats
        # multiplication with a constant of all elements within position
        # is possible. This is done to go from the relative position provided
        # by the position array itself to the absolute position.
        #####################################################################
        for lineIndex, line in enumerate(msfile):
            if line.find('positions') != -1:
                positions = np.array(re.findall("\d+\.\d+", line))
                if len(positions) == 0:
                    positions = np.array(re.findall("\d+", line))
                positions = positions.astype(np.float)
                positions = positions * multiplyPosition
                break
            elif lineIndex > 15:
                print("LineIndex time out more then 15 position lines")
                return

        #####################################################################
        # Variables storing the position information
        #####################################################################
        minPosition = positions[0]
        maxPosition = positions[len(positions)-1]
        
        #####################################################################
        # Generate warning when amount of segsites is not equal to
        # position vector length! NOT ASDEC WARNING!
        #####################################################################
        if (numberSegsites != len(positions)):
            # print("WARNING: ASDEC detected mismatch between segsites given" +
            # " and the vector length!")
            numberSegsites = len(positions)
        
        #####################################################################
        # define an empty matrix which will be filled by the data later
        #####################################################################
        matrix = np.empty(
            [numberOfRows, len(positions)], dtype=np.uint8)

        #####################################################################
        # counter how many lines are already
        #####################################################################
        counterMatrix = 0

        #####################################################################
        # fill the matrix with the corresponding notation
        #####################################################################
        for lineIndex, line in enumerate(msfile):
            if lineIndex < numberOfRows:
                line = line.replace('\n', '')
                # replace the . which means empty space by 2
                line = line.replace('.','2')
                matrix[counterMatrix] = np.array(list(line), dtype=np.uint8)
                counterMatrix += 1
            elif lineIndex >= numberOfRows:
                break

        #####################################################################
        # check center mode and change the amount of segsites
        # the center is determined based on the positions
        #####################################################################
        if extractionEnb:
            center = min(range(len(positions)),
                         key=lambda i: abs(positions[i] -
                                           (extractionPoint)))
            numberSegsites = extractionOffset*2
            minIndex = center - extractionOffset
            maxIndex = center + extractionOffset
            # check if the new index's are valid
            if ((minIndex < 0) or (maxIndex > len(positions))):
                print("ERROR: Given extraction point not possible")
                return
            matrix = matrix[:, minIndex:maxIndex]
            positions = positions[minIndex:maxIndex]
            minPosition = positions[0]
            maxPosition = positions[len(positions)-1]
            if (len(positions) != extractionOffset * 2):
                print("ERROR: Size not correct")
                return

        #####################################################################
        # each element in the matrix should be multiplied with 255, so either
        # black or white
        #####################################################################
        matrix = matrix * 127

        #####################################################################
        # if extra actions need to be performed on the data do it here!
        # for later implementation as discussed before
        #####################################################################

        #####################################################################
        # possible to enable window mode
        # if enabled multiple images are created per matrix
        # otherwise just one image is generated
        #####################################################################
        if windowMode:
            if windowsSize > numberSegsites:
                print(
                    "The chosen window size and step size are not " +
                    "sufficient to create an output, no image is generated!")
            else:
                for counter in range(0, (numberSegsites-windowsSize+1),
                                     stepRows):
                    adjustedMatrix = matrix[:, counter:windowsSize+counter]
                    img = Image.fromarray(adjustedMatrix)
                    img.save(outPath + str(counter) + ".n_" + str(itter) +
                             ".w_start_" +
                             str(positions[counter]) + ".w_end_" +
                             str(positions[counter+windowsSize-1]) + ".png")
        else:
            img = Image.fromarray(matrix)
            img.save(outPath + ".n_" + str(itter) + ".w_start_" +
                     str(minPosition) + ".w_end_" + str(maxPosition)
                     + ".png")

    ########################################################################
    # close the file
    ########################################################################
    msfile.close()
