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
        self.move(center(self.frameGeometry(), QtGui.QDesktopWidget().frameGeometry()))
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


def center(widget_frame, target_frame):
    widget_frame.moveCenter(target_frame.center())
    return widget_frame.topLeft()


class Game():
    
    gameCycleInterval = 10  # Time in ms
    
    def __init__(self):
        self.map = Map('debug')
        self.player = Player(1, 1, 10, 10)


class GameWindow(QtGui.QFrame):
    
    def __init__(self, parent):
        
        # Init the UI element
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFixedSize(800, 600)
        self.setFrameStyle(QtGui.QFrame.Box)
        
        self.x_stretch = self.width() / float(parent.game.map.view_size.width())
        self.y_stretch = self.height() / float(parent.game.map.view_size.height())
        
        # Var definition
        self.key_list = []
        self.you_rect = QtCore.QRect()  # Never used????
        self.obst_outlines_list = []
        self.intersection = QtCore.QPointF()
        self.game_cycle_timer = QtCore.QBasicTimer()
        self.game_cycle_timer.start(Game.gameCycleInterval, self)

        # Shot functions definitions
        self.shot_start_pos = 0
        self.shot_end_pos = 0
        self.shot_line_list = []
        self.angle = 0
        self.length = 0

    def draw_player(self, painter, rect):
        # Draw the player
        painter.drawRect(QtCore.QRect(QtCore.QPoint(rect.topLeft().x() * self.x_stretch,
                                                    rect.topLeft().y() * self.y_stretch),
                                      QtCore.QPoint(rect.bottomRight().x() * self.x_stretch,
                                                    rect.bottomRight().y() * self.y_stretch)))
    
    def draw_obstacles(self, painter, obst_rect_list):
        # Draw all obstacles
        for polygon in obst_rect_list:
            plist = []
            for point in polygon:
                plist.append(QtCore.QPoint(point.x() * self.x_stretch, point.y() * self.y_stretch))
            painter.drawPolygon(QtGui.QPolygon(plist))
        
    def draw_shot(self, painter, shot_line_list):
        
        for line in shot_line_list:
            painter.drawLine(QtCore.QLine(QtCore.QPoint(line.p1().x() * self.x_stretch,
                                                        line.p1().y() * self.y_stretch),
                                          QtCore.QPoint(line.p2().x() * self.x_stretch,
                                                        line.p2().y() * self.y_stretch)))
        
    def draw_indi_line(self, painter):
        
        line = QtCore.QLineF(QtCore.QPoint(main_UI.game.player.center().x() * self.x_stretch,
                                           main_UI.game.player.center().y() * self.y_stretch),
                             main_UI.game.player.center() + QtCore.QPoint(1, 0))

        line.setLength(main_UI.game.player.indi_line_length)
        line.setAngle(main_UI.game.player.angle)
        
        painter.drawLine(line)
    
    def keyPressEvent(self, event):
        
        # Append the pressed key to key_list 
        # It contains every currently pressed key
        key = event.key()
        self.key_list.append(key)
    
    def keyReleaseEvent(self, event):
        
        # Remove the pressed key from key_list 
        # It contains every currently pressed key
        key = event.key()
        self.key_list.remove(key)
        
    def timerEvent(self, event):
        if event.timerId() == self.game_cycle_timer.timerId():
            # The game_cycle_timer fired the event
            
            # Check for key presses and save next move in next_move_dir
            # Reset next_move_dir
            main_UI.game.player.next_move_dir = QtCore.QPoint(0, 0)
            
            for a in range(len(self.key_list)):
                key = self.key_list[a]
                if key == QtCore.Qt.Key_Left:
                    # the Left key is pressed
                    main_UI.game.player.next_move_dir.setX(main_UI.game.player.next_move_dir.x() - 1)
                elif key == QtCore.Qt.Key_Right:
                    # the Right key is pressed
                    main_UI.game.player.next_move_dir.setX(main_UI.game.player.next_move_dir.x() + 1)
                elif key == QtCore.Qt.Key_Up:
                    # the Up key is pressed
                    main_UI.game.player.next_move_dir.setY(main_UI.game.player.next_move_dir.y() - 1)
                elif key == QtCore.Qt.Key_Down:
                    # the Down key is pressed
                    main_UI.game.player.next_move_dir.setY(main_UI.game.player.next_move_dir.y() + 1)
                elif key == QtCore.Qt.Key_Q:
                    # Change player angle to turn left
                    main_UI.game.player.angle += main_UI.game.player.turn_speed
                    # If angle gets larger than 360, 
                    if main_UI.game.player.angle >= 360:
                        main_UI.game.player.angle -= 360
                elif key == QtCore.Qt.Key_E:
                    # Change player angle to turn right
                    main_UI.game.player.angle -= main_UI.game.player.turn_speed
                    # If angle gets less than 0, turn it to fit into 0 - 360 again
                    if main_UI.game.player.angle < 0:
                        main_UI.game.player.angle += 360
                elif key == QtCore.Qt.Key_Space:
                    # Shoot
                    memory = QtCore.QLineF(main_UI.game.player.pos, main_UI.game.player.pos + QtCore.QPoint(1, 0))
                    memory.setAngle(main_UI.game.player.angle)
                    memory.setLength(main_UI.game.player.shot.max_length)
                    main_UI.game.player.shot.try_shot(main_UI.game.player.center(), memory.p2())
                elif key == QtCore.Qt.Key_X:
                    print(str(main_UI.game.map.view_size))

                    main_UI.game.map.change_view_size(main_UI.game.map.view_size.width() + 1,
                                                      main_UI.game.map.view_size.height() + 1)

            # The next move is the player position + next_move_dir
            # to amplify move Speed, the next_move_dir is multiplied with self.move_speed
            if main_UI.game.player.next_move_dir.x() != 0 or main_UI.game.player.next_move_dir.y() != 0:
                main_UI.game.player.try_move(main_UI.game.player.pos, main_UI.game.player.next_move_dir,
                                             main_UI.game.player.move_speed)
            
            # do all logic here in the future
            
            # Update the scene AFTER all logic work
            self.update()
            
    def change_stretch(self):
        
        self.x_stretch = self.width() / float(main_UI.game.map.view_size.width())
        self.y_stretch = self.height() / float(main_UI.game.map.view_size.height())
        
    def paintEvent(self, event):
        # Initialize painter
        painter = QtGui.QPainter()       
        painter.begin(self) 
        # Basic painter setup
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Player gets drawn
        self.draw_player(painter, QtCore.QRect(main_UI.game.player.pos, main_UI.game.player.size))
        
        # Obstacles get drawn
        self.draw_obstacles(painter, main_UI.game.map.obstacle_list)
        
        # Shot computation
        if main_UI.game.player.shot.timer.isActive():
            # A Shot is currently up to draw
            # Compute its shortest distance before it hits an obstacle
            
            # Get the length the shot should have
            self.length = main_UI.game.player.shot.max_length
            self.shot_start_pos = main_UI.game.player.shot.start_pos
            self.shot_end_pos = main_UI.game.player.shot.end_pos
            self.angle = QtCore.QLineF(self.shot_start_pos, self.shot_end_pos).angle()
            self.shot_line_list = []

            # Iterate through the loop until the remaining length = 0
            # It then executes the else statement
            while self.length > 0.0:
                self.shot_end_pos, self.angle, self.length = main_UI.game.player.shot.compute_shot(self.shot_start_pos,
                                                                                                   self.angle,
                                                                                                   self.length)
                self.shot_line_list.append(QtCore.QLineF(QtCore.QPointF(self.shot_start_pos), self.shot_end_pos))
                self.shot_start_pos = self.shot_end_pos
        
            self.draw_shot(painter, self.shot_line_list)

        # Draw angle indicator
        self.draw_indi_line(painter)
                
        # TEST
        self.drawFrame(painter)
              
        painter.end()


