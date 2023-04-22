from snake import SnakeHead
from Lcd import LCD,LEFT_PIN, RIGHT_PIN, UP_PIN, DOWN_PIN, MIDDLE, ADC1, ADC2, BL


class Games:

    def __init__(self):
        self.games = ["Snake","Null1","Null2"]
        self.gameIdex = 0

    def startGame(self):
        start = self.games[self.gameIdex]
        print(start)
        if start == "Snake":
            snake = SnakeHead(LEFT_PIN, RIGHT_PIN, UP_PIN, DOWN_PIN, MIDDLE, ADC1, ADC2)
            snake.play()
        else:
            self.gameIdex = 0
            LCD.state == 0
            LCD.init()