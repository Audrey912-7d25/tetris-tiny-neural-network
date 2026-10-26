import numpy as np
import numba
from enum import Enum
from tetris import *
from network import *


class Config:
    def __init__ (self):
        self.threads = 32
        self.playersPerThread = 256

        self.gpuThreads = 128
        self.PlayersPerGPUThread = 1024
        self.numberOfGPUs = 2

        self.attemptsPerPlayer = 16384

        self.networkStructure = np.array([24, 12])
        # the network is gonna be something like
        # first 16 is the column height relative to the piece. if it is a wall its just the max. idk if we are doing max of 128 or 256 but it woudl just be that.
        # next 16 are the bits of the piece hot-encoded
        # next 7 are the sprite hot-encoded
        # next 4 are the rotation hot-encoded
        # next 11 are x position hot-encoded
        # next 21 are y position hot-encoded
        # then the next 4 are the distances from the sprite to the next saved bit on the board for each vertical column. if no sprite bit then max val again.
        # 78 total
        self.networkInputSize = 159
        self.networkOutputSize = 5

        self.networkDirectoryAll = "networks/network"
        self.networkDirectoryBest = "best/best"

        self.gameOverReward = -20
        self.piecePlaceReward = 1
        self.lineClearReward = 80
        self.makeHoleReward = 2
        self.placedFlatReward = 12

        self.seed = random.getrandbits(32)


def main ():
    #config = Config()
    #tetris = Tetris(config)
    #for _ in range(14):
    #    tetris.move(Direction.DROP)
    #print(tetris)
    lowerbound = 0
    upperbound = 5
    config = Config()
    network = NetworkCPU(config, lowerbound, upperbound)

main()
