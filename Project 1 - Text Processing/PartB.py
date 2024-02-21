############################################################################
##  Part B: Intersection of two files:                                    ##
##   Description:                                                         ##
##      Run on command line using command:                                ##
##          python PartB.py [filename1] [filename2]                       ##
##   Input: [filename1] - the path to a txt file                          ##
##          [filename2] - the path to a txt file                          ##
##   Output: prints the number of tokens file1 and file2 have in common   ##
##                                                                        ##
##   (Header Uploaded by Cora Schallock, last updated 1/10/23)            ##
############################################################################

'''
Runtime Analysis: PartB is divided into 4 main methods. They are in sequential order,
fileReader. tokenize, makeFrequencyDict from PartA and intersectionChecker.

fileReader has a linear runtime as it reads the whole input once.

The runtime for tokenize is linear with the input as it goes over each char in the input once 
and checks if it's valid with isValid(char) and adds it to a list or ignores it otherwise. the list is then returned.

makeFrequencyDict is also linear with the input as it goes over the token list once and adds it to a dictionary.

intersectionChecker is also linear as it goes over the token list from the 2nd file and checks if the token exists in the 
dictionary from the 1st file or not. If it does, the counter is incremented and the token is deleted from the dictionary.
Otherwise it does nothing. Counter is returned at the end.
'''

import sys
from PartA import tokenize, makeFrequencyDict, fileReader

def intersectionChecker(tokenList, frequencyDict):
    counter = 0
    for token in tokenList:
        if token in frequencyDict:
            counter += 1
            del frequencyDict[token]
    return counter

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Command must be in format=> python PartA.py [filename1] [filename2]")
    else:
        fileName1 = sys.argv[1]
        fileName2 = sys.argv[2]
        fileContent1 = fileReader(fileName1)
        fileContent2 = fileReader(fileName2)

        if fileContent1:
            tokenList1 = tokenize(fileContent1)
            frequencyDict1 = makeFrequencyDict(tokenList1)
            tokenList2 = tokenize(fileContent2)
            intersection = intersectionChecker(tokenList2, frequencyDict1)  
            print(intersection)