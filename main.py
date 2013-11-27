import sys
import os
import random
from PyQt4 import QtGui
from PyQt4 import QtCore

if sys.platform == 'win32':
    # Running on Windows
    import winsound
    winsound.PlaySound(os.path.dirname(__file__) + '\data\intro.wav', winsound.SND_ASYNC)


class Window(QtGui.QWidget):
    
    def __init__(self):
        # Initialize the window
        super(Window, self).__init__()
        
        # Set up the UI 
        self.setGeometry(0, 0, 820, 620)
        # Move the window to the screen center
        self.move(self.center(self.frameGeometry(), QtGui.QDesktopWidget().frameGeometry()))
        # Init the Game
        self.game = Game()
        self.game_window = GameWindow(self)
        
        # Take care of the Layout
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game_window)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        # Other stuff
        self.setWindowTitle('Shooter')
        self.show()
        
    def center(self, widget_frame, target_frame):
        widget_frame.moveCenter(target_frame.center())
        return widget_frame.topLeft()


class Game():
    
    gameCycleInterval = 10 # Time in ms
    
    def __init__(self):
        self.map = Map('debug')
        self.player = Player(1, 1, 20, 20)


class GameWindow(QtGui.QFrame):
    
    def __init__(self, parent):
        
        # Init the UI element
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFixedSize(800, 600)
        self.setFrameStyle(QtGui.QFrame.Box)
        
        self.xStretch = self.width() / float(parent.game.map.viewSize.width())
        self.yStretch = self.height() / float(parent.game.map.viewSize.height())
        
        # Var definition
        self.keyList = []
        self.youRect = QtCore.QRect()
        self.obstOutlinesList = []
        self.intersection = QtCore.QPointF()
        self.gameCycleTimer = QtCore.QBasicTimer()
        self.gameCycleTimer.start(Game.gameCycleInterval, self)
         
    def draw_Player(self, painter, Rect):
        
        # Draw the player
        painter.drawRect(QtCore.QRect(QtCore.QPoint(Rect.topLeft().x() * self.xStretch, Rect.topLeft().y() * self.yStretch), QtCore.QPoint(Rect.bottomRight().x() * self.xStretch, Rect.bottomRight().y() * self.yStretch)))
    
    def draw_Obstacles(self, painter, obstRectList):
        
        # Draw all obstacles
        for polygon in obstRectList:
            plist = []
            for point in polygon:
                plist.append(QtCore.QPoint(point.x() * self.xStretch, point.y() * self.yStretch))
            painter.drawPolygon(QtGui.QPolygon(plist))
        
    def draw_Shot(self, painter, shotLineList):
        
        for line in shotLineList:
            painter.drawLine(QtCore.QLine(QtCore.QPoint(line.p1().x() * self.xStretch, line.p1().y() * self.yStretch), QtCore.QPoint(line.p2().x() * self.xStretch, line.p2().y() * self.yStretch)))
        
    def draw_IndiLine(self, painter):
        
        line = QtCore.QLineF(QtCore.QPoint(main_UI.game.player.center().x() * self.xStretch, main_UI.game.player.center().y() * self.yStretch), main_UI.game.player.center() + QtCore.QPoint(1,0))
        line.setLength(main_UI.game.player.indiLineLength)
        line.setAngle(main_UI.game.player.angle)
        
        painter.drawLine(line)
    
    def keyPressEvent(self, event):
        
        # Append the pressed key to keyList 
        # It contains every currently pressed key
        key = event.key()
        self.keyList.append(key)
    
    def keyReleaseEvent(self, event):
        
        # Remove the pressed key from keyList 
        # It contains every currently pressed key
        key = event.key()
        self.keyList.remove(key)
        
    def timerEvent(self, event):
        if event.timerId() == self.gameCycleTimer.timerId():
            # The gameCycleTimer fired the event
            
            # Check for key presses and save next move in nextMoveDir
            # Reset nextMoveDir
            main_UI.game.player.nextMoveDir = QtCore.QPoint(0,0)
            
            for a in range(len(self.keyList)):
                key = self.keyList[a]
                if key == QtCore.Qt.Key_Left:
                    # the Left key is pressed
                    main_UI.game.player.nextMoveDir.setX(main_UI.game.player.nextMoveDir.x() - 1)
                elif key == QtCore.Qt.Key_Right:
                    # the Right key is pressed
                    main_UI.game.player.nextMoveDir.setX(main_UI.game.player.nextMoveDir.x() + 1)
                elif key == QtCore.Qt.Key_Up:
                    # the Up key is pressed
                    main_UI.game.player.nextMoveDir.setY(main_UI.game.player.nextMoveDir.y() - 1)
                elif key == QtCore.Qt.Key_Down:
                    # the Down key is pressed
                    main_UI.game.player.nextMoveDir.setY(main_UI.game.player.nextMoveDir.y() + 1)
                elif key == QtCore.Qt.Key_Q:
                    # Change player angle to turn left
                    main_UI.game.player.angle += main_UI.game.player.turnSpeed
                    # If angle gets larger than 360, 
                    if main_UI.game.player.angle >= 360:
                        main_UI.game.player.angle = main_UI.game.player.angle - 360
                elif key == QtCore.Qt.Key_E:
                    # Change player angle to turn right
                    main_UI.game.player.angle -= main_UI.game.player.turnSpeed
                    # If angle gets less than 0, turn it to fit into 0 - 360 again
                    if main_UI.game.player.angle < 0:
                        main_UI.game.player.angle = 360 + main_UI.game.player.angle
                elif key == QtCore.Qt.Key_Space:
                    # Shoot
                    memory = QtCore.QLineF(main_UI.game.player.pos, main_UI.game.player.pos + QtCore.QPoint(1,0))
                    memory.setAngle(main_UI.game.player.angle)
                    memory.setLength(main_UI.game.player.shot.maxLength)
                    main_UI.game.player.shot.tryShot(main_UI.game.player.center(), memory.p2())
                elif key == QtCore.Qt.Key_X:
                    print(str(main_UI.game.map.viewSize))
                    main_UI.game.map.changeViewSize(main_UI.game.map.viewSize.width() + 1, main_UI.game.map.viewSize.height() + 1)
                    
                    
            # The next move is the player position + nextMoveDir
            # to amplify move Speed, the nextMoveDir is multiplied with self.moveSpeed
            if main_UI.game.player.nextMoveDir.x() != 0 or main_UI.game.player.nextMoveDir.y() != 0:
                main_UI.game.player.tryMove(main_UI.game.player.pos, main_UI.game.player.nextMoveDir, main_UI.game.player.moveSpeed)
            
            # do all logic here in the future
            
            # Update the scene AFTER all logic work
            self.update()
            
    def changeStretch(self):
        
        self.xStretch = self.width() / float(main_UI.game.map.viewSize.width())
        self.yStretch = self.height() / float(main_UI.game.map.viewSize.height())
        
    def paintEvent(self , event):
        # Initialize painter
        painter = QtGui.QPainter()       
        painter.begin(self) 
        # Basic painter setup
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Player gets drawn
        self.draw_Player(painter, QtCore.QRect(main_UI.game.player.pos, main_UI.game.player.size))
        
        # Obstacles get drawn
        self.draw_Obstacles(painter, main_UI.game.map.obstacleList)
        
        # Shot computation
        if main_UI.game.player.shot.timer.isActive():
            # A Shot is currently up to draw
            # Compute its shortest distance before it hits an obstacle
            
            # Get the length the shot should have
            self.length = main_UI.game.player.shot.maxLength
            self.shotStartPos = main_UI.game.player.shot.startPos
            self.shotEndPos = main_UI.game.player.shot.endPos
            self.angle = QtCore.QLineF(self.shotStartPos, self.shotEndPos).angle()
            self.shotLineList = []
            
            # Iterate through the loop until the remaining length = 0
            # It then executes the else statement
            while self.length > 0.0:
                self.shotEndPos, self.angle, self.length = main_UI.game.player.shot.computeShot(self.shotStartPos, self.angle, self.length)
                self.shotLineList.append(QtCore.QLineF(QtCore.QPointF(self.shotStartPos), self.shotEndPos))
                self.shotStartPos = self.shotEndPos
        
            self.draw_Shot(painter, self.shotLineList)
                
                
        # Draw angle indicator
        self.draw_IndiLine(painter)
                
        # TEST
        self.drawFrame(painter)
              
        painter.end()


