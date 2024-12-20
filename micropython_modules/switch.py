import machine
import utime as time
from machine import Pin
import micropython

class Switch:
    SW_PRESS = 4
    SW_RELEASE = 8

    def __init__(self,sw):
        self.sw_pin = Pin(sw, Pin.IN, Pin.PULL_UP)
        self.sw_pin.irq(handler=self.switch_detect, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING )
        self.handlers = []
        self.last_button_status = self.sw_pin.value()

    def switch_detect(self,pin):
        if self.last_button_status == self.sw_pin.value():
            return
        self.last_button_status = self.sw_pin.value()
        if self.sw_pin.value():
            micropython.schedule(self.call_handlers, Switch.SW_RELEASE)
        else:
            micropython.schedule(self.call_handlers, Switch.SW_PRESS)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)
