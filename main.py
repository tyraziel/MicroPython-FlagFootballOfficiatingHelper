# Various code snippets taken from https://github.com/javaplus/PicoProjects/ and modified
# My code modifications released under the MIT License (c) Andrew Potozniak (Tyraziel)

import time
import utime
from machine import Pin#, ADC
import tm1637

time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico!")

version = "1"

# Create all our hardware components
play_clock_display = tm1637.TM1637(clk=Pin(1), dio=Pin(0))
game_clock_display = tm1637.TM1637(clk=Pin(3), dio=Pin(2))
debug_display = tm1637.TM1637(clk=Pin(26), dio=Pin(27))

home_team_display = tm1637.TM1637(clk=Pin(5), dio=Pin(4))
away_team_display = tm1637.TM1637(clk=Pin(7), dio=Pin(6))
down_display = tm1637.TM1637(clk=Pin(9), dio=Pin(8))

play_clock_display.show("PLC"+str(version), colon=False)
game_clock_display.show("GTM"+str(version), colon=False)
home_team_display.show("HOME", colon=False)
away_team_display.show("AWAY", colon=False)
down_display.show("DOWN", colon=False)
debug_display.show("REL"+str(version), colon=False)

# debounce utime saying 500ms between play_clock_toggle_button presses
DEBOUNCE_utime = 250 #acp playing around with debounce time
# debounce counter is our counter from the last button press
# initialize to current utime
play_clock_toggle_button = Pin(22, Pin.IN, Pin.PULL_DOWN)
play_clock_toggle_button_debounce_counter = utime.ticks_ms()

game_clock_toggle_button = Pin(21, Pin.IN, Pin.PULL_DOWN)
game_clock_toggle_button_debounce_counter = utime.ticks_ms()

# define flag to say when button is pressed:
play_clock_toggle_button_pressed = False
play_clock_on = False
play_clock_needs_reset = False

# define flag to say when button is pressed:
game_clock_toggle_button_pressed = False
game_clock_on = False
game_clock_needs_reset = False

#Define Starting (and reset) values for game information
playClockStartTimeSeconds = 30
gameClockStartTimeMinutes = 20

# define function to be called when button is pressed
def play_clock_toggle_button_interrupt_handler(pin):
    # since this is called by an interrupt do very little
    # need to give control back to CPU quickly.
    # Could possibly do debounce work here???
    global play_clock_toggle_button_pressed
    play_clock_toggle_button_pressed = True

def play_clock_reset():
    global play_clock_on, play_clock_needs_reset, playClockTimeLeftMS, playClockStartTimeSeconds

    play_clock_on = False
    play_clock_needs_reset = False
    playClockTimeLeftMS = playClockStartTimeSeconds * 1000

# Function to handle play clock toggling
def play_clock_toggle():
    global play_clock_on, play_clock_needs_reset, playClockTimeLeftMS, playClockStartTimeSeconds

    #If the play clock is on, we want to pause it and say it needs a reset
    if(play_clock_on):
        play_clock_on = False
        play_clock_needs_reset = True
    #If the play clock is off, we want to start it
    else:
        play_clock_on = True

    #If the play clock needs to be reset, we reset it
    if(play_clock_needs_reset):
        play_clock_reset()

# Function to handle when the button is pressed
def play_clock_toggle_button_press_detected():
    global play_clock_toggle_button_debounce_counter, play_clock_toggle_button_pressed
    current_utime = utime.ticks_ms()
    # Calculate utime passed since last button press
    utime_passed = utime.ticks_diff(current_utime,play_clock_toggle_button_debounce_counter)
    print("utime passed=" + str(utime_passed))
    if (utime_passed > DEBOUNCE_utime):
        print("play_clock_toggle_button Pressed!")
        # set play_clock_toggle_button_debounce_counter to current utime
        play_clock_toggle_button_debounce_counter = utime.ticks_ms()
        play_clock_toggle()
        play_clock_toggle_button_pressed = False
    else:
        play_clock_toggle_button_pressed = False
        print("Not enough utime")

# define function to be called when button is pressed
def game_clock_toggle_button_interrupt_handler(pin):
    # since this is called by an interrupt do very little
    # need to give control back to CPU quickly.
    # Could possibly do debounce work here???
    global game_clock_toggle_button_pressed
    game_clock_toggle_button_pressed = True

#function to reset the game clock
def game_clock_reset():
    global game_clock_on, game_clock_needs_reset, gameClockTimeLeftMS, gameClockStartTimeMinutes
    #stop the game clock and reset it
    game_clock_on = False
    game_clock_needs_reset = False
    gameClockTimeLeftMS = gameClockStartTimeMinutes * 60000

