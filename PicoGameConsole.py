from machine import Pin,PWM,ADC
import time
from Lcd import LCD,LEFT_PIN, RIGHT_PIN, UP_PIN, DOWN_PIN, MIDDLE, ADC1, ADC2, BL
from Games import Games

games = Games()

def external_interrupt(key):
    # 消除抖动
    time.sleep(0.1)
    # 再次判断按键是否被按下
    if key.value() == 0:
        print('The button is pressed:',key)
        print(LCD.state)
        if LCD.state == 0:
            if key == left_key:
                LCD.fill_rect(60,98,320,98,LCD.BLACK)
                LCD.write_text("-> " + games.games[games.gameIdex],60,98,2,LCD.WHITE)
                # print(LCD.gameIdex)
                games.gameIdex = games.gameIdex + 1
                if games.gameIdex >= len(games.games):
                    games.gameIdex = 0
                LCD.show()
            if key == right_key:
                LCD.fill_rect(0,0,320,172,LCD.RED)
                LCD.fill_rect(4,4,312,164,LCD.BLACK)
                LCD.show()
                games.startGame()

if __name__=='__main__':

    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    LCD.init()

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
    left_key.irq(external_interrupt, Pin.IRQ_FALLING)
    right_key.irq(external_interrupt, Pin.IRQ_FALLING)
    up_key.irq(external_interrupt, Pin.IRQ_FALLING)
    down_key.irq(external_interrupt, Pin.IRQ_FALLING)





