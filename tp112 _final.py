#Jacob Bauldock interface portion
from tkinter import *
import random
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2

class Food(object):
    def __init__(self, cx, cy, vx, vy, weight):
        self.cx = cx
        self.cy = cy
        self.r = random.randint(20, 40)
        self.speed = 5
        self.weight = weight
        #self.color = random.choice(["lime", "orange", "blue", "green", "pink", "purple", "white", "yellow", "red",
         #                           "lime", "orange", "blue", "pink", "purple", "yellow", "lime", "orange", "red",
          #                          "blue", "pink", "purple", "yellow", "red"])
        self.image = PhotoImage(file= 'C:\\Users\\jacob\PycharmProjects\\15112_jbauldoc\\15-112 hw\\TP\\atoms - Copy\\Carbon.gif')
        self.gravity = 9.8
        self.vx = vx
        self.vy = vy
        self.dt = .035
        # self.lst = lst

    def drawFood(self, canvas):
        canvas.create_image(self.cx - self.r, self.cy - self.r,
                           self.cx + self.r, self.cy + self.r, image= self.image)

    def getColor(self):
        return self.color

    def changeSpeedY(self):
        self.vy += self.gravity * self.dt
        # print(self.vy)

    def moveFood(self):
        self.cx += self.vx #* random.choice[1, -1]
        self.cy += self.vy

    def collidesWithOtherFood(self, other):
        distance = ((other.cx - self.cx)**2 + (other.cy - self.cy)**2)**0.5
        if distance <= self.r + other.r:
            tempvy = self.vy
            tempvx = self.vx

            self.vy = other.vy
            self.vx = other.vx

            other.vy = tempvy
            other.vx = tempvx

    def isOffScreen(self, width, height):
        if self.cx - self.r < 0:
            self.vx *= -1
        elif self.cx + self.r > width:
            self.vx *= -1
        return height + 100 <= self.cy - self.r

    def collidesWithPlayer(self, data):
        # print(data.tempMouth)
        if len(data.tempMouth) >= 0:
            if data.tempMouth[0][0] <= self.cx <= data.tempMouth[6][0] and \
                    data.tempMouth[3][1] <= self.cy <= data.tempMouth[9][1]:
                return True

# class Player(object):
#     def __init__(self, data):
#         self.lst = data.facePoints
#
#         print(self.lst)
#
#     def outlineMouth(self, data, canvas):
#         try:
#             canvas.create_polygon(data.facePoints, fill="green", width=2)
#         except:
#             self.lst = []
#         self.lst = []

def init(data):
    data.mode = "mainMenu"
    data.timer = 0
    data.r = random.randint(20,30)
    data.score = 0
    data.food = []
    data.time = 60
    print("[INFO] loading facial landmark predictor...")
    data.detector = dlib.get_frontal_face_detector()
    data.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    print("[INFO] camera sensor warming up...")
    data.video = VideoStream(0).start()
    data.landmarks = []
    data.facePoints = []
    data.tempMouth = []
    data.mouthOpen = None
    data.lives = 5
    data.isPoisoned = None
    data.poisonTime = 0
    data.posionColor = "black"
    # data.player = Player(data)

def mouth_aspect_ratio(mouth):
   # repeat the same format as above however this time make it applicable to the points around the mouth
   D = dist.euclidean(mouth[13], mouth[19])
   E = dist.euclidean(mouth[14], mouth[18])
   F = dist.euclidean(mouth[15], mouth[17])

   # horizontal points
   G = dist.euclidean(mouth[12], mouth[16])

   # calculation for mouth aspect ratio
   mar = (D + E + F) / (3.0 * G)

   return mar

def videoCapture(data):
    frame = data.video.read()

    if data.isPoisoned is True:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    elif data.isPoisoned is False or data.isPoisoned is None:
        frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=data.width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    MOUTH_AR_THRESH = 0.1
    # MOUTH_AR_CONSEC_FRAMES = 3

    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    # detect faces in the grayscale frame
    rects = data.detector(gray, 0)

    for rect in rects:
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = data.predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        # print(shape)
        # print(len(shape))

        #append a tuple of the coordinates to a list so that i can draw them
        for (x, y) in shape:
            data.landmarks.append((x, y))

        for (x, y) in shape[48:59]:
            data.facePoints.append((x, y))
            data.tempMouth.append((x,y))
        # print(data.tempMouth)
        mouth = shape[mStart: mEnd]
        mouthMAR = mouth_aspect_ratio(mouth)

        mar = mouthMAR
        print(mar)


        if mar > MOUTH_AR_THRESH:
            data.mouthOpen = True
        else:
            data.mouthOpen = False

    # print(data.mouthOpen)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `x` key was pressed, break from the loop
    if key == ord("x"):
        sys.exit(0)

