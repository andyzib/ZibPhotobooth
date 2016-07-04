#!/usr/bin/env python3

### Andrew Zbikowski's <andrew@zibnet.us> Raspberry Pi PhotoBooth.
### Version: 2016-06-20
### Version: 2016-06-21: Moved text display from PiCamera annotations to PyGame. Much better.

import picamera
import pygame
import time
import os
import shutil
import subprocess
from PIL import Image
from time import sleep



########## Configuration Section.
# Idle Time, in seconds
IDLETIME = 30

# Preview Alpha, 0-255
PREVIEW_ALPHA = 120 # OK For Black Background
#PREVIEW_ALPHA = 140
#PREVIEW_ALPHA = 200 # Meh for White Background
#PREVIEW_ALPHA = 220
#PREVIEW_ALPHA = 240

# Set Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Number of Photos to Take
NUMPHOTOS = 4

# Camera Rotation
CAMROTATION = 270
CAMFREAMERATE = 15

# Working Directory
globalWorkDir = '/home/aszbikowski/PhotoBooth_WorkDir'
globalDCIMDir = globalWorkDir + '/DCIM'
# Session Directory
globalSessionDir = ''

# Width of previous and next tap zones.
# ZONEWIDTH = 100
ZONEWIDTH = 80

# Setup the Montage
# Pixels separating photos, maintain 2:3 aspect ratio. (Perfect for a 4"x6" print)
MONTAGESPACING_W = 30
MONTAGESPACING_H = 20
MONTAGE_W = 1920
MONTAGE_H = 2880


########## End of Configuration Section.

########## Global variables. No modification necissary.
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
globalKonamiLast = 'None'

# RGB Codes
rgbRED = (255,0,0)
rgbGREEN = (0,255,0)
rgbBLUE = (0,0,255)
rgbDARKBLUE = (0,0,128)
rgbWHITE = (255,255,255)
rgbBLACK = (0,0,0)
rgbPINK = (255,200,200)

# Background Color!
rgbBACKGROUND = rgbBLACK

# Initialise PyGame
# pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
pygame.init() # Initialise pygame
# Don't full screen until you have a way to quit the program. ;)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption('Photo Booth')

# Setup the game surface
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(rgbBACKGROUND)

# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.mouse.set_visible(False)
# Working around what seems to be a bug in PyGame and/or libsdl where the
# cursor gets stuck in the lower right corner of the Raspberry Pi touchscreen
# after a few taps. This only happens when the cursor is not visible in PyGame Fullscreen.
# My workaround is setting a very small cursor. 
pygame.mouse.set_visible(True)
pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

# Load images and scale them to the screen and tap zones. 
# At some point find a GO! or START! icon that works with the transparency and all that. 
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

# Fonts to be used.
smallfont = pygame.font.Font(None, 50) #Small font for on screen messages.
# Original: 180
bigfont = pygame.font.Font(None, 220) # Big font for countdown.

########## End of Settings/Globals.

########## Object Initializations.
camera = picamera.PiCamera()
camera.rotation = CAMROTATION
camera.framerate = CAMFREAMERATE
# Flip the camera horizontally so it acts like a mirror.
camera.hflip = True

# List of effects to cycle through.
globalEffectList = ['none','sketch','posterise','emboss','negative','colorswap',
                    'hatch','watercolor','cartoon','washedout','solarize','oilpaint']
# Dictionary of friendly names for the various effects.
globalEffectDict = {'none': 'Normal','sketch':'Artist Sketch','posterise':'Poster','emboss':'Embossed',
                    'negative':'Negative Zone','colorswap':'Swap Colors','hatch':'Crosshatch','watercolor':'Water Color',
                    'cartoon':'Cartoon','washedout':'Washed Out','solarize':'Solar Flare','oilpaint':'Oil Painting'}
# Current effect.
globalEffectCurr = 0
# Number of effects.
globalEffectLeng = len(globalEffectList)-1

# Photobooth SessionID
# When a session is in progress, touchscreen inputs are ignored. 
SessionID = 0

