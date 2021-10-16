#!/usr/bin/python
############################################################################
# File:			errorHandling.py
# Organization:	University of twente
# Group:		CAES
# Date:			15-10-2021
# Version:		2.0.0
# Author:		Matthijs Souilljee, s2211246
# Education:	EMSYS msc.
############################################################################
# Some new errorhandling used on various places in ASDEC
############################################################################

from logic import datatypes
import sys
import os

class ErrorHandling(object):
    @staticmethod
    def HardwareCheck(hardwareDefinition):
        if hardwareDefinition != datatypes.Hardware.NULL:
            print("ERROR: hardware option not valid")
            print("only use one --GPU or --CPU")
            sys.exit(1)

    @staticmethod
    def ClassificationCheck(classificationDefinition):
        if classificationDefinition != datatypes.Classification.NULL:
            print("ERROR: classification option not valid")
            print("only use one --NS, --NH, or --NHS")
            sys.exit(1)

    @staticmethod
    def ThreadNumberCheck(threads):
        if (int(threads) < 1):
            print("ERROR: threads can not be zero or smaller then zero")
            sys.exit(1)

    @staticmethod
    def TryCountCheck(triesCount):
        if (triesCount < 1):
            print("ERROR: Count should atleast be 1")
            sys.exit(1)

    @staticmethod
    def InputDataCheck(startSet1, endSet1, startSet2, endSet2, rawFilesPath):
        if (((int(startSet1) == 0 and int(endSet1) == 0 and int(startSet2) == 0
            and int(endSet2) == 0 and len(rawFilesPath) == 0) or 
            (int(startSet1) > int(endSet1) or int(startSet2) > int(endSet2))) and 
            len(rawFilesPath) == 0):
            print("ERROR: Not enough data to train a model")
            print("Data generation is only supported for binary classification tasks")
            sys.exit(1) 

    @staticmethod
    def ModelExistsCheck(model, force):
        if (os.path.exists(model) and not force):
            print("ERROR: Model already present and no overwrite flag is provided")
            print("If overwrite is desired add --force flag")
            sys.exit(1)

    @staticmethod
    def TrajectoryExistsFolderCheck():
        if (not os.path.exists("trajectory_files/")):
            print("ERROR: no folder called trajectory files, please")
            print("run: ./tools/setupTrajectoryFiles.sh")
            sys.exit(1) 

    @staticmethod
    def ClassificationSelected(classificationDefinition):
        if classificationDefinition == datatypes.Classification.NULL:
            print("ERROR: no classification option provided")
            print("only use one --NS, --NH, or --NHS")
            sys.exit(1)

    @staticmethod
    def HardwareSelected(hardwareDefinition):
        if hardwareDefinition == datatypes.Hardware.NULL:
            print("ERROR: no hardware option provided")
            print("only use one --GPU or --CPU")
            sys.exit(1)
