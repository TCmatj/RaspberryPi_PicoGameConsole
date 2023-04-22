from machine import Pin,SPI,PWM,ADC
import framebuf
import utime
import time
import math
import random
import _thread
from Lcd import LCD

class SnakeHead:
    def __init__(self, LEFT_PIN, RIGHT_PIN, UP_PIN, DOWN_PIN, MIDDLE, ADC1, ADC2):
        self.snake_pos = [(160, 85),(161,85),(162, 85),(163,85),(164, 85),(165,85)]
        self.level = 0
        self.score = 0
        self.direction = 'RIGHT'
        self.apple_x = random.randint(4, 315)
        self.apple_y = random.randint(4, 168)
        self.left_key = Pin(LEFT_PIN, Pin.IN, Pin.PULL_UP)  # 左键
        self.right_key = Pin(RIGHT_PIN, Pin.IN, Pin.PULL_UP)# 右键
        self.up_key = Pin(UP_PIN, Pin.IN, Pin.PULL_UP)      # 上键
        self.down_key = Pin(DOWN_PIN, Pin.IN, Pin.PULL_UP)  # 下键
        self.press = Pin(MIDDLE, Pin.IN, Pin.PULL_UP)       # 中键
        self.adc1 = ADC(Pin(ADC1))                          #水平方向
        self.adc2 = ADC(Pin(ADC2))                          #垂直方向
        self.event = {'key': None}

    def event_listener(self):
        running = True
        while running:
            adc1 = self.adc1.read_u16()
            adc2 = self.adc2.read_u16()
            if not self.left_key.value() or adc1 > 55000:
                self.event['key'] = 'LEFT'
            elif not self.right_key.value() or adc1 < 5000:
                self.event['key'] = 'RIGHT'
            elif not self.up_key.value() or adc2 < 5000:
                self.event['key'] = 'UP'
            elif not self.down_key.value() or adc2 > 55000:
                self.event['key'] = 'DOWN'
            utime.sleep_ms(100)
            if LCD.state == 2:
                running = False 

    def draw_snake(self, color=0x07E0):
        for pos in self.snake_pos:
            #LCD.pixel(pos[0], pos[1], color)
            LCD.fill_ellipse(pos[0], pos[1], 2, 2, color)

    def draw_apple(self, color=0xffff):
        if self.apple_pos != None:
            LCD.fill_ellipse(self.apple_pos[0], self.apple_pos[1], 2, 2, color)
    

    def external_interrupt(self,key):
            # 消除抖动
        time.sleep(0.1)
        # 再次判断按键是否被按下
        if key.value() == 0:
            # print('The button is pressed:',key)
            if key == self.up_key:
                if self.direction in ['LEFT', 'RIGHT']:
                    self.direction = 'UP'
            elif key == self.down_key:
                if self.direction in ['LEFT', 'RIGHT']:
                    self.direction = 'DOWN'
            elif key == self.left_key:
                if self.direction in ['UP', 'DOWN']:
                    self.direction = 'LEFT'
            elif key == self.right_key:
                if self.direction in ['UP', 'DOWN']:
                    self.direction = 'RIGHT'


    def diff(self):
        #求最小相对距离
        diff_x = self.apple_pos[0] - self.snake_pos[-1][0]
        diff_y = self.apple_pos[1] - self.snake_pos[-1][1]
        
        return math.sqrt(math.fabs(diff_y * diff_y + diff_x * diff_x))
    
    def move_snake(self):
        # print(self.snake_pos)
        if self.direction == 'RIGHT':
            # print("R")
            new_head = (self.snake_pos[-1][0] + 2 , self.snake_pos[-1][1])
        elif self.direction == 'LEFT':
            # print("L")
            new_head = (self.snake_pos[-1][0] - 2 , self.snake_pos[-1][1])
        elif self.direction == 'UP':
            # print("U")
            new_head = (self.snake_pos[-1][0], self.snake_pos[-1][1] - 2 )
        elif self.direction == 'DOWN':
            # print("D")
            new_head = (self.snake_pos[-1][0], self.snake_pos[-1][1] + 2 )

        # 检查是否撞到墙壁
        if new_head[0] < 4 or new_head[0] >= 314 or new_head[1] < 4 or new_head[1] >= 168:
            # print('1-False')
            return False

        # 检查是否撞到自己的身体
        for pos in self.snake_pos[:-1]:
            if pos == new_head:
                # print('2-False')
                return False
        
        self.snake_pos.append(new_head)

        # 吃掉苹果
        if self.diff() <= 2:
            LCD.fill_ellipse(self.apple_pos[0] ,self.apple_pos[1], 2, 2, LCD.BLACK)
            self.generate_apple()
            self.score += 1
            LCD.fill_rect(90,2,226,20,LCD.BLACK)
            LCD.fill_rect(90,1,228,3,LCD.RED)
            LCD.write_text("L:", 150, 2, 2,LCD.WHITE)
            LCD.write_text("H:", 230, 2, 2,LCD.WHITE)
            if(self.score % 10 == 0):
                self.level = self.level + 1
            
            LCD.write_text(str(self.level), 180, 2, 2,LCD.WHITE)
            LCD.write_text(str(self.score), 100, 1, 2,LCD.WHITE)
        else:
            LCD.fill_ellipse(self.snake_pos[0][0] ,self.snake_pos[0][1], 2, 2, LCD.BLACK)
            #LCD.pixel(self.snake_pos[0][0],self.snake_pos[0][1],LCD.BLACK)
            self.snake_pos.pop(0)
        
        return True

    def generate_apple(self):
        while True:
            x = utime.ticks_ms() % 311
            y = utime.ticks_us() % 163
            if (x, y) not in self.snake_pos:
                self.apple_pos = (x+5, y+5)
                break

    def play(self):
        self.draw_snake()
        self.generate_apple()
        LCD.write_text("Score:0", 5, 2, 2,LCD.WHITE)
        # 开启新的线程来监听按键输入
        _thread.start_new_thread(self.event_listener, ())
        while True:
            # 如果收到事件，则更新贪吃蛇方向
            if self.event['key'] != None:
                new_direction = self.event['key']
                if (new_direction, self.direction) not in [('LEFT', 'RIGHT'), ('RIGHT', 'LEFT'), ('UP', 'DOWN'), ('DOWN', 'UP')]:
                    self.direction = new_direction
                self.event['key'] = None

            utime.sleep_ms(100)
            for _ in range(self.level + 1):
                # 移动贪吃蛇
                success = self.move_snake()
                # print(self.direction)

                # 绘制游戏场景
                self.draw_snake()
                self.draw_apple()

                LCD.show()

                # 检查游戏状态
                if not success:
                    # print('end')
                    break

            else:
                continue
            break
        self.game_over()

    def game_over(self):
        LCD.state = 2
        LCD.write_text("Game Over",20,60,4,LCD.RED)
        LCD.write_text("Wait 3s to return!",80,90,1,LCD.RED)
        LCD.show()
        time.sleep(1)
        LCD.fill_rect(5,90,312,30,LCD.BLACK)
        LCD.write_text("Wait 2s to return!",80,90,1,LCD.RED)
        LCD.show()
        time.sleep(1)
        LCD.fill_rect(5,90,312,30,LCD.BLACK)
        LCD.write_text("Wait 1s to return!",80,90,1,LCD.RED)
        LCD.show()
        time.sleep(1)
        LCD.init()
        LCD.state = 0
        self.snake_pos = [(160, 85),(161,85),(162, 85),(163,85),(164, 85),(165,85)]
        self.level = 0
        self.score = 0
