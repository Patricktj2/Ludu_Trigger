from machine import Pin, ADC
from time import sleep, sleep_ms, ticks_ms, ticks_diff

adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)
beat = False
last_beat = ticks_ms() # Skal være der for at lave en start last_beat værdi

while True:
    puls_value = adc.read()
    sleep_ms(10)
    
    if puls_value > 2500 and not beat:
        beat = True
        current_beat = ticks_ms()
        difference = ticks_diff(current_beat, last_beat)
        bpm = 60000 // difference # Bruger // i stedet for / for at fjerne decimaler
        last_beat = current_beat
 
        if difference > 300 and difference < 2000: # Bruges til at skip bpm print hvis værdien er urealistisk
            print(bpm)							   # Udregnes ved at sige 60000 / 200 (puls) og 60000 / 30 (puls) da 200 og 30 er en urealistiske puls
            print("Heartbeat")
            
    elif puls_value < 1500:
            beat = False
        

