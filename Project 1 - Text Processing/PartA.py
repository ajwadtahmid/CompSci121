############################################################################
##  PART A: Word Frequencies:                                             ##
##   Description:                                                         ##
##      Run on command line using command:                                ##
##          python PartA.py [filename]                                    ##
##   Input: [filename] - the path to a txt file                           ##
##   Output: prints tokens and frequencies                                ##
##                                                                        ##
##   (Header Uploaded by Cora Schallock, last updated 1/10/23)            ##
############################################################################

'''
Runtime Analysis: PartA is divided into 5 main methods. They are in sequential order:
fileReader, tokenize, makeFrequencyDict, computeWordFequency and printWordFrequency.

fileReader has a linear runtime as it reads the whole input once.

The runtime for tokenize is linear with the input as it goes over each char in the input once 
and checks if it's valid with isValid(char) and adds it to a list or ignores it otherwise. the list is then returned.

makeFrequencyDict is also linear with the input as it goes over the token list once and adds it to a dictionary.

computeWordFequency uses bucket sort to make buckets for the frequency of words and add the words of specific frequency
to the indexed buckets. It then performs a sort on each bucket to sort them alphabetically. Adding to the buckets is linear with
respect to the input. Even in the case of the sample text being just one word repeating many time where each word is added to 
the same bucket, the runtime for Timsort is linear for identical items. (https://stackoverflow.com/a/66925224)

printWordFrequency is also linear with respect to the input frequency as it prints each token which is less than equal to the input.
'''

import sys

def fileReader(fileName):
    try:
        with open(fileName, "r") as file:
            fileContent = file.read()
            return fileContent
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def isValid(char):
    if 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9':
        return True
    else:
        return False

def tokenize(fileContent):
    filteredToken = ''
    tokens = []

    for char in fileContent:
        if isValid(char):
            filteredToken += char
        else:
            if filteredToken:
                tokens.append(filteredToken.lower())
                filteredToken = ''

    if filteredToken:
        tokens.append(filteredToken.lower())
    return tokens

def makeFrequencyDict(tokenList):
    frequencyDictionary = {}
    for token in tokenList:
        if token in frequencyDictionary:
            frequencyDictionary[token] += 1
        else:
            frequencyDictionary[token] = 1
    return frequencyDictionary

def computeWordFequency(tokenList, frequencyDictionary):
    buckets = []
    for _ in range(len(tokenList) + 1):
        buckets.append([])
    for word, freq in frequencyDictionary.items():
        buckets[freq].append(word)
    
    for bucket in buckets:
        bucket.sort();
    return buckets

def printWordFrequency(buckets):
    for freqIndex in range(len(buckets) - 1, 0, -1):
        if buckets[freqIndex]:
            for token in buckets[freqIndex]:
                print(f"{token}\t{freqIndex}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Command must be in format=> python PartA.py [filename]")
    else:
        fileName = sys.argv[1]
        fileContent = fileReader(fileName)

        if fileContent:
            tokenList = tokenize(fileContent)
            frequencyDictionary = makeFrequencyDict(tokenList)
            buckets = computeWordFequency(tokenList, frequencyDictionary)
            printWordFrequency(buckets)