def drawFace(data, canvas):
    for point in data.landmarks:
        # print(point)
        x, y = point
        canvas.create_oval(x + 1, y + 1, x - 1, y - 1, fill = "yellow")
        data.landmarks = []

def outlineMouth(data, canvas):
    try:
        canvas.create_polygon(data.facePoints, fill = "green", width = 2)
    except:
        data.facePoints = []
    data.facePoints = []

# different modes
def mousePressed(event, data):
    if data.mode == "mainMenu": mainMenuMousePressed(event, data)
    elif data.mode == "play" : playMousePresed(canvas, data)
    elif data.mode == "timeAttack": timeAttackMousePressed(event, data)
    elif data.mode == "zenMode": zenModeMousePresed(event, data)
    elif data.mode == "classic": classicMousePressed(event, data)
    elif data.mode == "endGame": endGameMousePressed(event, data)

def keyPressed(event, data):
    if data.mode == "mainMenu": mainMenuKeyPressed(event, data)
    elif data.mode == "play" : playKeyPressed(event, data)
    elif data.mode == "timeAttack": timeAttackKeyPressed(event, data)
    elif data.mode == "zenMode": zenModeKeyPressed(event, data)
    elif data.mode == "classic": classicKeyPressed(event, data)
    elif data.mode == "endGame": endGameKeyPressed(event, data)
    elif data.mode == "help": helpKeyPressed(event, data)

def timerFired(data):
    if data.mode == "mainMenu": mainMenuTimerFired(data)
    elif data.mode == "play": playTimerFired(data)
    elif data.mode == "timeAttack": timeAttackTimerFired(data)
    elif data.mode == "zenMode": zenModeTimerFired(data)
    elif data.mode == "classic": classicTimerFired(data)
    elif data.mode == "endGame": endGameTimerFired(data)
    elif data.mode == "help": helpTimerFired(data)

def redrawAll(canvas, data):
    if data.mode == "mainMenu": mainMenuRedrawAll(canvas, data)
    elif data.mode == "play" : playRedrawAll(canvas, data)
    elif data.mode == "timeAttack": timeAttackRedrawAll(canvas, data)
    elif data.mode == "zenMode": zenModeRedrawAll(canvas, data)
    elif data.mode == "classic": classicRedrawAll(canvas, data)
    elif data.mode == "endGame": endGameRedrawAll(canvas, data)
    elif data.mode == "help": helpRedrawAll(canvas, data)

#main menu########################################################################################################
def drawText(canvas, data):
    canvas.create_text(data.width/2, 65, text = "feeding frenzy 112", font = "arial 30 bold", fill = "white")

def makeButton(canvas, data):
    # canvas.create_rectangle(data.width/2 + 80, data.height/2 - 30, data.width/2 - 80, data.height/2 + 30, fill = "red")
    canvas.create_text(data.width/2 + 120, data.height/2 + 10, text = "press p to play", font = "arial 16 bold",
                       fill = "white")
    canvas.create_text(data.width/2 + 120, data.height/2 + 40, text = "press h for help", font = "arial 16 bold",
                       fill = "white")
    # canvas.create_rectangle(data.width/2 + 80, data.height/2 + 40, data.width/2 - 80, data.height/2 + 100, fill = "green")

def drawFaceBox(canvas, data):
    canvas.create_rectangle(15, 110, 260, 350, width = 1, fill = "gray")
    canvas.create_text(125, 375, text = "Fit your head in the box \nand keep this distance", font = "arial 12 bold",
                       fill = "white")


def mainMenuMousePressed(event, data):
    pass

def mainMenuKeyPressed(event, data):
    if event.char == "p":
        data.mode = "play"
    elif event.char == "h":
        data.mode = "help"

def mainMenuTimerFired(data):
    videoCapture(data)
    data.tempMouth = []

def mainMenuRedrawAll(canvas, data):
    drawText(canvas, data)
    makeButton(canvas, data)
    drawFaceBox(canvas, data)
    outlineMouth(data, canvas)
    drawFace(data, canvas)


# help mode #############################################

def helpKeyPressed(event, data):
    if event.char == "m":
        data.mode = "mainMenu"

def helpTimerFired(data):
    pass

def helpRedrawAll(canvas, data):
    canvas.create_text(270, 170, text = """READ.ME
Let’s play feeding Frenzy. 

Classic mode
Classic mode is like the classic mode in Fruit ninja. 
The goal is to last as long as possible while eating the most amount of fruit. 
Everytime you eat either a red food or you let a food drop without catching it you lose a life
and become poisoned. 
When your lives go down you lose

Time attack 
The goal of this mode is to get the most amount of fruit possible 
in the alloted time. Same rules apply as from above, however if you 
are aloud to let fruit drop
NOTE: WHEN YOU ARE POISONED YOU WILL TURN BLUE ON THE CVSCREEN. this lasts
for 5 seconds

Zen mode
If you just want to eat food without the pressure of poisonous food, 
zen mode is for you. Here lesurely eat food at your own pace until the timer runs out, 
just so you can get the hang of it

press "m" to go back to the main menu""", font = "arial 8 bold", fill = "white")

