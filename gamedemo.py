from machine import Pin,SPI,PWM,ADC
import framebuf
import utime
import time
import math
import random
import _thread

BL = 16
DC = 20
RST = 19
MOSI = 3
SCK = 2
CS = 5
# 按键定义
LEFT_PIN = 8
RIGHT_PIN = 7
UP_PIN = 22
DOWN_PIN = 21

#摇杆定义
ADC1 = 27       # 水平方向  初始值： 32767 附近，左加右减 0-65535
ADC2 = 28       # 垂直方向  初始值： 32767 附近，下加上减 0-65535
MIDDLE = 26     # 摇杆中键  初始值： 1     按下为 0 



class LCD_1inch47(framebuf.FrameBuffer):
    
    def __init__(self):
        self.width = 320
        self.height = 172
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(0,1000_000)
        self.spi = SPI(0,100000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000

        self.state = 0
        self.gameIdex = 0
        self.games = ['Snake','Null1','NULL2']
        class SnakeHead:
            def __init__(self, outer):
                self.snake_pos = [(160, 85),(161,85),(162, 85),(163,85),(164, 85),(165,85)]
                self.level = 0
                self.score = 0
                self.outer = outer
                self.direction = 'RIGHT'
                self.apple_x = random.randint(4, 315)
                self.apple_y = random.randint(4, 168)
                self.left_key = Pin(LEFT_PIN, Pin.IN, Pin.PULL_UP) # 左键
                self.right_key = Pin(RIGHT_PIN, Pin.IN, Pin.PULL_UP)# 右键
                self.up_key = Pin(UP_PIN, Pin.IN, Pin.PULL_UP)   # 上键
                self.down_key = Pin(DOWN_PIN, Pin.IN, Pin.PULL_UP) # 下键
                self.event = {'key': None}

            def event_listener(self):
                running = True
                while running:
                    if not self.left_key.value():
                        self.event['key'] = 'LEFT'
                    elif not self.right_key.value():
                        self.event['key'] = 'RIGHT'
                    elif not self.up_key.value():
                        self.event['key'] = 'UP'
                    elif not self.down_key.value():
                        self.event['key'] = 'DOWN'
                    utime.sleep_ms(100)
                    if LCD.state == 2:
                        running = False 

            def draw_snake(self, color=0x07E0):
                for pos in self.snake_pos:
                    #self.outer.pixel(pos[0], pos[1], color)
                    self.outer.fill_ellipse(pos[0], pos[1], 2, 2, color)

            def draw_apple(self, color=0xffff):
                if self.apple_pos != None:
                    self.outer.fill_ellipse(self.apple_pos[0], self.apple_pos[1], 2, 2, color)
            

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
                    self.outer.fill_ellipse(self.apple_pos[0] ,self.apple_pos[1], 2, 2, LCD.BLACK)
                    self.generate_apple()
                    self.score += 1
                    self.outer.fill_rect(90,2,226,20,LCD.BLACK)
                    self.outer.fill_rect(90,1,228,3,LCD.RED)
                    self.outer.write_text("L:", 150, 2, 2,LCD.WHITE)
                    self.outer.write_text("H:", 230, 2, 2,LCD.WHITE)
                    if(self.score % 10 == 0):
                        self.level = self.level + 1
                    
                    self.outer.write_text(str(self.level), 180, 2, 2,LCD.WHITE)
                    self.outer.write_text(str(self.score), 100, 1, 2,LCD.WHITE)
                else:
                    self.outer.fill_ellipse(self.snake_pos[0][0] ,self.snake_pos[0][1], 2, 2, LCD.BLACK)
                    #self.outer.pixel(self.snake_pos[0][0],self.snake_pos[0][1],self.outer.BLACK)
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
                self.outer.write_text("Score:0", 5, 2, 2,LCD.WHITE)
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

                        self.outer.show()

                        # 检查游戏状态
                        if not success:
                            # print('end')
                            break

                    else:
                        continue
                    break
                self.game_over()

            def game_over(self):
                self.outer.state = 2
                self.outer.write_text("Game Over",20,60,4,LCD.RED)
                self.outer.write_text("Wait 3s to return!",80,90,1,LCD.RED)
                self.outer.show()
                time.sleep(1)
                self.outer.fill_rect(5,90,312,30,LCD.BLACK)
                self.outer.write_text("Wait 2s to return!",80,90,1,LCD.RED)
                self.outer.show()
                time.sleep(1)
                self.outer.fill_rect(5,90,312,30,LCD.BLACK)
                self.outer.write_text("Wait 1s to return!",80,90,1,LCD.RED)
                self.outer.show()
                time.sleep(1)
                init()
                self.outer.state = 0
                self.snake_pos = [(160, 85),(161,85),(162, 85),(163,85),(164, 85),(165,85)]
                self.level = 0
                self.score = 0
                


        self.snake = SnakeHead(self)


    def fill_ellipse(self, x, y, rx, ry, color):
        # 计算椭圆的参数
        rx2 = rx * rx
        ry2 = ry * ry
        tworx2 = 2 * rx2
        twory2 = 2 * ry2
        
        # 计算椭圆在 x 轴上需要绘制的线段集合
        x0 = x - rx
        x1 = x + rx
        for xi in range(x0, x1+1):
            dx = xi - x
            dy = int(math.sqrt(rx2 - dx*dx) / ry)
            yi0 = y - dy
            y1 = y + dy
            self.hline(xi, yi0, y1 - yi0 + 1, color)

        # 计算椭圆在 y 轴上需要绘制的线段集合
        y0 = y - ry
        y1 = y + ry
        for yi in range(y0, y1+1):
            dy = yi - y
            dx = int(math.sqrt(ry2 - dy*dy) / rx)
            xi0 = x - dx
            x1 = x + dx
            self.vline(xi0, yi, x1 - xi0 + 1, color)

    # 定义绘制三角形函数
    def draw_filled_triangle(self, x1, y1, x2, y2, x3, y3, color=0xffff):

        # 绘制三角形的线段
        self.buffer.line(x1, y1, x2, y2, color)
        self.bufferb.line(x2, y2, x3, y3, color)
        self.buffer.line(x3, y3, x1, y1, color)

        # 使用扫描线算法填充三角形
        min_y = min(y1, y2, y3)
        max_y = max(y1, y2, y3)

        for y in range(min_y, max_y + 1):
            x_left = self.width - 1
            x_right = 0

            for x in range(self.width):
                if self.pixel(x, y):
                    x_left = min(x_left, x)
                    x_right = max(x_right, x)

            if x_right >= x_left:
                self.hline(x_left, y, x_right - x_left + 1, color)

        # 在 OLED 屏幕上绘制三角形
        self.blit(self.buffer, 0, 0)


    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x13)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xF0)
        self.write_data(0x00)
        self.write_data(0x04)
        self.write_data(0x04)
        self.write_data(0x05)
        self.write_data(0x29)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x38)
        self.write_data(0x12)
        self.write_data(0x12)
        self.write_data(0x28)
        self.write_data(0x30)

        self.write_cmd(0xE1)
        self.write_data(0xF0)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x07)
        self.write_data(0x28)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x36)
        self.write_data(0x14)
        self.write_data(0x14)
        self.write_data(0x29)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x3f)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x22)
        self.write_data(0x00)
        self.write_data(0xCD)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

    def write_text(self,text,x,y,size,color):
        ''' Method to write Text on OLED/LCD Displays
            with a variable font size
            Args:
                text: the string of chars to be displayed
                x: x co-ordinate of starting position
                y: y co-ordinate of starting position
                size: font size of text
                color: color of text to be displayed
        '''
        background = self.pixel(x,y)
        info = []
        # Creating reference charaters to read their values
        self.text(text,x,y,color)
        for i in range(x,x+(8*len(text))):
            for j in range(y,y+8):
                # Fetching amd saving details of pixels, such as
                # x co-ordinate, y co-ordinate, and color of the pixel
                px_color = self.pixel(i,j)
                info.append((i,j,px_color)) if px_color == color else None
        # Clearing the reference characters from the screen
        self.text(text,x,y,background)
        # Writing the custom-sized font characters on screen
        for px_info in info:
            self.fill_rect(size*px_info[0] - (size-1)*x , size*px_info[1] - (size-1)*y, size, size, px_info[2])   

    def external_interrupt(self,key):
         # 消除抖动
        time.sleep(0.1)
        # 再次判断按键是否被按下
        if key.value() == 0:
            # print('The button is pressed:',key)
            if self.state == 0:
                if key == left_key:
                    LCD.fill_rect(60,98,320,98,LCD.BLACK)
                    LCD.write_text("-> " + self.games[self.gameIdex],60,98,2,LCD.WHITE)
                    # print(self.gameIdex)
                    self.gameIdex = self.gameIdex + 1
                    if self.gameIdex >= len(self.games):
                        self.gameIdex = 0
                    LCD.show()
                if key == right_key:
                    self.state = 1
                    LCD.fill_rect(0,0,320,172,self.RED)
                    LCD.fill_rect(4,4,312,164,self.BLACK)
                    LCD.show()
                    self.snake.play()

