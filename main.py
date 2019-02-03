import cv2
import numpy as np
import math
import subprocess
import sys
import random
import os
import time


def getScreenshot(screenshotPath):
    process = subprocess.Popen(
        'adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    if sys.platform == 'win32':
        screenshot = screenshot.replace(b'\r\n', b'\n')
    f = open(screenshotPath, 'wb')
    f.write(screenshot)
    f.close()


def press(time):
    command = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=random.randint(0, 1080),
        y1=random.randint(0, 1920),
        x2=random.randint(0, 1080),
        y2=random.randint(0, 1920),
        duration=round(time)
    )
    os.system(command)


def getDistance(screenshotPath):
    screenshot = cv2.imread(screenshotPath)
    hsvScreenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

    penguinMask = cv2.inRange(hsvScreenshot, np.array(
        [0, 2, 30]), np.array([175, 35, 65]))
    cv2.imwrite("penguin_mask.png", penguinMask)

    possiblePenguinBottomYWithW = []
    tempW = 1
    preAppend = []
    for i, j in enumerate(penguinMask):
        if (j == 255).any():
            if (penguinMask[i - 1] != 255).all():
                preAppend.append(i)
            if (penguinMask[i + 1] != 255).all():
                preAppend = preAppend + [i, tempW]
                possiblePenguinBottomYWithW.append(preAppend)
                tempW = 1
                preAppend = []
            else:
                tempW = tempW + 1

    for i in possiblePenguinBottomYWithW:
        print("Penguin: Possible Y: Start:",
              i[0], "End:", i[1], "Weight:", i[2])

    def getW(elem): return elem[-1]
    possiblePenguinBottomYWithW.sort(key=getW, reverse=True)
    penguinBottomY = possiblePenguinBottomYWithW[0][1]
    penguinHeight = penguinBottomY - possiblePenguinBottomYWithW[0][0]
    print("Penguin: Selected Y:", penguinBottomY)
    print("Penguin: Height:", penguinHeight)

    possiblePenguinBottomX = np.where(penguinMask[penguinBottomY] == 255)[0]
    for i in possiblePenguinBottomX:
        print("Penguin: Possible X:", i)

    penguinBottomX = possiblePenguinBottomX[round(
        len(possiblePenguinBottomX)/2)]
    print("Penguin: Selected X:", penguinBottomX)

    startCenterX = penguinBottomX
    startCenterY = penguinBottomY - round(penguinHeight / 15)

    print("Start Center:", startCenterX, startCenterY)

    endMask = cv2.inRange(hsvScreenshot, np.array(
        [0, 180, 255]), np.array([1, 195, 255]))
    cv2.imwrite("end_mask.png", endMask)

    possibleEndBottomYWithW = []
    tempW = 1
    for i, j in enumerate(endMask):
        if (j == 255).any():
            if (endMask[i + 1] != 255).all():
                possibleEndBottomYWithW.append([i, tempW])
                tempW = 1
            else:
                tempW = tempW + 1

    for i in possibleEndBottomYWithW:
        print("End: Possible Y:", i[0], "Weight:", i[1])

    possibleEndBottomYWithW.sort(key=getW, reverse=True)
    for i, j in enumerate(possibleEndBottomYWithW):
        try:
            if abs(j[1] - possibleEndBottomYWithW[i + 1][1]) < 3:
                if j[0] < possibleEndBottomYWithW[i + 1][0]:
                    possibleEndBottomYWithW.pop(i + 1)
                else:
                    possibleEndBottomYWithW.pop(i)
        except:
            continue

    endBottomY = possibleEndBottomYWithW[0][0]
    print("End: Selected Y:", endBottomY)

    possibleEndBottomX = np.where(endMask[endBottomY] == 255)[0]
    for i in possibleEndBottomX:
        print("End: Possible X:", i)

    endBottomX = possibleEndBottomX[round(
        len(possibleEndBottomX)/2)]
    print("End: Selected X:", endBottomX)

    endCenterX = endBottomX
    endCenterY = endBottomY - round(penguinHeight * 1 / 8)

    print("End Center:", endCenterX, endCenterY)

    distance = math.sqrt((endCenterX - startCenterX)
                         ** 2 + (endCenterY - startCenterY) ** 2) / penguinHeight
    print("Distance:", distance)

    return distance


def main():
    while True:
        input()
        getScreenshot("screenshot.png")
        press(getDistance("screenshot.png") * 155)


if __name__ == "__main__":
    main()
