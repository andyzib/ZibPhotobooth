#!/usr/bin/env python3
import pygame
from time import sleep
import time
import picamera
import os

########## Configuration Section.
# Preview Alpha, 0-255
PREVIEW_ALPHA = 200

# Set Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Number of Photos to Take
NUMPHOTOS = 4

# Camera Rotation
CAMROTATION = 270
CAMFREAMERATE = 15
# Text Annotation Size
ANNOTATIONSIZE = 48
#54
#66
#ANNOTATIONSIZE = 72
#80
#88
#ANNOTATIONSIZE = 96

# Working Directory
globalWorkDir = '/home/aszbikowski/PhotoBooth_WorkDir'
# Session Directory
globalSessionDir = ''

# Width of previous and next tap zones.
ZONEWIDTH = 100

########## End of Configuration Section.

########## Settings/Globals. No modification necissary.
# For readable code.
LEFTMOUSEBUTTON = 1

# Center of display.
CENTER_X = SCREEN_WIDTH/2
CENTER_Y = SCREEN_HEIGHT/2

# Previous Tap Zone: 0,0 to 100,480
# Previous Zone is easy, start at 0,0 (top left corner) and draw for ZONEWIDTH.
PREV_X = 0
PREV_Y = 0
# Next Tap Zone: 700,0 to 800,480
NEXT_X = SCREEN_WIDTH - ZONEWIDTH
NEXT_Y = SCREEN_HEIGHT

# Start Box, Center of Screen?
# Center: Width/2,Height/2.
# Upper left corner of box: CenterX-ZONEWIDTH/2,CenterY-ZONEWIDTH/2
START_MIN_X = CENTER_X-(ZONEWIDTH/2)
START_MAX_X = START_MIN_X+ZONEWIDTH
START_MIN_Y = CENTER_Y-(ZONEWIDTH/2)
START_MAX_Y = START_MIN_Y+ZONEWIDTH

# Define Up, Down, Left, Right, B, and A.
## Left is next to previous. Starts at PREV_X+ZONEWIDTH, ends at PREV_X+(ZONEWIDTH*2)
LEFT_MIN_X = PREV_X+ZONEWIDTH
LEFT_MAX_X = PREV_X+(ZONEWIDTH*2)
LEFT_MIN_Y = 0
LEFT_MAX_Y = SCREEN_HEIGHT

## Right is next to next. Starts at NEXT_X-ZONEWIDTH, Ends at NEXT_X.
RIGHT_MIN_X = NEXT_X-ZONEWIDTH
RIGHT_MAX_X = NEXT_X
RIGHT_MIN_Y = 0
RIGHT_MAX_Y = SCREEN_HEIGHT

# Up tap zone.
UP_MIN_X = LEFT_MIN_X
UP_MAX_X = RIGHT_MIN_X
UP_MIN_Y = 0
UP_MAX_Y = UP_MIN_Y + ZONEWIDTH

# Down tap zone.
DOWN_MIN_X = LEFT_MIN_X
DOWN_MAX_X = RIGHT_MIN_X
DOWN_MIN_Y = SCREEN_HEIGHT - ZONEWIDTH
DOWN_MAX_Y = SCREEN_HEIGHT

# Konami Code tracker.
KonamiLast = 'None'