class Map():
    
    def __init__(self, load_type):
        
        # Contains every obstacle element that is present in the map
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlines_list = []

        # def load_from_test variable definition
        self.size = 0
        self.view_size = 0
        
        # Init the map and declare which map to use
        if load_type == 'debug':
            # Just load the debug map
            self.load_from_test()
        else:
            print('load_type not supported')
            
    def add_obstacle(self, point_list):
        
        # Create the obstacle
        obstacle = Obstacle(point_list)
        
        # Add the obstacle to the lists obstacle_list and outlines_list
        self.obstacle_list.append(obstacle.polygon)
        self.outlines_list.append(obstacle.outlines())
        
    def load_from_test(self):
        
        # This method loads up a debugging map which is declared in here
        self.size = QtCore.QSize(800, 600)
        self.view_size = QtCore.QSize(300, 300)
        self.add_obstacle([QtCore.QPoint(100, 100),
                          QtCore.QPoint(390, 100),
                          QtCore.QPoint(390, 290),
                          QtCore.QPoint(100, 290)])

        self.add_obstacle([QtCore.QPoint(500, 500),
                          QtCore.QPoint(690, 500),
                          QtCore.QPoint(790, 590),
                          QtCore.QPoint(500, 590)])
        
    def change_view_size(self, w, h):
        if w <= main_UI.game_window.width():
            self.view_size.setWidth(w)
        if h <= main_UI.game_window.height():
            self.view_size.setHeight(h)
            
        main_UI.game_window.change_stretch()