def init():
    #LCD.__init__()
    #color BRG
    LCD.fill(LCD.WHITE)
    LCD.show()
    
    LCD.fill_rect(0,0,320,172,LCD.BLACK)
    LCD.write_text("TC2023-04",5,8,1,LCD.WHITE)
    
#    LCD.fill_rect(0,30,320,30,LCD.BLUE)
#     LCD.rect(0,20,160,20,LCD.BLUE)
    LCD.write_text("PicoGame",110,58,2,LCD.WHITE)
    
#    LCD.fill_rect(0,60,320,30,LCD.GREEN)
#     LCD.rect(0,40,160,20,LCD.GREEN)
    LCD.write_text("-> Snake",60,98,2,LCD.WHITE)

#    LCD.fill_rect(0,90,320,30,0X07FF)
#    LCD.fill_rect(0,120,320,30,0xF81F)
#    LCD.fill_rect(0,150,320,30,0xFFE0)
    
    LCD.show()

    time.sleep(1)


if __name__=='__main__':

    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    LCD = LCD_1inch47()
    init()

    # while True:
    # 选择游戏
    # 左键轮换，右键确定
    left_key = Pin(LEFT_PIN, Pin.IN, Pin.PULL_UP) # 左键
    right_key = Pin(RIGHT_PIN, Pin.IN, Pin.PULL_UP) # 右键
    up_key = Pin(UP_PIN, Pin.IN, Pin.PULL_UP)   # 上键
    down_key = Pin(DOWN_PIN, Pin.IN, Pin.PULL_UP) # 下键

    press = Pin(MIDDLE, Pin.IN, Pin.PULL_UP)    # 中键
    adc1 = ADC(Pin(ADC1))                     #水平方向
    adc2 = ADC(Pin(ADC2))                     #垂直方向
    # handler:中断执行的回调函数
    # trigger:触发中断的方式，分别为Pin.IRQ_FALLING(下降沿触发)、
    # Pin.IRQ_RISING(上升沿触发)、Pin.IRQ_LOW_LEVEL(低电平触发)和
    # Pin.IRQ_HIGH_LEVEL(高电平触发)四种
    # 定义中断，下降沿触发
    left_key.irq(LCD.external_interrupt, Pin.IRQ_FALLING)
    right_key.irq(LCD.external_interrupt, Pin.IRQ_FALLING)
    up_key.irq(LCD.external_interrupt, Pin.IRQ_FALLING)
    down_key.irq(LCD.external_interrupt, Pin.IRQ_FALLING)