# Show instructions on screen?
ShowInstructions = True
LastTap = 0

 ########## Functions

# Replacing ShowTapZones() with a more generic UpdateDisplay(). 
# When I'm done, ShowTapZones() will do exactly what it says. 
# Update display will take care of deciding which elements should be on screen.
def UpdateDisplay():
    global screen
    global background
    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
    return
# End of function
 
# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones(KonamiScreen):
    global screen
    global background
    background.fill(rgbBACKGROUND)  # Black background
    # Draw the Previous tap zone on screen.
    pygame.draw.rect(background, rgbBLUE, pygame.Rect(PREV_X, PREV_Y, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Next tap zone on screen.
    pygame.draw.rect(background, rgbBLUE, pygame.Rect(NEXT_X, 0, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Start tap zone on screen.
    pygame.draw.rect(background, rgbBLUE, pygame.Rect(START_MIN_X, START_MIN_Y, ZONEWIDTH, ZONEWIDTH))
    # pygame.draw.circle(screen, (0, 128, 255), (400, 240), 75)

    # If Up,Up,Down,Down,Left,Right,Left,Right has been successfully entered,
    # the tap zone icons change to B, A, and an alien guy.
    if KonamiScreen == True:
        background.blit(ImgB, (PREV_X, START_MIN_Y))
        background.blit(ImgA, (NEXT_X, START_MIN_Y))
        background.blit(ImgStart, (START_MIN_X, START_MIN_Y))
    else:
        background.blit(ImgPointLeft, (PREV_X, START_MIN_Y))
        background.blit(ImgPointRight, (NEXT_X, START_MIN_Y))
        background.blit(ImgOK, (START_MIN_X, START_MIN_Y))

    if ShowInstructions == True:
        SetInstructions()
    SetEffectText(globalEffectList[globalEffectCurr])
    UpdateDisplay()
    return
# End of function

def SetBlankScreen():
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    return
# End of function. 

# Show the instructions on screen.
def SetInstructions():
    global background
    global smallfont
    Text = "Tap left and right to change effect."
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    height = Text.get_height()
    background.blit(Text,(textpos)) #Write the small text
    Text = "Tap OK to take photos."
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = height*2
    background.blit(Text, (textpos))  # Write the small text
    return

# Writes the current effect to the screen using PyGame. 
def SetEffectText(NewEffect):
    global globalEffectDict
    global background
    global smallfont
    #Text = "Effect: " + globalEffectDict[NewEffect]
    Text = "Effect: " + globalEffectDict[NewEffect]
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = SCREEN_HEIGHT - Text.get_height()
    background.blit(Text,(textpos)) #Write the small text
    #UpdateDisplay()
    return

def QuitGracefully():
    camera.stop_preview()
    camera.close()
    pygame.quit()
    quit()
    #GPIO.remove_event_detect(BUTTON_NEXT)
    #GPIO.remove_event_detect(BUTTON_BACK)
    #GPIO.remove_event_detect(BUTTON_START)
    #GPIO.cleanup()
    #quit("Quitting program gracefully.")
# End of function

# Call on an input event that resets Konami Code.
def KonamiCodeReset():
    global globalKonamiLast
    print('Konami Code Reset!')
    globalKonamiLast = 'None'
    return

# If the Konami Code is verified, then fire!
def KonamiCodeVerified():
    print('Konami Code Verified!!!')
    QuitGracefully()
    return

# Call on an input event that is part of Konami Code.
def KonamiCode(KonamiInput):
    global globalKonamiLast
    # Up 1, Up 2, Down 1, Down 2, Left 1, Right 1, Left 2, Right 2, B, A.
    if KonamiInput == 'Up' and globalKonamiLast == 'None':
        globalKonamiLast = 'Up1'
        Sequence = True
    elif KonamiInput == 'Up' and globalKonamiLast == 'Up1':
        globalKonamiLast = 'Up2'
        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Up2':
        globalKonamiLast = 'Down1'
        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Down1':
        globalKonamiLast = 'Down2'
        Sequence = True
    elif KonamiInput == 'Left' and globalKonamiLast == 'Down2':
        globalKonamiLast = 'Left1'
        Sequence = True
    elif KonamiInput == 'Right' and globalKonamiLast == 'Left1':
        globalKonamiLast = 'Right1'
        Sequence = True
    elif KonamiInput == 'Left' and globalKonamiLast == 'Right1':
        globalKonamiLast = 'Left2'
        Sequence = True
    elif KonamiInput == 'Right' and globalKonamiLast == 'Left2':
        globalKonamiLast = 'Right2'
        Sequence = True
    elif KonamiInput == 'B' and globalKonamiLast == 'Right2':
        globalKonamiLast = 'B'
        Sequence = True
    elif KonamiInput == 'A' and globalKonamiLast == 'B':
        globalKonamiLast = 'A'
        Sequence = True
    elif KonamiInput == 'Start' and globalKonamiLast == 'A':
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

# Function to change effect.
def SetEffect(NewEffect):
    global globalEffectList
    global globalEffectCurr
    global camera
    print('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    SetEffectText(NewEffect)
    globalEffectCurr = globalEffectList.index(NewEffect)
    return
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

# Generates a PhotoBoot Session
def SetupPhotoboothSession():
    global SessionID
    global globalWorkDir
    global globalSessionDir
    SessionID = int(time.time())  # Use UNIX epoc time as session ID.
    # Create the Session Directory for storing photos.
    globalSessionDir = globalWorkDir + '/' + str(SessionID)
    os.makedirs(globalSessionDir, exist_ok=True)
# End of function

def StartCameraPreview():
    camera.hflip = True
    camera.resolution = RES_PREVIEW
    camera.start_preview(alpha=PREVIEW_ALPHA)
# End of function.

def TakePhoto(PhotoNum):
    global SessionID
    global globalSessionDir
    PhotoPath = globalSessionDir + '/' + str(PhotoNum) + '.jpg'
    camera.stop_preview()
    camera.resolution = RES_PHOTO
    camera.hflip = False
    # Feeling ambitions? PyGame the screen to white, turn off camera preview, take picture, change back to normal.
    background.fill(rgbWHITE)
    UpdateDisplay()
    camera.capture(PhotoPath)
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    StartCameraPreview()
# End of function.

def RunCountdown():
    i = 5
    while i >= 0:
        if i == 0:
            string = 'CHEESE!!!'
        else:
            string = str(i)
        text = bigfont.render(string, 1, rgbRED)
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        SetBlankScreen()
        background.blit(text, textpos)
        UpdateDisplay()
        i = i - 1
        sleep(1)
    # Blank Cheese off the screen.
    SetBlankScreen()
    UpdateDisplay()
    return
# End of function.

def ResetPhotoboothSession():
    global SessionID
    SessionID = 0
    StartCameraPreview()
    SetEffect('none')
# End of function.

def RunPhotoboothSession():
    global NUMPHOTOS
    currentPhoto = 1 # File name for photo.
    SetupPhotoboothSession()
    while currentPhoto <= NUMPHOTOS:
        RunCountdown()
        TakePhoto(currentPhoto)
        currentPhoto = currentPhoto + 1
    montageFile = CreateMontage()
    print("Montage File: " + montageFile)
    PreviewMontage(montageFile)
    ResetPhotoboothSession()
# End of function.

# Function called when the Start zone is tapped.
def TapStart():
    print("Start")
    # I think this will clear the screen?
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    RunPhotoboothSession()
    #sleep(10)
    return
# End of Function.

# Function called when the Previous zone is tapped.
def TapPrev():
    global ShowInstructions
    global LastTap
    print("Previous")
    ShowInstructions = False
    LastTap = time.time()
    PrevEffect()
    return
# End of Function

# Function called when the Next zone is tapped.
def TapNext():
    global ShowInstructions
    global LastTap
    print("Next")
    ShowInstructions = False
    LastTap = time.time()
    NextEffect()
    return
# End of Function

def IdleReset():
    global ShowInstructions
    global LastTap
    LastTap = 0
    ShowInstructions = True
    SetEffect('none')
    UpdateDisplay()
# End of function.

# Creates the Montage image using ImageMagick.
# Python ImageMagick bindings seem to suck, so using the CLI utility.
def CreateMontage():
    global globalSessionDir
    global SessionID
    global globalWorkDir
    binMontage = '/usr/bin/montage'
    outFile = globalSessionDir + "/" + str(SessionID) + ".jpg"
    argsMontage = "-tile 2x6 "
    # Loop controls.
    incrementCounter = False
    photoCounter = 1
    for counter in range(1, NUMPHOTOS*2+1):
        argsMontage = argsMontage + str(globalSessionDir) + "/" + str(photoCounter) + ".jpg "
        if incrementCounter:
            photoCounter = photoCounter + 1
            incrementCounter = False
        else:
            incrementCounter = True
    argsMontage = argsMontage + globalWorkDir + "/Logo.png " + globalWorkDir + "/Logo.png "
    #argsMontage = argsMontage + "-geometry " + str(MONTAGE_W) + "x" + str(MONTAGE_H) + "+" + str(MONTAGESPACING_W) + "+" + str(MONTAGESPACING_H) + " " + outFile
    argsMontage = argsMontage + "-geometry " + "+" + str(MONTAGESPACING_W) + "+" + str(MONTAGESPACING_H) + " " + outFile
    print(binMontage + " " + argsMontage)
    # Display Processing On screen.
    string = "Processing, Please Wait."
    text = smallfont.render(string, 1, rgbRED)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    SetBlankScreen()
    background.blit(text, textpos)
    UpdateDisplay()
    subprocess.call(binMontage + " " + argsMontage, shell=True)
    return outFile
# End of function.

# Show preview of the montage.
def PreviewMontage(MontageFile):
    print("Show something.")
    preview = pygame.image.load(MontageFile)
    PILpreview = Image.open(MontageFile)
    previewSize = PILpreview.size # returns (width, height) tuple
    ScaleW = AspectRatioCalc(previewSize[0], previewSize[1], SCREEN_HEIGHT)
    preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
    SetBlankScreen()
    background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
    camera.stop_preview()
    UpdateDisplay()
    sleep(15)
    return
# End of function.

# Aspect Ratio Calculator
def AspectRatioCalc(OldH, OldW, NewW):
    #(original height / original width) x new width = new height
    return int((OldH/OldW)*NewW)
# End of function.
########## End of functions.


######### Main

# Setup Camera resolution for picture taking.
# PiCam Max Res is 2592, 1944, a 4:3 aspect ratio.
# A 4x6 print (4 inch height, 6 inch width) is 3:2 aspect ratio.
# This gives us ready to use thumbnails to montage, minimal scaling needed.
CAMRES_W = int((MONTAGE_W/2)-(MONTAGESPACING_W*2))
# Maintain the Aspect Ratio Math:
# (original height / original width) x new width = new height
CAMRES_H = AspectRatioCalc(1920, 2880, CAMRES_W)
RES_PREVIEW = (640, 480)
RES_PHOTO = (CAMRES_W, CAMRES_H)


SetEffect('none')
camera.resolution = RES_PREVIEW
camera.start_preview(alpha=PREVIEW_ALPHA)
sleep(2) # This seems to be recommended when starting the camera.

running = 1

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
            QuitGracefully()
    #elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTMOUSEBUTTON:
    #   print("You released the left mouse button at (%d, %d)" % event.pos)

    if LastTap != 0 and time.time()-LastTap > IDLETIME:
        IdleReset()

    if globalKonamiLast == 'A' or globalKonamiLast == 'B' or globalKonamiLast == 'Right2':
        ShowTapZones(True)
    else:
        ShowTapZones(False)
########## End of Main