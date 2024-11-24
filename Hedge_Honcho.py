import pyautogui
import time
import numpy as np
from PIL import Image
import win32api
import win32con
import math
import cv2
import keyboard


# Parameters to play
screenWidth = 257
screenHeight = 190
HeightDifference = 240
lowerLimitThresholdLeaf = [32, 81, 188]
upperLimitThresholdLeaf = [64, 192, 250]
lowerLimitThresholdLadybug = [0, 146, 162]
upperLimitThresholdLadybug = [9, 255, 252]
lowerLimitThresholdBee = [21, 156, 128]
upperLimitThresholdBee = [28, 255, 255]

def setup():


    posLogo = pyautogui.locateOnScreen("MarioPartyDS_Resources/_SharedResources/melonDS_Symbol.png", confidence = 0.95)

    step = 0
    start = False


    while True:

        if step == 0: # Wait game to start
            try: start = pyautogui.locateOnScreen("MarioPartyDS_Resources/_SharedResources/Start.png", confidence = 0.90)
            except: pass
            if start: step = 1

        if step == 1:
            play(posLogo)
            break

def play(posLogo):

    # Obtain window coordinates, we only need bottom screen
    leftScreen = int(posLogo[0] - 6)
    topScreen = int(posLogo[1] + HeightDifference)
    rightScreen = leftScreen + screenWidth
    bottomScreen = topScreen + screenHeight
    CenterX = posLogo[0] + int(screenWidth/2) - 10
    CenterY = topScreen + int(screenHeight/2) + 10
    stop = True


    while True:

        # Ensure mouse doesn't start clicking
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # Obtaining screenshot for lower screen only and converting to HSV
        region = (leftScreen, topScreen, screenWidth, screenHeight)  # Left, top, width, height
        img = pyautogui.screenshot(region = region)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert image from BGR to HSV

        # Filter image to see only brightest region where the top leaf is
        lowerLimitLeaf = np.array(lowerLimitThresholdLeaf, dtype=np.uint8)
        upperLimitLeaf = np.array(upperLimitThresholdLeaf, dtype=np.uint8)
        maskedImgLeaf = cv2.inRange(hsvImg, lowerLimitLeaf, upperLimitLeaf)  # Create mask to see only the color specified

        # Filter image to see only red for ladybug
        lowerLimitLadybug = np.array(lowerLimitThresholdLadybug, dtype=np.uint8)
        upperLimitLadybug = np.array(upperLimitThresholdLadybug, dtype=np.uint8)
        maskedImgLadybug = cv2.inRange(hsvImg, lowerLimitLadybug, upperLimitLadybug)  # Create mask to see only the color specified
        redPixelsCount = cv2.countNonZero(maskedImgLadybug)

        # Filter image to see only yellow for bee
        lowerLimitBee = np.array(lowerLimitThresholdBee, dtype=np.uint8)
        upperLimitBee = np.array(upperLimitThresholdBee, dtype=np.uint8)
        maskedImgBee = cv2.inRange(hsvImg, lowerLimitBee, upperLimitBee)  # Create mask to see only the color specified
        yellowPixelsCount = cv2.countNonZero(maskedImgBee)

        cv2.imshow("Ladybug Filter", maskedImgLadybug)
        cv2.imshow("Bee Filter", maskedImgBee)
        cv2.imshow("Leaf Filter", maskedImgLeaf)

        if yellowPixelsCount >= 200: # If Bee present do nothing
            pass
        elif redPixelsCount >= 200: # If ladybug is detected remove it
            edgesImg = cv2.Canny(maskedImgLadybug, 30, 200)
            M = cv2.moments(edgesImg)
            try: cxLadybug = int(M['m10'] / M['m00'])
            except: pass
            try: cyLadybug = int(M['m01'] / M['m00'])
            except: pass
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            pyautogui.moveTo(leftScreen + cxLadybug + 10, topScreen + cyLadybug + 20, 0.1)
            pyautogui.moveRel(0, -30, 0.1)
            pyautogui.moveRel(0, 30, 0.1)
            print("Ladybug")
        else: # Move and drag mouse to remove leaf
            edgesImg = cv2.Canny(maskedImgLeaf, 30, 200)
            M = cv2.moments(edgesImg)
            try: cxLeaf = int(M['m10'] / M['m00'])
            except: pass
            try: cyLeaf = int(M['m01'] / M['m00'])
            except: pass
            NewX = int((leftScreen + (cxLeaf) - CenterX) * 2.5)
            NewY = int((topScreen + (cyLeaf) - CenterY) * 2.5)
            print("NewX:" + str(NewX) + ", leftScreen: " + str(leftScreen))
            if NewX < (leftScreen - CenterX): NewX = leftScreen - CenterX # Ensuring cursor won't move off window
            if NewX > (rightScreen - CenterX): NewX = rightScreen - CenterX  # Ensuring cursor won't move off window
            if NewY < (topScreen - CenterY): NewY: topScreen - CenterY + 60
            if NewY > (bottomScreen - CenterY): NewY: bottomScreen - CenterY - 35
            win32api.SetCursorPos((CenterX, CenterY))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            # pyautogui.moveRel(int(NewX*-1), int((NewY)), 0.5)

            pyautogui.moveRel(NewX, NewY, 0.1)
            # pyautogui.moveTo(int(leftScreen + (cxLeaf)), int(topScreen + (cyLeaf)), 0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # cv2.circle(img, (cxLeaf, cyLeaf), 5, (255, 0, 0), -1)
        # cv2.imshow("Image", edgesImg)
        # cv2.waitKey()

        while stop:
            if keyboard.is_pressed('w'):  # Stop program by pressing the "q" keyboard
                stop = False
                break

        cv2.waitKey(1)
        if keyboard.is_pressed('q'):  # Stop program by pressing the "q" keyboard
            break


time.sleep(2) # Just to allow enough time for user to open game window
print("Program initiated")
setup()