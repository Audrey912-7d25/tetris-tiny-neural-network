import numpy as np
import numba
from enum import Enum
from tetris import *

def main ():
    seed = 0
    network = 0
    inputLayer = 0
    config = Config()
    tetris = Tetris(seed, network, inputLayer, config.attemptsPerPlayer, True)
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    tetris.newPiece()
    print(tetris)

main()
