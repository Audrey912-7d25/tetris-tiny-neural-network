from tetris import *
import numpy as np
import random


class NetworkCPU:
    def __init__(self, config, lowerbound, upperbound):
        self.config = config
        self.lowerbound = lowerbound
        self.upperbound = upperbound
        self.networks = self.loadNetworks()
        self.tetrisGames = self.loadTetrisGames()

        for _ in range(100):
            index = 0
            self.stepTetris(index)
            print(self.tetrisGames[index])


    def trainTetris(self, index):
        for _ in range(self.config.attemptsPerPlayer):
            self.stepTetris(self.tetrisGames[index], index)
            firstLayer = self.computeFirstLayer(self.tetrisGames[index])
            movement = int(np.argmax(self.computeNetwork(firstLayer, index)))

            # some bullshit here

            #self.tetris.move(decision)

    def stepTetris(self, index):
        firstLayer = self.computeFirstLayer(self.tetrisGames[index])
        movement = Direction(int(np.argmax(self.computeNetwork(firstLayer, index))) + 1)
        self.tetrisGames[index].move(movement)



    def loadNetworks(self):
        networks = []
        for i in range(self.lowerbound, self.upperbound):
            try:
                networks.append(np.load(self.config.networkDirectoryAll+str(self.lowerbound + i)+".npy", allow_pickle=True))
            except:
                np.save(self.config.networkDirectoryAll+str(self.lowerbound + i), self.newNetwork(), allow_pickle=True)
                networks.append(np.load(self.config.networkDirectoryAll+str(self.lowerbound + i)+".npy", allow_pickle=True))
        return networks


    def newNetwork(self):
        networkList = [np.zeros(self.config.networkInputSize * self.config.networkStructure[0], dtype=bool),np.zeros(self.config.networkStructure[0], dtype=int)]
        for i in range(len(self.config.networkStructure)):
            if i != len(self.config.networkStructure) - 1:
                networkList.append(np.zeros(self.config.networkStructure[i] * self.config.networkStructure[i+1], dtype=bool))
                networkList.append(np.zeros(self.config.networkStructure[i+1], dtype=int))
            else:
                networkList.append(np.zeros(self.config.networkStructure[i] * self.config.networkOutputSize, dtype=bool))
                networkList.append(np.zeros(self.config.networkOutputSize, dtype=int))
        network = np.array(networkList, dtype=object)
        for i in range(len(network)):
            if i % 2 == 1:
                for k in range(len(network[i])):
                    network[i][k] = random.randint(2, int((int(len(network[i - 1]) / len(network[i])) - 2)/1.25))
            else:
                for k in range(len(network[i])):
                    network[i][k] = random.choice([True, False])
        return network


    def computeFirstLayer(self, tetris):
        firstLayer = np.zeros(self.config.networkInputSize,dtype=bool)
        # first 16 are the bits of the piece hot encoded
        # 0-15, 16
        for y in range(len(tetris.sprite)):
            for x in range(len(tetris.sprite[y])):
                if tetris.sprite[y][x] != 0:
                    firstLayer[y*4 + x] = True
        # then 16-22 are the piece,
        firstLayer[15 + tetris.currentPiece] = True
        print(15 + tetris.currentPiece)
        # then 23-26 are the rotation
        firstLayer[23 + tetris.rotation] = True
        print(23 + tetris.rotation)
        # 27-37 is the position x
        firstLayer[29 + tetris.x] = True
        print(29 + tetris.x)
        # 38-59 is the position y
        firstLayer[41 + tetris.y] = True
        print(41 + tetris.y)
        # 60-159 is the distance from the sprite to the next saved bit on the board/distance to the board relative to the sprite

        return firstLayer


    def computeNetwork(self, firstLayer, index):
        network = self.networks[index]
        layers = []
        thresholds = []
        weights = []
        output = np.zeros(self.config.networkOutputSize)
        for i in range(len(network)):
            if i%2 == 1:
                thresholds.append(network[i])
                layers.append(np.zeros(len(network[i]), dtype=bool))
            else:
                weights.append(network[i])
        for i in range(len(network[1])):
            counter = 0
            for k in range(len(network[0]) // len(network[1])):
                if self.xnor(network[0][(i * (len(network[0]) // len(network[1]))) + k], firstLayer[k]):
                    counter += 1
            if counter >= thresholds[0][i]:
                layers[0][i] = True
        for i in range(2, len(network)):   # k = 0-12 j = 0 = 24
            if i%2 == 1: #12, 5
                currentBits = len(network[i])
                previousBits = (len(network[i - 1]) // len(network[i]))
                previousLayerIndex = i//2 - 1
                for k in range(currentBits): #0-12
                    counter = 0
                    for j in range(previousBits): #0-24
                        if self.xnor(layers[previousLayerIndex][j], network[i-1][k * previousBits + j]):
                            counter += 1
                    if len(layers[i // 2]) == self.config.networkOutputSize:
                        output[k] = counter
                    else:
                        layers[i // 2][k] = counter >= thresholds[i // 2][k]
        print(output)
        return output


    def xnor(self, a, b):
        return a==b


    def loadTetrisGames(self):
        tetrisList = []
        for i in range(self.lowerbound, self.upperbound):
            tetrisList.append(Tetris(self.config))
        return tetrisList
