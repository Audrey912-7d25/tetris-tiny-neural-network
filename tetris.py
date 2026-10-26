import numpy as np
import random
from enum import Enum

class Tetris:
    def __init__ (self, config):
        self.l = np.array([[0, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]])
        self.j = np.array([[0, 0, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
        self.t = np.array([[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]])
        self.i = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]])
        self.z = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [0, 0, 0, 0]])
        self.s = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]])
        self.c = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
        self.config = config
        self.board = np.zeros((20, 10))
        self.sprite = self.t
        self.currentPiece = 3
        self.bag = [1, 2, 4, 5, 6, 7]
        self.rotation = 0
        self.x = 4  #  4
        self.y = -3 # -3
        self.losses = 0
        self.reward = 0
        self.score = 0
        self.piecesPlaced = 0
        self.gamesToPlay = self.config.attemptsPerPlayer


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

            case Direction.RIGHT:
                allowMoveRight = True
                for y in range(0, len(self.sprite)):
                    for x in range(0, len(self.sprite[y])):
                        if self.sprite[y][x] != 0:
                            if 10 <= self.x+x+1 or (self.board[y+self.y][x+self.x + 1] != 0 and y+self.y >= 20):
                                allowMoveRight = False
                if allowMoveRight:
                    self.x += 1

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

            case Direction.DROP:
                lastHeight = self.y
                while self.y >= lastHeight:
                    lastHeight = self.y
                    self.move(Direction.DOWN)


    def getRotated(self):
        return np.rot90(self.sprite, k=-1)


    def spriteOnGround(self):
        spriteInScreenLimits = True
        for y in range(0, len(self.sprite)):
            for x in range(0, len(self.sprite[y])):
                if self.sprite[y][x] != 0 and y+self.y < 0:
                    spriteInScreenLimits = False
        if spriteInScreenLimits:
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
        else:
            self.gameOver()


    def gameOver(self):
        self.losses += 1
        self.board = np.zeros((20, 10))
        self.sprite = self.t
        self.currentPiece = 3
        self.bag = [1, 2, 4, 5, 6, 7]
        self.rotation = 0
        self.x = 4 #   4
        self.y = -3 # -3

        self.giveReward(Reward.GameOver)
        self.score += self.reward / self.gamesToPlay
        self.reward = 0
        self.piecesPlaced = self.losses * 100


    def giveReward(self, reward):
        match reward:

            case Reward.Place:
                self.reward += self.config.piecePlaceReward

            case Reward.GameOver:
                self.reward += self.config.gameOverReward

            case Reward.LineClear:
                self.reward += self.lineClearReward


    def newPiece(self):
        self.x = 4
        self.y = -3
        self.rotation = 0
        random.seed(self.config.seed + self.piecesPlaced)
        popPiece = random.randrange(len(self.bag))
        self.sprite = self.getPieceFromIndex(self.bag[popPiece])
        self.currentPiece = self.bag[popPiece]
        self.bag.pop(popPiece)
        if len(self.bag) == 0:
            self.bag = [1, 2, 3, 4, 5, 6, 7]
        self.piecesPlaced += 1


    def getPieceFromIndex(self, index):
        match index:
            case 1:
                return self.l
            case 2:
                return self.j
            case 3:
                return self.t
            case 4:
                return self.i
            case 5:
                return self.z
            case 6:
                return self.s
            case 7:
                return self.c


    def __repr__ (self):
        output = ""
        display = [[('\u2588') for i in range(10)] for j in range(20)]
        for y in range(0, len(self.board)):
            for x in range(0, len(self.board[y])):
                if self.board[y][x] != 0:
                    display[y][x] = ('\u2591')
        for y in range(0, len(self.sprite)):
            for x in range(0, len(self.sprite[y])):
                if self.sprite[y][x] != 0 and 20 > y + self.y >= 0 and 10 > x+self.x >= 0:
                    display[y + self.y][x + self.x] = ('\u2591')
        for y in range(20):
            printout = ""
            for x in range(10):
                output += str(display[y][x]) + str(display[y][x])
            output += "\n"
        output += f"[{self.x},{self.y}, piece:{self.currentPiece}, rotation:{self.rotation}, reward:{self.reward}, score:{self.score * (self.gamesToPlay - (self.losses-1))}, attempts left: {self.gamesToPlay - self.losses}]\n"
        return output


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