class Shot():
    
    def __init__(self):

        self.start_pos = QtCore.QPoint(0, 0)
        self.end_pos = QtCore.QPoint(0, 0)
        self.shot_up_time = 400  # ms how long the shot should be visible
        self.max_length = 1000

        # compute_shot variable definition
        self.obst_outlines_list = []
        self.intersection = 0
        self.max_line = 0

        # init a timer
        # A Timer to fade out the shot after a certain time is initiated
        self.timer = QtCore.QTimer()
        QtCore.QTimer.setInterval(self.timer, self.shot_up_time)
        QtCore.QTimer.setSingleShot(self.timer, True)
        self.timer.stop()
        
    def try_shot(self, s_point, e_point):
        # Try to set new shot
        # This is only possible if the old shot has faded away
        if not self.timer.isActive():
            self.start_pos = s_point
            self.end_pos = e_point
            # The fade out timer is started
            self.timer.start()
            
            # EARLY SOUNDS
            winsound.PlaySound(os.path.dirname(__file__) + '\data\shot' + str(random.randint(0, 1) + 1) + '.wav',
                               winsound.SND_ASYNC)
            
    def compute_shot(self, start_point,  angle, length):
        # Returns the end point of the shot
        # whether its the actual end or just a collision with an obstacle can be seen in var Length
        # if remaining Length is 0 after calling the method, its the actual endpoint of the line
        # if remaining Length is not 0, call the method again with the remaining length
        
        # The method also returns the outgoing angle of the line if it has hit an obstacle
        # Therefore it CHANGES var angle and var length

        # Create the ideal line
        self.max_line = QtCore.QLineF(start_point, start_point + QtCore.QPoint(1, 0))
        self.max_line.setLength(length)
        self.max_line.setAngle(angle)
        
        # Find the intersection between that line and all obstacle outlines
        self.obst_outlines_list = main_UI.game.map.outlines_list
        self.intersection = QtCore.QPointF()
        
        # Iterate trough all outlines
        for a in range(len(self.obst_outlines_list)):
            for b in range(len(self.obst_outlines_list[a])):
                if self.max_line.intersect(self.obst_outlines_list[a][b], self.intersection) == 1:
                    # Intersection of both lines in self.intersection
                    self.max_line = QtCore.QLineF(start_point, self.intersection)
                    print('intersection')
                    # Compute the outgoing angle of the shot
                    # It is done here, because I need the obstacle outline to compute it
                    angle = self.max_line.angleTo(self.obst_outlines_list[a][b]) + self.obst_outlines_list[a][b].angle()
                else:
                    print('No intersection')
                    
        # max_line is now as short as possible
        
        # Return the remaining length
        length -= round(self.max_line.length())

        # Get angle inside 0 - 360
        if angle >= 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        
        # Set Length of max_line
        # If not done, the start point of the next line would instantly intersect the same outline again
        # Resulting in an infinite loop
        self.max_line.setLength(self.max_line.length() - 1)
        
        return self.max_line.p2(), angle, length


class Obj():

    def __init__(self):
        self.pos = None
        self.size = None
        self.polygon = None

    def center(self):
        return QtCore.QRect(self.pos, self.size).center()
    
    def outlines(self):
        
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
    def __init__(self, point_list):
        Obj.__init__(self)
        self.polygon = QtGui.QPolygon(point_list)


class Player(Obj):
    
    def __init__(self, x, y, w, h):
        Obj.__init__(self)
        self.pos = QtCore.QPoint(x, y)
        self.size = QtCore.QSize(w, h)
        self.shot = Shot()
        self.turn_speed = 2
        self.angle = 0
        self.indi_line_length = 30
        self.move_speed = 5
        self.next_move_dir = QtCore.QPoint(0, 0)
        
    def try_move(self, pos, move_dir, ms):
        # Generate the new positions
        # Go through every possible new position in the direction (dir)
        # Start with full move speed (ms) and if it does not work, try the next lower step
        # Break out of the loop if next move is possible
            
        for a in range(ms, 1, -1):
            new_rect = QtCore.QRect(QtCore.QPoint(pos.x() + move_dir.x() * a, pos.y() + move_dir.y() * a), self.size)
            # Check if new positions are in bounds of the window
            if new_rect.topLeft().x() >= 0 and new_rect.topLeft().y() >= 0 and \
                    new_rect.bottomRight().x() <= main_UI.game.map.view_size.width() and \
                    new_rect.bottomRight().y() <= main_UI.game.map.view_size.height():
                # Positions are inside the window
                # Check if player comes into contact with an obstacle
                # Check if uL or bR of the player are contained by an obstacle
                
                # Iterate through the list of obstacles
                for a in range(len(main_UI.game.map.obstacle_list)):
                    if main_UI.game.map.obstacle_list[a].containsPoint(new_rect.topLeft(),
                                                                       QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            main_UI.game.map.obstacle_list[a].containsPoint(new_rect.topRight(),
                                                                            QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            main_UI.game.map.obstacle_list[a].containsPoint(new_rect.bottomRight(),
                                                                            QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            main_UI.game.map.obstacle_list[a].containsPoint(new_rect.bottomLeft(),
                                                                            QtCore.Qt.OddEvenFill) % 2 == 1:
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
                    self.force_move(new_rect.topLeft())
                    return True
            else:
                # Positions are outside the window
                pass
            continue
        else:
            # Not even the smallest possible step (1) was possible
            return False
    
    def force_move(self, point):
        # Force a move command
        # Don't use! Use try_move() instead.
        self.pos = point
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_UI = Window()
    sys.exit(app.exec_())