#Tristan Basil
#Assignment: Project 1 - cS460G Machine Learning, Dr. Harrison
#https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary -
#used to find corresponding key to min value in a dictionary
#https://stackoverflow.com/questions/26584003/output-to-the-same-line-overwriting-previous
#used to print progress

import sys
import random
import copy

#this class is only designed to work for the data in this project.
class KNearestNeighbor:
    debug = False
    fileContents = list()
    userIDs = list()
    movieIndexes = set()
    users = set()
    movieRatings = list()
    userRatings = dict()

    #initialization takes a filename.
    def __init__(self, fileContents, debug):
        self.fileContents = fileContents
        #get all the ratings for each user.
        for line in fileContents:
            parsedLine = line.split('\t')
            #mark the distinct movie indexes and user indexes.
            self.users.add(int(parsedLine[0]))
            self.movieIndexes.add(int(parsedLine[1]))
            #if we don't already have the user in the dictionary, initialize their entry.
            if int(parsedLine[0]) not in self.userRatings:
                self.userRatings[int(parsedLine[0])] = dict()
            #for each user, add an entry for the movie, and their rating.
            self.userRatings[int(parsedLine[0])][int(parsedLine[1])] = float(parsedLine[2])

        #go back through and add default values for each missing movie
        for user in self.users:
            for i in range(1, max(self.movieIndexes)+1):
                if i not in self.userRatings[user]:
                    self.userRatings[user][i] = 2.5
                #looks like there's a chance that a movie index doesn't appear in the training data. add it in.
                if i not in self.movieIndexes:
                    self.movieIndexes.add(i)

        #print self.userRatings[405]

        #print 'euclidean distance test', self.__euclideanDistance__((1, 1, 1), (1, 1, 1))
        #self.__kNearestNeighbors(1, 3, [1])

    #cross validate with the given k values. this will print the average mean squared error for each k value, and return the best k.
    def crossValidate(self, kValues, folds):

        fileContents = copy.deepcopy(self.fileContents)
        #test = KNearestNeighbor(fileContents, False)
        foldList = list()
        elementsPerBin = len(fileContents) // folds
        print('Partitioning folds for cross validation...')
        #split out into folds
        for i in range(folds):
            foldList.append(list())
            for j in range(elementsPerBin):
                indexAdd = random.choice(range(len(fileContents)))
                foldList[i].append(fileContents[indexAdd])
                del fileContents[indexAdd]
            #print 'bin', i, len(foldList[i])

        print('Beginning cross validation...')
        #start testing out each k.
        for k in kValues:
            #for each fold,
            averageMeanSquaredErrors = dict()
            totalMeanSquaredError = 0.0
            for i in range(folds):
                
                #extending every OTHER fold, this will be our training set. smash em together and build the object with that
                trainingList = list()
                for fold in range(folds):
                    if i != fold:
                        trainingList.extend(foldList[fold])
                #create a kNearestNeighbor object these folds (train on them)
                currentFold = KNearestNeighbor(trainingList, False)
                
                #this code is essentially yanked from main and repurposed here.
                testRatings = dict()
                actualRatings = list()
                for line in foldList[i]:
                    parsedLine = line.split('\t')
                    #if we don't already have the user in the dictionary, initialize their entry with a list of movies to rate.
                    if int(parsedLine[0]) not in testRatings:
                        testRatings[int(parsedLine[0])] = list()
                    #for each user, add the indexes of the movies they need predicted.
                    testRatings[int(parsedLine[0])].append(int(parsedLine[1]))
                    #keep the actual ratings for each user as well.
                    actualRatings.append(float(parsedLine[2]))

                #now, predict the ratings for each user, and find the mean squared error.
                meanSquaredError = 0.0
                index = 0
                iteration = 0
                numUsers = float(len(testRatings))
                for user in testRatings:
                    prediction = currentFold.kNearestNeighborsPrediction(user, k, testRatings[user])
                    #print prediction
                    for j in range(len(prediction)):
                        #print 'difference of', prediction[i], '-', actualRatings[index], '=', prediction[i] - actualRatings[index]
                        meanSquaredError += (prediction[j] - actualRatings[index]) ** 2
                        index+=1
                    iteration+=1
                    percentDone = round((float(iteration)/numUsers) * 100, 2)
                    sys.stdout.write('Progress: [%.2f%%] (Fold %d for K value %d)\r' % (percentDone,i,k))
                    sys.stdout.flush()

                totalMeanSquaredError += meanSquaredError/len(actualRatings)
                print ''

            totalMeanSquaredError = totalMeanSquaredError/folds
            averageMeanSquaredErrors[k] = totalMeanSquaredError
            print 'Average mean squared error for k =', k, totalMeanSquaredError

        #finally, we have our average mean squared errors. return the key for the lowest error!
        bestK = min(averageMeanSquaredErrors, key=averageMeanSquaredErrors.get)
        print 'Best k value:', bestK
        return bestK

    def __cosineSimilarity__(self, vector1, vector2):
        topDotProduct = 0.0
        vector1SquaredSum = 0.0
        vector2SquaredSum = 0.0
        #tot = 0.0
        for i in self.movieIndexes:
            #print vector1[i],'*',vector2[i]
            topDotProduct += vector1[i]*vector2[i]
            vector1SquaredSum += vector1[i]**2
            vector2SquaredSum += vector2[i]**2
            #tot += (vector1[i] - vector2[i])**2
        #print topDotProduct
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
                #print 'cosine similarity to user', user, otherUserDistances[user]

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
    kValues = [1, 3, 5, 7, 9]

    #try to open the training file, and populate the array of lines.
    fileContents = list()
    try:
        fileTraining = open(trainingFilename, "r")
        for line in fileTraining:
            fileContents.append(line)
    except:
        print('training file not found')
        exit -1
    
    print('Initializing training file...')
    kNeighbor = KNearestNeighbor(fileContents, debug=True)
    
    #time to cross validate.
    numFolds = 4
    k = kNeighbor.crossValidate(kValues, numFolds)
    #k = 3

    #open the testfile, and read the entries we need to test.
    testFile = None
    try:
        testFile = open(testFilename, "r")
    except:
        print('test file not found')
        exit -1
    testRatings = dict()
    actualRatings = list()
    #for each line
    for line in testFile:
        parsedLine = line.split('\t')
        #if we don't already have the user in the dictionary, initialize their entry with a list of movies to rate.
        if int(parsedLine[0]) not in testRatings:
            testRatings[int(parsedLine[0])] = list()
        #for each user, add the indexes of the movies they need predicted.
        testRatings[int(parsedLine[0])].append(int(parsedLine[1]))
        #keep the actual ratings for each user as well.
        actualRatings.append(float(parsedLine[2]))

    #now, predict the ratings for each user, and find the mean squared error.
    meanSquaredError = 0.0
    index = 0
    iteration = 0
    numUsers = float(len(testRatings))
    for user in testRatings:
        prediction = kNeighbor.kNearestNeighborsPrediction(user, k, testRatings[user])
        #print prediction
        for i in range(len(prediction)):
            #print 'difference of', prediction[i], '-', actualRatings[index], '=', prediction[i] - actualRatings[index]
            meanSquaredError += (prediction[i] - actualRatings[index]) ** 2
            index+=1
        iteration+=1
        percentDone = round((float(iteration)/numUsers) * 100, 2)
        sys.stdout.write('Progress: [%.2f%%]\r'%percentDone)
        sys.stdout.flush()

    meanSquaredError = meanSquaredError/len(actualRatings)
    print ''
    print 'Mean Squared Error:', meanSquaredError


main()