#play mode ###################################################################################
def drawPlayText(canvas, data):
    canvas.create_text(data.width/2, 75, text = "Select a mode", font = "arial 30 bold", fill = "white")
    canvas.create_text(data.width/2 + 120, data.height/2 - 10, text = "press c for Classic Mode", font = "arial 12 bold"
                        ,fill = "white")
    canvas.create_text(data.width/2 + 120, data.height/2 + 30, text = "press t for Time Attack", font = "arial 12 bold",
                       fill="white")
    canvas.create_text(data.width / 2 + 120, data.height / 2 + 70, text="press z for Zen Mode", font="arial 12 bold",
                       fill="white")

def playMousePresed(event, data):
    pass

def playKeyPressed(event, data):
    if event.char == "c":
        data.mode = "classic"
    elif event.char == "t":
        data.mode = "timeAttack"
    elif event.char == "z":
        data.mode = "zenMode"

def playTimerFired(data):
    videoCapture(data)
    data.tempMouth = []

def playRedrawAll(canvas, data):
    drawPlayText(canvas, data)
    drawFaceBox(canvas, data)
    outlineMouth(data, canvas)
    drawFace(data, canvas)

def poisonTimer(data):
    if data.isPoisoned is True:
        data.poisonTime += 1
        if data.poisonTime % 50 == 0:
            data.isPoisoned = False
            data.poisonTime = 0

def scoreBelowZero(data):
    if data.score < 0:
        data.score = 0

#### classic Mode #########################################################
def classicMousePressed(event, data):
    pass

def classicKeyPressed(event, data):
    pass

def classicTimerFired(data):
    poisonTimer(data)

    filler = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    if len(data.tempMouth) <= 0:
        data.tempMouth = filler

    data.timer += 1

    #if data.timer % random.choice([10, 20, 30, 30, 40, 40, 40, 40, 50, 50, 50, 50, 50]) == 0:
    if data.timer % random.choice([10, 20, 30, 30, 40, 40, 40]) == 0:
        #for i in range(random.choice([1, 1, 1, 1, 1, 1, 1, 2, 2, 3])):
        for i in range(random.choice([1, 1, 1, 1, 1, 1])):
            data.food.append(Food(random.randint(data.r + 10, data.width - data.r - 10), data.height + data.r,
                                  random.randint(-5, 5), random.randint(-15, -13), random.randint(1, 3)))
    # print(data.food)
    for item in data.food:
        item.moveFood()
        item.changeSpeedY()
        for jtem in data.food:
            item.collidesWithOtherFood(jtem)
        if item.collidesWithPlayer(data) is True and data.mouthOpen is True:
            data.food.remove(item)
            if item.getColor == "white":
                data.isPoisoned = False
                data.score += 3
            if item.getColor() != "red":
                data.score += 1
            elif item.getColor() == "red":
                data.score -= 5
                data.lives -= 1
                data.isPoisoned = True

        if item.isOffScreen(data.width, data.height):
            # print("is it working")
            if item.getColor() != "red":
                data.lives -= 1
            data.food.remove(item)

    scoreBelowZero(data)

    # print(len(data.food))
    try:
        data.tempMouth = []
    except:
        pass
    pass

    videoCapture(data)

    if data.lives == 0:
        data.mode = "endGame"

def classicRedrawAll(canvas, data):
    for item in data.food:
        item.drawFood(canvas)
    canvas.create_text(data.width - 40, 20, text = "score:" + str(data.score), font = "arial 12 bold", fill = "white")
    canvas.create_text(40, 20, text = "lives:" + str(data.lives), font = "arial 12 bold", fill = "white")
    outlineMouth(data, canvas)
    drawFace(data, canvas)

# time attack ################################################################################

def timeAttackMousePresed(event, data):
    pass

def timeAttackKeyPressed(event, data):
    if event.keysym == "Right":
        data.player.movePlayer(5, 0)
    elif event.keysym == "Left":
        data.player.movePlayer(-5, 0)
    elif event.keysym == "Up":
        data.player.movePlayer(0, -5)
    elif event.keysym == "Down":
        data.player.movePlayer(0, 5)

