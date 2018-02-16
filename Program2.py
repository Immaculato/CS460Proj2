#Tristan Basil
#Assignment: Project 1 - cS460G Machine Learning, Dr. Harrison
#https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary -
#used to find corresponding key to min value in a dictionary

import math
import sys
import copy

#this class is only designed to work for the data in this project.
class KNearestNeighbor:
    debug = False
    userIDs = list()
    movieIndexes = set()
    users = set()
    movieRatings = list()
    userRatings = dict()
    testIndexes = dict()

    #initialization takes a filename.
    def __init__(self, trainingFilename, testFilename, debug):
        self.debug = debug
        file = None
        try:
            fileTraining = open(trainingFilename, "r")
            fileTest = open(testFilename, "r")
        except:
            print('one or more files not found')
            exit -1
        
        #get all the ratings for each user.
        movieRatings = list()
        for line in fileTraining:
            parsedLine = line.split('\t')
            #mark the distinct movie indexes and user indexes.
            self.users.add(int(parsedLine[0]))
            self.movieIndexes.add(int(parsedLine[1]))
            #save each movie rating with the respective user. we'll use this to rebuild each user's vector.
            #movieRatings.append((int(parsedLine[0]), int(parsedLine[1]), int(parsedLine[2])))
            #if we don't already have the user in the dictionary, initialize their entry.
            if int(parsedLine[0]) not in self.userRatings:
                self.userRatings[int(parsedLine[0])] = dict()
            #for each user, add an entry for the movie, and their rating.
            self.userRatings[int(parsedLine[0])][int(parsedLine[1])] = float(parsedLine[2])

        #go back through and add default values for each missing movie, noting the missing movies. we'll use these to test the algorithm's predictions.
        for user in self.users:
            for i in self.movieIndexes:
                if i not in self.userRatings[user]:
                    self.userRatings[user][i] = 2.5
                    self.testIndexes[user] = i

        self.__kNearestNeighbors(1, 3)


    def __euclideanDistance__(self, vector1, vector2):
        tot = 0.0
        for i in self.movieIndexes:
            tot += (vector1[i] - vector2[i])**2
        tot = tot**0.5
        return tot


    def __kNearestNeighbors(self, userIndex, k):
        #find the euclidean distance for each other user to the current user.
        otherUserDistances = dict()
        #for each other user,
        for user in self.users:
            if user != userIndex:
                #find the distance from that user to the current user.
                otherUserDistances[user] = self.__euclideanDistance__(self.userRatings[userIndex], self.userRatings[user])

        #now, find the k nearest neighbors
        kNearestNeighborsIndexes = list()
        for i in range(k):
            minUserIndex = min(otherUserDistances, key=otherUserDistances.get)
            print min(otherUserDistances)
            kNearestNeighborsIndexes.append(minUserIndex)
            print minUserIndex
            #take out the min user so we don't add them multiple times.
            del otherUserDistances[minUserIndex]






def main():
    if (len(sys.argv) != 3):
        print "Takes 2 command line arguments: the name of the training file, and the test file."
        exit(-1)
    trainingFilename = sys.argv[1]
    testFilename = sys.argv[2]
    debug = True
    kNeighbor = KNearestNeighbor(trainingFilename, testFilename, debug)

main()
