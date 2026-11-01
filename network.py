from tetris import *
import numpy as np
from numba.typed import List
from numba import njit
import random
import time


class NetworkCPU:
    def __init__(self, config, lowerbound, upperbound):
        self.config = config
        self.lowerbound = lowerbound
        self.upperbound = upperbound
        self.biases, self.thresholds = self.loadNetworks()
        self.tetrisGames = self.loadTetrisGames()
        self.packedBiases = [packNetwork(self.biases[i], self.thresholds[i])for i in range(len(self.biases))]
        self.biases = self.packedBiases

        index = 0
        self.stepTetris(index)
        self.tetrisGames[index].move(Direction(int(np.argmax(computeNetwork(self.biases[index], self.thresholds[index], self.config.networkOutputSize, self.config.networkInputSize, self.tetrisGames[index].sprite, self.tetrisGames[index].currentPiece, self.tetrisGames[index].rotation, self.tetrisGames[index].x, self.tetrisGames[index].y, self.tetrisGames[index].board))) + 1))

        print("Starting games")
        for _ in range(6):
            for _ in range(5):
                start = time.perf_counter()
                while self.tetrisGames[index].losses <= self.config.attemptsPerPlayer - 1:
                    self.stepTetris(index)
                elapsed = time.perf_counter() - start
                print(self.config.attemptsPerPlayer/elapsed, "games/second for", self.config.attemptsPerPlayer, "games")
                print(self.tetrisGames[index].score)
                self.tetrisGames = self.loadTetrisGames()
                self.config.seed = random.getrandbits(32)
            self.config.attemptsPerPlayer *= 2
            self.tetrisGames = self.loadTetrisGames()
            self.config.seed = random.getrandbits(32)


    def loadNetworks(self):
        weights = []
        thresholds = []
        for i in range(self.lowerbound, self.upperbound):
            weightPath = self.config.networkDirectoryAll + str(self.lowerbound + i) + "_weights_.npy"
            thresholdPath = self.config.networkDirectoryAll + str(self.lowerbound + i) + "_thresholds_.npy"
            try:
                weights.append(self.loadTypedList(weightPath, np.bool_))
            except FileNotFoundError:
                self.saveTypedList(weightPath,self.newNetworkBiases())
                weights.append(self.loadTypedList(weightPath, np.bool_))
            try:
                thresholds.append(self.loadTypedList(thresholdPath, np.int64))
            except FileNotFoundError:
                self.saveTypedList(thresholdPath,self.newNetworkThresholds())
                thresholds.append(self.loadTypedList(thresholdPath, np.int64))
        return weights, thresholds


    def loadTetrisGames(self):
        tetrisList = []
        for i in range(self.lowerbound, self.upperbound):
            tetrisList.append(Tetris(self.config))
        return tetrisList


    def saveTypedList(self, path, data):
        saved = np.empty(len(data), dtype=object)
        for i in range(len(data)):
            saved[i] = data[i]
        np.save(path, saved, allow_pickle=True)

    def loadTypedList(self, path, dtype):
        loaded = np.load(path, allow_pickle=True)
        result = List()
        for layer in loaded:
            result.append(np.asarray(layer, dtype=dtype))
        return result


    def newNetworkBiases(self):
        biases = List()
        layerSizes = [self.config.networkInputSize]
        layerSizes.extend(self.config.networkStructure)
        layerSizes.append(self.config.networkOutputSize)
        for i in range(len(layerSizes) - 1):
            size = layerSizes[i] * layerSizes[i + 1]
            layer = np.zeros(size, dtype=np.bool_)
            for k in range(size):
                layer[k] = random.choice([True, False])
            biases.append(layer)
        return biases


    def newNetworkThresholds(self):
        thresholds = List()
        layerSizes = []
        for i in range(len(self.config.networkStructure)):
            layerSizes.append(self.config.networkStructure[i])
        layerSizes.append(self.config.networkOutputSize)
        for i in range(len(layerSizes)):
            layer = np.zeros(layerSizes[i], dtype=int)
            for k in range(layerSizes[i]):
                lastLayerLength = 0
                if i == 0:
                    lastLayerLength = self.config.networkInputSize
                else:
                    lastLayerLength = layerSizes[i - 1]
                layer[k] = random.randint(2, int(lastLayerLength/1.25))
            thresholds.append(layer)
        return thresholds


    def stepTetris(self, index):
        self.tetrisGames[index].move(Direction(int(np.argmax(computeNetwork(self.biases[index], self.thresholds[index], self.config.networkOutputSize, self.config.networkInputSize, self.tetrisGames[index].sprite, self.tetrisGames[index].currentPiece, self.tetrisGames[index].rotation, self.tetrisGames[index].x, self.tetrisGames[index].y, self.tetrisGames[index].board))) + 1))
        self.tetrisGames[index].clock += 1
        if self.tetrisGames[index].clock >= self.tetrisGames[index].config.clockCyclesPerForcedFall:
            self.tetrisGames[index].clock = 0
            self.tetrisGames[index].move(Direction.DOWN)

    def runNetwork(self, index):
        while self.tetrisGames[index].losses <= self.config.attemptsPerPlayer - 1:
            self.stepTetris(index)
        return self.tetrisGames[index].score