class Map():
    
    def __init__(self, loadType):
        
        # Contains every obstacle element that is present in the map
        self.obstacleList = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlinesList = []
        
        # Init the map and declare which map to use
        if loadType == 'debug':
            # Just load the debug map
            self.loadfromTest()
        else:
            print('loadType not supported')
            
    def addObstacle(self, pointList):
        
        # Create the obstacle
        obstacle = Obstacle(pointList)
        
        # Add the obstacle to the lists obstacleList and outlinesList
        self.obstacleList.append(obstacle.polygon)
        self.outlinesList.append(obstacle.Outlines())
        
    def loadfromTest(self):
        
        # This method loads up a debugging map which is declared in here
        self.size = QtCore.QSize(800,600)
        self.viewSize = QtCore.QSize(300,300)
        self.addObstacle([QtCore.QPoint(100,100), QtCore.QPoint(390,100), QtCore.QPoint(390,290), QtCore.QPoint(100,290)])
        self.addObstacle([QtCore.QPoint(500,500), QtCore.QPoint(690,500), QtCore.QPoint(790,590), QtCore.QPoint(500,590)])
        
    def changeViewSize(self, w, h):
        if w <= main_UI.game_window.width():
            self.viewSize.setWidth(w)
        if h <= main_UI.game_window.height():
            self.viewSize.setHeight(h)
            
        main_UI.game_window.changeStretch()


