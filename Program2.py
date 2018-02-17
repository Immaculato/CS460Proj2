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
    def __init__(self, trainingFilename, debug):
        self.debug = debug
        file = None
        try:
            fileTraining = open(trainingFilename, "r")
        except:
            print('training file not found')
            exit -1
        
        #get all the ratings for each user.
        for line in fileTraining:
            parsedLine = line.split('\t')
            #mark the distinct movie indexes and user indexes.
            self.users.add(int(parsedLine[0]))
            self.movieIndexes.add(int(parsedLine[1]))
            #if we don't already have the user in the dictionary, initialize their entry.
            if int(parsedLine[0]) not in self.userRatings:
                self.userRatings[int(parsedLine[0])] = dict()
            #for each user, add an entry for the movie, and their rating.
            self.userRatings[int(parsedLine[0])][int(parsedLine[1])] = float(parsedLine[2])

        #go back through and add default values for each missing movie, noting the missing movies. we'll use these to test the algorithm's predictions.
        for user in self.users:
            for i in range(1, max(self.movieIndexes)+1):
                if i not in self.userRatings[user]:
                    self.userRatings[user][i] = 2.5
                    self.testIndexes[user] = i
                #looks like there's a chance that a movie index doesn't appear in the training data. add it in.
                if i not in self.movieIndexes:
                    self.movieIndexes.add(i)

        #print self.userRatings[405]

        #print 'euclidean distance test', self.__euclideanDistance__((1, 1, 1), (1, 1, 1))
        #self.__kNearestNeighbors(1, 3, [1])


    def __cosineSimilarity__(self, vector1, vector2):
        topDotProduct = 0.0
        vector1SquaredSum = 0.0
        vector2SquaredSum = 0.0
        #tot = 0.0
        for i in self.movieIndexes:
            topDotProduct += vector1[i]*vector2[i]
            vector1SquaredSum += vector1[i]**2
            vector2SquaredSum += vector2[i]**2
            #tot += (vector1[i] - vector2[i])**2
        return topDotProduct / (((vector1SquaredSum) ** 0.5) * ((vector2SquaredSum) ** 0.5))


    #using the index of the user to predict for and k neighbors, predict ratings for each movieIndex.
    #returns a list of floats that correspond to rating predictions for each movie index given.
    def kNearestNeighborsPrediction(self, userIndex, k, movieIndexes):
        #find the euclidean distance for each other user to the current user.
        otherUserDistances = dict()
        #for each other user,
        for user in self.users:
            if user != userIndex:
                #find the cosine similarity from that user to the current user.
                otherUserDistances[user] = self.__cosineSimilarity__(self.userRatings[userIndex], self.userRatings[user])

        #now, find the k nearest neighbors
        kNearestNeighborsIndexes = list()
        neighborsSimilarities = dict()
        for i in range(k):
            minUserIndex = min(otherUserDistances, key=otherUserDistances.get)
            #print 'min distance',otherUserDistances[minUserIndex]
            kNearestNeighborsIndexes.append(minUserIndex)
            neighborsSimilarities[minUserIndex] = otherUserDistances[minUserIndex]
            #print 'min index',minUserIndex
            #take out the min user so we don't add them multiple times.
            del otherUserDistances[minUserIndex]

        #print kNearestNeighborsIndexes
        #use the k nearest neighbors to make a prediction for the given movie indexes.
        numerator = 0.0
        denominator = 0.0
        movieRatingPredictions = list()
        for movie in movieIndexes:
            for i in kNearestNeighborsIndexes:
                #print 'movie', movie, 'i', i
                #print 'similarity', neighborsSimilarities[i]
                #print 'user rating', self.userRatings[i][movie]
                numerator += neighborsSimilarities[i]*self.userRatings[i][movie]
                denominator += neighborsSimilarities[i]
            movieRatingPredictions.append(numerator/denominator)

        #print 'ratings', movieRatingPredictions
        return movieRatingPredictions






def main():
    if (len(sys.argv) != 3):
        print "Takes 2 command line arguments: the name of the training file, and the test file."
        exit(-1)
    trainingFilename = sys.argv[1]
    testFilename = sys.argv[2]
    kNeighbor = KNearestNeighbor(trainingFilename, debug=True)
    testFile = None
    try:
        testFile = open(testFilename, "r")
    except:
        print('test file not found')
        exit -1
    testRatings = dict()
    for line in testFile:
        parsedLine = line.split('\t')
        #if we don't already have the user in the dictionary, initialize their entry with a list of movies to rate.
        if int(parsedLine[0]) not in testRatings:
            testRatings[int(parsedLine[0])] = list()
        #for each user, add the indexes of the movies they need predicted.
        testRatings[int(parsedLine[0])].append(int(parsedLine[1]))

    #now, predict the ratings for each user.
    testUserPredictions = dict()
    for user in testRatings:
        #print 'user', user, 'movies', testRatings[user]
        prediction = kNeighbor.kNearestNeighborsPrediction(user, 3, testRatings[user])
        testUserPredictions[user] = prediction
        print 'finished user', user


main()