def timeAttackTimerFired(data):
    #quick fix to small bug
    poisonTimer(data)

    filler = [(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)]
    if len(data.tempMouth) <= 0:
        data.tempMouth = filler

    poisonTimer(data)

    data.timer += 1
    data.time -= .1
    print(data.timer)
    #if data.timer % random.choice([10, 20, 30, 30, 40, 40, 40, 50, 50, 50, 50, 50]) == 0:
    if data.timer % random.choice([10, 20, 30, 30, 40, 40]) == 0:
        #for i in range(random.choice([1, 1, 1, 1, 1, 1, 2, 2, 3, 3])):
        for i in range(random.choice([1, 1, 1, 1, 1, 1])):
            data.food.append(Food(random.randint(data.r, data.width - data.r), data.height + data.r,
                                  random.randint(-5, 5), random.randint(-15, -13)))
    # print(data.food)
    for item in data.food:
        item.moveFood()
        item.changeSpeedY()
        for jtem in data.food:
            item.collidesWithOtherFood(jtem)
        if item.collidesWithPlayer(data) is True and data.mouthOpen is True:
            data.food.remove(item)
            if item.getColor() != "red":
                data.score += 1
            elif item.getColor == "white":
                data.score += 3
                data.isPoisoned = False
            else:
                data.score -= 5
                data.isPoisoned = True

        if item.isOffScreen(data.width, data.height):
            data.food.remove(item)

    scoreBelowZero(data)

    try:
        data.tempMouth = []
    except:
        pass
    pass

    videoCapture(data)

    if data.time <= 0:
        data.mode = "endGame"

def timeAttackRedrawAll(canvas, data):
    for item in data.food:
        item.drawFood(canvas)
    canvas.create_text(data.width - 20, 20, text = data.score, font = "arial 16 bold", fill = "white")
    canvas.create_text(20, 20, text = int(data.time), font = "arial 16 bold", fill = "white")
    # data.player.drawPlayer(canvas)
    outlineMouth(data, canvas)
    drawFace(data, canvas)

# zen mode ####################################################################################
def zenModeMousePresed(event, data):
    pass

def zenModeKeyPressed(event, data):
    pass

def zenModeTimerFired(data):
    # quick fix to small bug
    poisonTimer(data)

    filler = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    if len(data.tempMouth) <= 0:
        data.tempMouth = filler

    poisonTimer(data)

    data.timer += 1
    data.time -= .1
    #print(data.timer)
    #if data.timer % random.choice([10, 20, 30, 30, 40, 40, 40, 50, 50, 50, 50, 50]) == 0:
    if data.timer % random.choice([10, 20, 30, 30, 40, 40, 50]) == 0:
        #for i in range(random.choice([1, 1, 1, 1, 1, 1, 2, 2, 3, 3])):
        for i in range(random.choice([1, 1, 1, 1, 1, 1])):
            data.food.append(Food(random.randint(data.r, data.width - data.r), data.height + data.r,
                                  random.randint(-5, 5), random.randint(-15, -13)))
    # print(data.food)
    for item in data.food:
        item.moveFood()
        item.changeSpeedY()
        for jtem in data.food:
            item.collidesWithOtherFood(jtem)
        if item.collidesWithPlayer(data) is True and data.mouthOpen is True:
            data.food.remove(item)
            data.score += 1
            if item.getColor == "white":
                data.score += 3



        if item.isOffScreen(data.width, data.height):
            data.food.remove(item)

    try:
        data.tempMouth = []
    except:
        pass
    pass

    videoCapture(data)

    if data.time <= 0:
        data.mode = "endGame"

def zenModeRedrawAll(canvas, data):
    for item in data.food:
        if item.getColor() == "red":
            data.food.append(item)
        else:
            item.drawFood(canvas)
    canvas.create_text(data.width - 20, 20, text = data.score, font = "arial 16 bold", fill = "white")
    canvas.create_text(20, 20, text = int(data.time), font = "arial 16 bold", fill = "white")
    # data.player.drawPlayer(canvas)
    outlineMouth(data, canvas)
    drawFace(data, canvas)



# end game #####################################################################################
def drawEndScreen(canvas, data):
    canvas.create_text(data.width / 2, 50, text="Your Time Ran Out", font="arial 20 bold", fill = "white")
    canvas.create_text(data.width / 2, 100, text="Game Over", font="arial 30 bold", fill = "white")
    canvas.create_text(data.width / 2, 175, text="Final Score: " + str(data.score),
                       font="arial 20 bold", fill = "white")
    canvas.create_text(data.width / 2, 250, text="Press \"m\" to start again", font="arial 20 bold", fill = "white")

def endGameMousePresed(event, data):
    pass

def endGameKeyPressed(event, data):
    if event.char == "m":
        data.score = 0
        data.isPoisoned = None
        data.lives = 5
        data.time = 60
        data.food = []
        data.mode = "mainMenu"

def endGameTimerFired(data):
    pass

def endGameRedrawAll(canvas, data):
    drawEndScreen(canvas, data)

#from 15-112 website
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='black', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 10 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(500, 400)