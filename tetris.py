import numpy as np
import random
from enum import Enum

class Config:
    def __init__ (self):
        self.threads = 32
        self.playersPerThread = 256
        self.attemptsPerPlayer = 16384

        self.networkStructure = np.array([64, 64, 32, 32, 16, 16, 8, 8, 8])
        # the network is gonna be something like
        # first 16 is the column height relative to the piece. if it is a wall its just the max. idk if we are doing max of 128 or 256 but it woudl just be that.
        # next 16 are the bits of the piece hot-encoded
        # next 7 are the sprite hot-encoded
        # next 4 are the rotation hot-encoded
        # next 12 are x position hot-encoded
        # next 19 are y position hot-encoded
        # then the next 4 are the distances from the sprite to the next saved bit on the board for each vertical column. if no sprite bit then max val again.
        # 78 total
        self.networkInputSize = 78
        self.networkOutputSize = 5

class Tetris:
    def __init__ (self, seed, network, inputLayer, attempts, training):
        self.l = np.array([[0, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]])
        self.j = np.array([[0, 0, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
        self.t = np.array([[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]])
        self.i = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]])
        self.z = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [0, 0, 0, 0]])
        self.s = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]])
        self.c = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
        self.board = np.zeros((20, 10))
        self.sprite = self.t
        self.bag = [1, 2, 4, 5, 6, 7]
        self.rotation = 0
        self.x = 4 #   4
        self.y = -3 # -3
        self.seed = seed
        self.network = network
        self.inputLayer = inputLayer
        self.reward = 0
        self.score = 0
        self.games_left = attempts
        self.training = training

    def move(self, movement):
        match movement:


            case Direction.DOWN:
                allowMoveDown = True
                for y in range(0, len(self.sprite)):
                    for x in range(0, len(self.sprite[y])):
                        if self.sprite[y][x] != 0:
                            if not(20 > self.y+y+1 > 0 and self.board[y + self.y + 1][x + self.x] == 0) and not(self.y+y < -1 or (self.y+y == -1 and self.board[y + self.y + 1][x + self.x] == 0)):
                                allowMoveDown = False
                if allowMoveDown:
                    self.y += 1
                else:
                    self.spriteOnGround()


            case Direction.LEFT:
                allowMoveLeft = True
                for y in range(0, len(self.sprite)):
                    for x in range(0, len(self.sprite[y])):
                        if self.sprite[y][x] != 0:
                            if 0 > self.x+x-1 or (self.board[y+self.y][x+self.x - 1] != 0 and y+self.y >= 20):
                                allowMoveLeft = False
                if allowMoveLeft:
                    self.x -= 1
                else:
                    print("what the fuck ro")


            case Direction.RIGHT:
                allowMoveRight = True
                for y in range(0, len(self.sprite)):
                    for x in range(0, len(self.sprite[y])):
                        if self.sprite[y][x] != 0:
                            if 10 <= self.x+x+1 or (self.board[y+self.y][x+self.x + 1] != 0 and y+self.y >= 20):
                                allowMoveRight = False
                if allowMoveRight:
                    self.x += 1
                else:
                    print("what the fuck ro")


            case Direction.ROTATE:
                allowMoveRotate = True
                testSprite = self.getRotated()
                for y in range(0, len(testSprite)):
                    for x in range(0, len(testSprite[y])):
                        if testSprite[y][x] != 0:
                            if not(10 > self.x+x >= 0 and 20 > self.y+y):
                                allowMoveRotate = False
                if allowMoveRotate:
                    self.rotation += 1
                    if self.rotation >= 4:
                        self.rotation = 0
                    self.sprite = self.getRotated()


    def getRotated(self):
        return np.rot90(self.sprite, k=-1)


    def spriteOnGround(self):
        for y in range(0, len(self.sprite)):
            for x in range(0, len(self.sprite[y])):
                if self.sprite[y][x] != 0:
                    self.board[y+self.y][x+self.x] = self.sprite[y][x]
        self.newPiece()
        self.giveReward(Reward.Place)


        for y in range(0, len(self.board)):
            sum = 0
            for x in range(0, len(self.board[y])):
                if self.board[y][x] != 0:
                    sum += 1
            if sum >= 10:
                for k in range(y, 1, -1):
                    for x in range(0, len(self.board[y])):
                        self.board[k][x] = self.board[k - 1][x]
                for x in range(0, 10):
                    self.board[0][x] = 0


    def giveReward(self, reward):
        match reward:


            case Reward.Place:
                self.reward += 10


    def newPiece(self):
        self.x = 4
        self.y = -3
        self.rotation = 0
        popPiece = random.randrange(len(self.bag))
        self.bag.pop(popPiece)
        if len(self.bag) == 0:
            self.bag = [1, 2, 3, 4, 5, 6, 7]
        print(self.bag)




    def __repr__ (self):
        display = np.zeros((20, 10))
        for y in range(0, len(self.board)):
            for x in range(0, len(self.board[y])):
                if self.board[y][x] != 0:
                    display[y][x] = self.board[y][x]
        for y in range(0, len(self.sprite)):
            for x in range(0, len(self.sprite[y])):
                if self.sprite[y][x] != 0 and 20 > y + self.y >= 0 and 10 > x+self.x >= 0:
                    display[y + self.y][x + self.x] = self.sprite[y][x]
        print(display)
        print(f"[{self.x},{self.y}]")
        return ""


class Direction(Enum):
    DROP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    ROTATE = 5


class Reward(Enum):
    Place = 1
    LineClear = 2
    GameOver = 3
    MakeHole = 4
    PlacePiece = 5

