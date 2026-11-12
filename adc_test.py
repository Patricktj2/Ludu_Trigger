from machine import Pin, ADC
from time import sleep, sleep_ms, ticks_ms, ticks_diff

adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)
beat = False
last_beat = ticks_ms() # Skal være der for at lave en start last_beat værdi

while True:
    puls_value = adc.read()
    sleep_ms(10)
    print(puls_value)