class Shot():
    
    def __init__(self):

        self.startPos = QtCore.QPoint(0,0)
        self.endPos = QtCore.QPoint(0,0)
        self.shotUpTime = 400 # ms how long the shot should be visible
        self.maxLength = 1000
        
        self.initTimer()
        
    def initTimer(self):
        # A Timer to fade out the shot after a certain time is initiated
        self.timer = QtCore.QTimer()
        QtCore.QTimer.setInterval(self.timer, self.shotUpTime)
        QtCore.QTimer.setSingleShot(self.timer, True)
        self.timer.stop()
        
    def tryShot(self, sPoint, ePoint):
        # Try to set new shot
        # This is only possible if the old shot has faded away
        if self.timer.isActive() == False:
            self.startPos = sPoint
            self.endPos = ePoint
            # The fade out timer is started
            self.timer.start()
            
            # EARLY SOUNDS
            winsound.PlaySound(os.path.dirname(__file__) + '\data\shot' + str(random.randint(0,1) + 1) + '.wav', winsound.SND_ASYNC)
            
    def computeShot(self, startPoint,  angle, length):
        # Returns the end point of the shot
        # whether its the actual end or just a collision with an obstacle can be seen in var Length
        # if remaining Length is 0 after calling the method, its the actual endpoint of the line
        # if remaining Lenfth is not 0, call the method again with the remaining length
        
        # The method also returns the outgoing angle of the line if it has hit an obstacle
        # Therefore it CHANGES var angle and var length
        
        
        # Create the ideal line
        self.maxLine = QtCore.QLineF(startPoint, startPoint + QtCore.QPoint(1,0))
        self.maxLine.setLength(length)
        self.maxLine.setAngle(angle)
        
        # Find the intersection between that line and all obstacle outlines
        self.obstOutlinesList = main_UI.game.map.outlinesList
        self.intersection = QtCore.QPointF()
        
        # Iterate trough all outlines
        for a in range(len(self.obstOutlinesList)):
            for b in range(len(self.obstOutlinesList[a])):
                if self.maxLine.intersect(self.obstOutlinesList[a][b], self.intersection) == 1:
                    # Intersection of both lines in self.intersection
                    self.maxLine = QtCore.QLineF(startPoint, self.intersection)
                    print('intersection')
                    # Compute the outgoing angle of the shot
                    # It is done here, because I need the obstacle outline to compute it
                    angle = self.maxLine.angleTo(self.obstOutlinesList[a][b]) + self.obstOutlinesList[a][b].angle()
                else:
                    print('No intersection')
                    
        # maxLine is now as short as possible
        
        # Return the remaining length
        length = length - round(self.maxLine.length())

        # Get angle inside 0 - 360
        if angle >= 360:
            angle = angle - 360
        elif angle < 0:
            angle = 360 + angle
        
        # Set legth of maxLine
        # If not done, the start point of the next line would instantly intersect the same outline again
        # Resulting in an infinite loop
        self.maxLine.setLength(self.maxLine.length() - 1)
        
        return (self.maxLine.p2(), angle, length)      