# RGB Code for Blue
BLUE = (0, 128, 255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

running = 1
# Don't full screen until you have a way to quit the program. ;)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#pygame.mouse.set_visible(False)
pygame.mouse.set_visible(True)
pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

#ImgOK = pygame.image.load('Start.png')
ImgOK = pygame.image.load('OK.png')
ImgOK = pygame.transform.scale(ImgOK, (ZONEWIDTH, ZONEWIDTH))
ImgPointLeft = pygame.image.load('PointLeft.png')
ImgPointLeft = pygame.transform.scale(ImgPointLeft, (ZONEWIDTH, ZONEWIDTH))
ImgPointRight = pygame.image.load('PointRight.png')
ImgPointRight = pygame.transform.scale(ImgPointRight, (ZONEWIDTH, ZONEWIDTH))

ImgStart = pygame.image.load('8bit.png')
ImgStart = pygame.transform.scale(ImgStart, (ZONEWIDTH, ZONEWIDTH))
ImgA = pygame.image.load('A.png')
ImgA = pygame.transform.scale(ImgA, (ZONEWIDTH, ZONEWIDTH))
ImgB = pygame.image.load('B.png')
ImgB = pygame.transform.scale(ImgB, (ZONEWIDTH, ZONEWIDTH))
########## End of Settings/Globals.

########## Object Initilizations.
camera = picamera.PiCamera()
#camera.rotation = 180
camera.rotation = CAMROTATION
camera.framerate = CAMFREAMERATE
# Default text size is 32, range is 6-160.
camera.annotate_text_size = ANNOTATIONSIZE

# List of effects to cycle through.
globalEffectList = ['none','sketch','posterise','emboss','negative','colorswap',
                    'hatch','watercolor','cartoon','washedout','solarize','oilpaint']
# List of friendly names for the various effects.
globalEffectDict = {'none': 'Normal','sketch':'Artist Sketch','posterise':'Poster','emboss':'Embossed',
                    'negative':'Negative Zone','colorswap':'Swap Colors','hatch':'Crosshatch','watercolor':'Water Color',
                    'cartoon':'Cartoon','washedout':'Washed Out','solarize':'Solar Flare','oilpaint':'Oil Painting'}
# Set the current effect.
# Current effect.
globalEffectCurr = 0
# Number of effects.
globalEffectLeng = len(globalEffectList)-1

# Photobooth SessionID
SessionID = 0


########## Functions

# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones(KonamiScreen):
    # Draw the Previous tap zone on screen.
    pygame.draw.rect(screen, BLUE, pygame.Rect(PREV_X, PREV_Y, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Next tap zone on screen.
    pygame.draw.rect(screen, BLUE, pygame.Rect(NEXT_X, 0, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Start tap zone on screen.
    pygame.draw.rect(screen, BLUE, pygame.Rect(START_MIN_X, START_MIN_Y, ZONEWIDTH, ZONEWIDTH))
    #pygame.draw.circle(screen, (0, 128, 255), (400, 240), 75)

    if KonamiScreen == True:
        screen.blit(ImgB, (PREV_X, START_MIN_Y))
        screen.blit(ImgA, (NEXT_X, START_MIN_Y))
        screen.blit(ImgStart, (START_MIN_X, START_MIN_Y))
    else:
        screen.blit(ImgPointLeft, (PREV_X, START_MIN_Y))
        screen.blit(ImgPointRight, (NEXT_X, START_MIN_Y))
        screen.blit(ImgOK, (START_MIN_X, START_MIN_Y))
    pygame.display.flip()
    return
# End of function

# Call on an input event that resets Konami Code.
def KonamiCodeReset():
    global KonamiLast
    print('Konami Code Reset!')
    KonamiLast = 'None'
    return

# If the Konami Code is verified, then fire!
def KonamiCodeVerified():
    print('Konami Code Verified!!!')
    pygame.quit()
    quit()
    return

# Call on an input event that is part of Konami Code.
def KonamiCode(KonamiInput):
    global KonamiLast
    # Up 1, Up 2, Down 1, Down 2, Left 1, Right 1, Left 2, Right 2, B, A.
    if KonamiInput == 'Up' and KonamiLast == 'None':
        KonamiLast = 'Up1'
        Sequence = True
    elif KonamiInput == 'Up' and KonamiLast == 'Up1':
        KonamiLast = 'Up2'
        Sequence = True
    elif KonamiInput == 'Down' and KonamiLast == 'Up2':
        KonamiLast = 'Down1'
        Sequence = True
    elif KonamiInput == 'Down' and KonamiLast == 'Down1':
        KonamiLast = 'Down2'
        Sequence = True
    elif KonamiInput == 'Left' and KonamiLast == 'Down2':
        KonamiLast = 'Left1'
        Sequence = True
    elif KonamiInput == 'Right' and KonamiLast == 'Left1':
        KonamiLast = 'Right1'
        Sequence = True
    elif KonamiInput == 'Left' and KonamiLast == 'Right1':
        KonamiLast = 'Left2'
        Sequence = True
    elif KonamiInput == 'Right' and KonamiLast == 'Left2':
        KonamiLast = 'Right2'
        Sequence = True
    elif KonamiInput == 'B' and KonamiLast == 'Right2':
        KonamiLast = 'B'
        Sequence = True
    elif KonamiInput == 'A' and KonamiLast == 'B':
        KonamiLast = 'A'
        Sequence = True
    elif KonamiInput == 'Start' and KonamiLast == 'A':
        KonamiCodeVerified()
        Sequence = True
    else:
        KonamiCodeReset()
        Sequence = False
    print(KonamiInput)
    return Sequence
# End of function.

# Process Input from the Left Mouse Button being depressed.
# Also tapping on the touch screen.
def LeftMouseButtonDown(xx, yy):
    # Detect Taps in Previous Zone
    if xx >= PREV_X and xx <= ZONEWIDTH:
        if KonamiCode('B') == False:
            TapPrev()
    # Detect Taps in Next Zone
    elif xx >= NEXT_X and xx <= SCREEN_WIDTH:
        if KonamiCode('A') == False:
            TapNext()
    # Detect Taps in the Start Zone
    elif xx >= START_MIN_X and yy >= START_MIN_Y and xx <= START_MAX_X and yy <= START_MAX_Y:
        if KonamiCode('Start') == False:
            TapStart()
    # Detect Taps in the Up Zone.
    elif xx >= UP_MIN_X and yy >= UP_MIN_Y and xx <= UP_MAX_X and yy <= UP_MAX_Y:
        KonamiCode('Up')
    # Detect Taps in the Down Zone.
    elif xx >= DOWN_MIN_X and yy >= DOWN_MIN_Y and xx <= DOWN_MAX_X and yy <= DOWN_MAX_Y:
        KonamiCode('Down')
    # Detect Taps in the Left Zone.
    elif xx >= LEFT_MIN_X and yy >= LEFT_MIN_Y and xx <= LEFT_MAX_X and yy <= LEFT_MAX_Y:
        KonamiCode('Left')
    # Detect Taps in the Right Zone.
    elif xx >= RIGHT_MIN_X and yy >= RIGHT_MIN_Y and xx <= RIGHT_MAX_X and yy <= RIGHT_MAX_Y:
        KonamiCode('Right')
    else:
        KonamiCodeReset()
        print("No Event")
    return
# End of function.

# Set Camera Annotation Text.
def SetAnnotate(aText):
    # camera.annotate_background('Blue')
    # camera.annotate_foreground('Yellow')
    camera.annotate_background = picamera.Color('black')
    camera.annotate_foreground = picamera.Color('white')
    camera.annotate_text = aText
# End function.

# Function to change effect.
def SetEffect(NewEffect):
    global globalEffectList
    global globalEffectCurr
    global camera
    print('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    SetAnnotate("Effect: %s" % globalEffectDict[NewEffect])
    # sleep(10)
    # SetAnnotate("")
# End of function.

# Function to cycle effects forward.
def NextEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == globalEffectLeng:
        globalEffectCurr = 0
    else:
        globalEffectCurr = globalEffectCurr + 1

    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
# End of function.

# Function to cycle effects backward.
def PrevEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == 0:
        globalEffectCurr = globalEffectLeng
    else:
        globalEffectCurr = globalEffectCurr - 1
    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
    return True
# End of Function

def QuitGracefully():
    camera.stop_preview()
    camera.close()
    #GPIO.remove_event_detect(BUTTON_NEXT)
    #GPIO.remove_event_detect(BUTTON_BACK)
    #GPIO.remove_event_detect(BUTTON_START)
    #GPIO.cleanup()
    #quit("Quitting program gracefully.")
# End of function

# Generates a PhotoBoot Session
def SetupPhotoboothSession():
    global SessionID
    global globalWorkDir
    global globalSessionDir
    SessionID = time.time()  # Use UNIX epoc time as session ID.
    # Create the Session Directory for storing photos.
    globalSessionDir = globalWorkDir + '/' + str(SessionID)
    os.makedirs(globalSessionDir, exist_ok=True)
# End of function

def TakePhoto(PhotoNum):
    global SessionID
    global globalSessionDir
    PhotoPath = globalSessionDir + '/' + str(PhotoNum) + '.jpg'
    SetAnnotate('')
    camera.capture(PhotoPath)
# End of function.

def RunCountdown():
    SetAnnotate('3')
    sleep(1)
    SetAnnotate('2')
    sleep(1)
    SetAnnotate('1')
    sleep(1)
    SetAnnotate('CHEESE!!!')
    sleep(1)
# End of function.

def ResetPhotoboothSession():
    global SessionID
    SessionID = 0
    SetEffect('none')
# End of function.

def RunPhotoboothSession():
    global NUMPHOTOS
    currentPhoto = 1
    SetupPhotoboothSession()
    while currentPhoto <= NUMPHOTOS:
        RunCountdown()
        TakePhoto(currentPhoto)
        currentPhoto = currentPhoto + 1
    ResetPhotoboothSession()
# End of function.

# Function called when the Start zone is tapped.
def TapStart():
    print("Start")
    screen.fill(black)
    pygame.display.flip() # I think this will clear the screen?
    RunPhotoboothSession()
    #sleep(10)
    return
# End of Function.

# Function called when the Previous zone is tapped.
def TapPrev():
    print("Previous")
    PrevEffect()
    return
# End of Function

# Function called when the Next zone is tapped.
def TapNext():
    print("Next")
    NextEffect()
    return
# End of Function

########## End of functions.


######### Main

SetEffect('none')
camera.start_preview(alpha=PREVIEW_ALPHA)
sleep(2) # This seems to be recommended when starting the camera.

while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTMOUSEBUTTON:
        x, y = event.pos
        print("You pressed the left mouse button at (%d, %d)" % event.pos)
        LeftMouseButtonDown(x, y)
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F4:
            print('F4 pressed, quitting.')
            quit()
    #elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTMOUSEBUTTON:
    #   print("You released the left mouse button at (%d, %d)" % event.pos)

    if KonamiLast == 'A' or KonamiLast == 'B' or KonamiLast == 'Right2':
        ShowTapZones(True)
    else:
        ShowTapZones(False)
########## End of Main