# Function to handle starting and stopping the game clock
def game_clock_toggle():
    global game_clock_on, game_clock_needs_reset, gameClockTimeLeftMS, gameClockStartTimeMinutes

    #If the game clock is on, we want to pause it
    if(game_clock_on):
        game_clock_on = False
    #If the game clock is off, we want to start it
    else:
        game_clock_on = True

    #If the game clock needs to be reset, we reset it
    if(game_clock_needs_reset):
        game_clock_reset()
        play_clock_reset()

# Function to handle when the button is pressed
def game_clock_toggle_button_press_detected():
    global game_clock_toggle_button_debounce_counter, game_clock_toggle_button_pressed
    current_utime = utime.ticks_ms()
    # Calculate utime passed since last button press
    utime_passed = utime.ticks_diff(current_utime,game_clock_toggle_button_debounce_counter)
    print("utime passed=" + str(utime_passed))
    if (utime_passed > DEBOUNCE_utime):
        print("game_clock_toggle_button Pressed!")
        # set game_clock_toggle_button_debounce_counter to current utime
        game_clock_toggle_button_debounce_counter = utime.ticks_ms()
        game_clock_toggle()
        game_clock_toggle_button_pressed = False
    else:
        game_clock_toggle_button_pressed = False
        print("Not enough utime")

## define interrupt to call our function when button is pressed:
play_clock_toggle_button.irq(trigger=Pin.IRQ_RISING, handler=play_clock_toggle_button_interrupt_handler)
game_clock_toggle_button.irq(trigger=Pin.IRQ_RISING, handler=game_clock_toggle_button_interrupt_handler)

playClockTimeLeftMS = playClockStartTimeSeconds * 1000
playClockDisplaySeconds = int(playClockTimeLeftMS / 1000)
playClockDisplaySubSeconds = int((playClockTimeLeftMS - (playClockDisplaySeconds*1000)) / 10)
play_clock_display.numbers(playClockDisplaySeconds, playClockDisplaySubSeconds, colon=True)

gameClockTimeLeftMS = gameClockStartTimeMinutes * 60000
gameClockDisplayMinutes = int(gameClockTimeLeftMS / 60000)
gameClockDisplaySeconds = int((gameClockTimeLeftMS - (gameClockDisplayMinutes*60000)) / 1000)
gameClockDisplaySubSeconds = int((gameClockTimeLeftMS - (gameClockDisplayMinutes*60000) - (gameClockDisplaySeconds*1000)) / 10)
game_clock_display.numbers(gameClockDisplayMinutes, gameClockDisplaySeconds, colon=True)

startTime = utime.ticks_ms()

#Main Loop
while True:
    utime.sleep_ms(100) #comment this line out when running on real hardware.
    
    if play_clock_toggle_button_pressed==True:
        play_clock_toggle_button_press_detected()
    if game_clock_toggle_button_pressed==True:
        game_clock_toggle_button_press_detected()

    #debug_display.show("DBG1", colon=False)
    timePassed = utime.ticks_diff(utime.ticks_ms(), startTime)

    startTime = utime.ticks_ms()

    if play_clock_on:
        playClockTimeLeftMS = playClockTimeLeftMS - timePassed

    if game_clock_on:
        gameClockTimeLeftMS = gameClockTimeLeftMS - timePassed

    if playClockTimeLeftMS > 0:
        playClockDisplaySeconds = int(playClockTimeLeftMS / 1000)
        playClockDisplaySubSeconds = int((playClockTimeLeftMS - (playClockDisplaySeconds*1000)) / 10)
        if gameClockTimeLeftMS > 0:
            play_clock_display.numbers(playClockDisplaySeconds, playClockDisplaySubSeconds, colon=True)
    elif gameClockTimeLeftMS > 0:
        play_clock_display.show("DONE", colon=False)
        play_clock_on = False
        play_clock_needs_reset = True

    if gameClockTimeLeftMS > 0:
        gameClockDisplayMinutes = int(gameClockTimeLeftMS / 60000)
        gameClockDisplaySeconds = int((gameClockTimeLeftMS - (gameClockDisplayMinutes*60000)) / 1000)

        if(gameClockDisplayMinutes > 0):
            game_clock_display.numbers(gameClockDisplayMinutes, gameClockDisplaySeconds, colon=True)
        else:
            gameClockDisplaySubSeconds = int((gameClockTimeLeftMS - (gameClockDisplayMinutes*60000) - (gameClockDisplaySeconds*1000)) / 10)
            game_clock_display.numbers(gameClockDisplaySeconds, gameClockDisplaySubSeconds, colon=True)
    else:
        play_clock_display.show("HALF", colon=False)
        game_clock_display.show("OVER", colon=False)
        play_clock_on = False
        play_clock_needs_reset = True
        game_clock_on = False
        game_clock_needs_reset = True