class Obj():
    def center(self):
        return QtCore.QRect(self.pos, self.size).center()
    
    def Outlines(self):
        
        # Iterate through every index of polygon
        # every index represents a point
        # outline = line(i, i - 1)
        
        result = []
        for i in range(len(self.polygon)):
            print(self.polygon[i])
        # Index 0 is skipped because it has nothing to draw a line to
        # Start at index 1. Make a line from 0 to 1
        for a in range(1, len(self.polygon)):
            result.append(QtCore.QLineF(self.polygon[a-1], self.polygon[a]))
            # append the last line from the last index to 
        result.append(QtCore.QLineF(self.polygon[len(self.polygon) - 1], self.polygon[0]))
        return result
    
    
class Obstacle(Obj):
    
    def __init__(self, pointList):
        self.polygon = QtGui.QPolygon(pointList)


class Player(Obj):
    
    def __init__(self, x, y, w, h):
         
        self.pos = QtCore.QPoint(x,y)
        self.size = QtCore.QSize(w,h)
        self.shot = Shot()
        
        self.turnSpeed = 2
        self.angle = 0
        self.indiLineLength = 30
        self.moveSpeed = 5
        
        self.nextMoveDir = QtCore.QPoint(0,0)
        
    def tryMove(self, pos, mDir, ms):
        # Generate the new positions
        # Go through every possible new position in the direction (dir)
        # Start with full move speed (ms) and if it does not work, try the next lower step
        # Break out of the loop if next move is possible
            
        for a in range(ms, 1, -1):
            nRect = QtCore.QRect(QtCore.QPoint(pos.x() + mDir.x() * a, pos.y() + mDir.y() * a), self.size)          
            # Check if new positions are in bounds of the window
            if nRect.topLeft().x() >= 0 and nRect.topLeft().y() >= 0 and nRect.bottomRight().x() <= main_UI.game.map.viewSize.width() and nRect.bottomRight().y() <= main_UI.game.map.viewSize.height():
                # Positions are inside the window
                # Check if player comes into contact with an obstacle
                # Check if uL or bR of the player are contained by an obstacle
                
                # Iterate through the list of obstacles
                for a in range(len(main_UI.game.map.obstacleList)):
                    if main_UI.game.map.obstacleList[a].containsPoint(nRect.topLeft(), QtCore.Qt.OddEvenFill) % 2 == 1 or main_UI.game.map.obstacleList[a].containsPoint(nRect.topRight(), QtCore.Qt.OddEvenFill) % 2 == 1 or main_UI.game.map.obstacleList[a].containsPoint(nRect.bottomRight(), QtCore.Qt.OddEvenFill) % 2 == 1 or main_UI.game.map.obstacleList[a].containsPoint(nRect.bottomLeft(), QtCore.Qt.OddEvenFill) % 2 == 1:
                        # The player is inside an obstacle
                        # Break out of the loop because if player contains one obstacle its worthless to check any other
                        break
                    else:
                        # The player is outside of the obstacle
                        # Iterate to the next obstacle
                        continue
                else: 
                    # Getting here means no break was thrown
                    # No obstacle in the way
                    self.forceMove(nRect.topLeft()) 
                    return True
            else:
                # Positions are outside the window
                pass
            continue
        else:
            # Not even the smallest possible step (1) was possible
            return False
    
    def forceMove(self, Point):
        # Force a move command
        # Dont use! Use tryMove() instead.
        self.pos = Point 
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_UI = Window()
    sys.exit(app.exec_())