def packNetwork(biases, thresholds):
    packedLayers = []
    previousBits = 180
    for layer in range(len(biases)):
        neuronCount = len(thresholds[layer])
        groups = (neuronCount + 3) // 4
        chunks = (previousBits + 15) // 16
        packed = np.zeros((groups, chunks), dtype=np.uint64)
        for neuron in range(neuronCount):
            group = neuron // 4
            lane = neuron % 4
            for inputIndex in range(previousBits):
                if biases[layer][neuron * previousBits + inputIndex]:
                    chunk = inputIndex // 16
                    bit = lane * 16 + inputIndex % 16
                    packed[group, chunk] |= (np.uint64(1) << np.uint64(bit))
        packedLayers.append(packed)
        previousBits = neuronCount
    return tuple(packedLayers)

@njit(cache=True, inline="always")
def popcount4x16(x):
    x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
    x = ((x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2))& np.uint64(0x3333333333333333)))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    x = (x + (x >> np.uint64(8))) & np.uint64(0x00FF00FF00FF00FF)
    return x

@njit(cache=True, inline="always")
def runPackedLayer(
    inputChunks, packedWeights,
    thresholds, inputCount,
    neuronCount, useThreshold):
    groups = (neuronCount + 3) // 4
    chunkCount = inputChunks.shape[0]
    activations = np.uint64(0)
    outputCounts = np.uint64(0)
    for group in range(groups):
        accumulated = np.uint64(0)
        for chunk in range(chunkCount):
            remaining = inputCount - chunk * 16
            validBits = min(remaining, 16)
            baseMask = (
                (np.uint64(1) << np.uint64(validBits)) - np.uint64(1))
            laneMask = (
                baseMask
                | (baseMask << np.uint64(16))
                | (baseMask << np.uint64(32))
                | (baseMask << np.uint64(48))
            )
            inputWord = (
                inputChunks[chunk] * np.uint64(0x0001000100010001))
            matches = ~(packedWeights[group, chunk] ^ inputWord)
            matches &= laneMask
            accumulated += popcount4x16(matches)
        for lane in range(4):
            neuron = group * 4 + lane
            if neuron < neuronCount:
                count = (accumulated >> np.uint64(lane * 16)) & np.uint64(0xFF)
                if useThreshold:
                    if count >= np.uint64(thresholds[neuron]):
                        activations |= (np.uint64(1) << np.uint64(neuron))
                else:
                    outputCounts |= (count << np.uint64(lane * 16))
    if useThreshold:
        return activations
    else:
        return outputCounts

@njit(cache=True)
def computeNetwork(
    biases, thresholds,
    networkOutputSize,
    inputSize, sprite,
    currentPiece,
    rotation, x, y,
    board):
    firstLayer = np.zeros(inputSize, dtype=np.bool_)
    for sy in range(4):
        for sx in range(4):
            if sprite[sy][sx] != 0:
                firstLayer[sy * 4 + sx] = True
    firstLayer[15 + currentPiece] = True
    firstLayer[23 + rotation] = True
    firstLayer[29 + x] = True
    firstLayer[41 + y] = True
    xVal = x - 8
    for i in range(20):
        counter = 0
        if 0 <= xVal <= 9:
            while (counter + 1 + y < 20 and (y + counter + 1 < 0 or board[y + counter + 1][xVal] == 0)):
                counter += 1
            value = counter
        else:
            value = 26
        for bit in range(5):
            firstLayer[60 + i * 5 + bit] = ((value >> bit) & 1)
        xVal += 1
    y_offset = np.zeros(4, dtype=np.int64)
    foundBit = np.zeros(4, dtype=np.bool_)
    for sx in range(4):
        for sy in range(4):
            if sprite[sy][sx] != 0:
                y_offset[sx] = sy
                foundBit[sx] = True
    for i in range(4):
        value = 31
        if foundBit[i]:
            xVal = x + i
            yVal = y + y_offset[i]
            if 0 <= xVal <= 9:
                counter = 0
                while (
                    counter + 1 + yVal < 20 and (yVal + counter + 1 < 0 or board[yVal + counter + 1][xVal] == 0)):
                    counter += 1

                value = counter
            else:
                value = 26

        for bit in range(5):
            firstLayer[60 + (20 + i) * 5 + bit] = ((value >> bit) & 1)
    inputChunks = np.zeros((inputSize + 15) // 16,dtype=np.uint64)

    for i in range(inputSize):
        if firstLayer[i]:
            inputChunks[i // 16] |= (np.uint64(1) << np.uint64(i % 16))
    firstActivations = runPackedLayer(
        inputChunks,
        biases[0],
        thresholds[0],
        inputSize,
        24,
        True
    )
    secondInput = np.zeros(2, dtype=np.uint64)

    secondInput[0] = (firstActivations & np.uint64(0xFFFF))

    secondInput[1] = (firstActivations >> np.uint64(16))
    secondActivations = runPackedLayer(
        secondInput,
        biases[1],
        thresholds[1],
        24,
        12,
        True
    )
    thirdInput = np.zeros(1, dtype=np.uint64)

    thirdInput[0] = (secondActivations & np.uint64(0xFFF))
    packedOutput = runPackedLayer(
        thirdInput,
        biases[2],
        thresholds[2],
        12,
        networkOutputSize,
        False)
    output = np.zeros(networkOutputSize,dtype=np.int64)

    for i in range(networkOutputSize):
        output[i] = (packedOutput >> np.uint64(i * 16)) & np.uint64(0xFF)

    return output

