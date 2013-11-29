import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore

from main import Game

# If the system is Windows, import winsound lib to do the audio
if sys.platform == 'win32':
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

        # Create a canvas for the game to run inside
        self.game_window = GameWindow(self)

        # Layout management
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game_window)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setWindowTitle('Shooter')
        self.show()


class GameWindow(QtGui.QFrame):
    def __init__(self, parent):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFixedSize(800, 600)
        self.setFrameStyle(QtGui.QFrame.Box)

        # Create a game instance
        self.game = Game()

        self.x_stretch = self.width() / float(self.game.get_viewable_map_area().width())
        self.y_stretch = self.height() / float(self.game.get_viewable_map_area().height())

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

    def draw_player(self, painter, player):
        """Draws the player"""
        rect = QtCore.QRect(player.pos, player.size)

        painter.drawRect(QtCore.QRect(QtCore.QPoint(rect.topLeft().x() * self.x_stretch,
                                                    rect.topLeft().y() * self.y_stretch),
                                      QtCore.QPoint(rect.bottomRight().x() * self.x_stretch,
                                                    rect.bottomRight().y() * self.y_stretch)))

    def draw_obstacles(self, painter, obstacle_list):
        """Draws obstacles"""
        for polygon in obstacle_list:
            point_list = []
            for point in polygon:
                point_list.append(QtCore.QPoint(point.x() * self.x_stretch, point.y() * self.y_stretch))
            painter.drawPolygon(QtGui.QPolygon(point_list))

    def draw_shot(self, painter, player):
        """Draws shot of the player"""

        shot_line_list = self.game.get_shot(player)
        if not shot_line_list:
            return

        for line in shot_line_list:
            painter.drawLine(QtCore.QLine(QtCore.QPoint(line.p1().x() * self.x_stretch,
                                                        line.p1().y() * self.y_stretch),
                                          QtCore.QPoint(line.p2().x() * self.x_stretch,
                                                        line.p2().y() * self.y_stretch)))

    def draw_direction_indicator_line(self, painter, player):

        player_rectangle = QtCore.QRect(self.game.get_player_pos(player), self.game.get_player_size(player))
        line = QtCore.QLineF(QtCore.QPointF(player_rectangle.center().x() * self.x_stretch,
                                            player_rectangle.center().y() * self.y_stretch),
                             QtCore.QPointF(player_rectangle.center() + QtCore.QPoint(1, 0)))

        line.setLength(self.game.get_player_direction_indicator_line_length(player))
        line.setAngle(self.game.get_player_angle(player))

        painter.drawLine(line)

    def timerEvent(self, event):
        if event.timerId() == self.game_cycle_timer.timerId():
            # The game_cycle_timer fired the event

            # Check for key presses and save next move in next_move_dir
            # Reset next_move_dir
            next_move_dir = QtCore.QPoint(0, 0)

            for a in range(len(self.key_list)):
                key = self.key_list[a]
                if key == QtCore.Qt.Key_Left:
                    # the Left key is pressed
                    next_move_dir.setX(next_move_dir.x() - 1)

                elif key == QtCore.Qt.Key_Right:
                    # the Right key is pressed
                    next_move_dir.setX(next_move_dir.x() + 1)

                elif key == QtCore.Qt.Key_Up:
                    # the Up key is pressed
                    next_move_dir.setY(next_move_dir.y() - 1)

                elif key == QtCore.Qt.Key_Down:
                    # the Down key is pressed
                    next_move_dir.setY(next_move_dir.y() + 1)

                elif key == QtCore.Qt.Key_Q:
                    # Change player angle to turn left
                    self.game.turn_player(self.game.player_1, 'left')
                elif key == QtCore.Qt.Key_E:
                    self.game.turn_player(self.game.player_1, 'right')

                elif key == QtCore.Qt.Key_Space:
                    # Shot
                    memory = QtCore.QLineF(self.game.player_1.pos, main_UI.game.player.pos + QtCore.QPoint(1, 0))
                    memory.setAngle(main_UI.game.player.angle)
                    memory.setLength(main_UI.game.player.shot.max_length)
                    self.game.try_shot(self.game.player_1, main_UI.game.player.center(), memory.p2())

                elif key == QtCore.Qt.Key_X:
                    # Zoom
                    self.game.change_viewable_map_area(self.game.get_viewable_map_area() + QtCore.QSize(1, 1),
                                                       self.size())

                    main_UI.game.map.change_view_size(main_UI.game.map.view_size.width() + 1,
                                                      main_UI.game.map.view_size.height() + 1)

            # The next move is the player position + next_move_dir
            # to amplify move Speed, the next_move_dir is multiplied with self.move_speed
            if next_move_dir.x() != 0 or next_move_dir.y() != 0:
                self.game.move_player(self.game.player_1, next_move_dir)

            # do all logic here in the future

            # Update the scene AFTER all logic work
            self.update()

    def change_stretch(self):

        self.x_stretch = self.width() / float(main_UI.game.map.view_size.width())
        self.y_stretch = self.height() / float(main_UI.game.map.view_size.height())

    def paintEvent(self, event):
        """Reimplementation of the paint Event"""
        # Initialize painter
        painter = QtGui.QPainter()
        painter.begin(self)

        # Basic painter setup
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self.draw_player(painter, self.game.player_1)
        self.draw_shot(painter, self.game.player_1)

        self.draw_obstacles(painter, self.game.get_obstacle_list())

        # Draw angle indicator
        self.draw_direction_indicator_line(painter, self.game.player_1)

        # TEST
        self.drawFrame(painter)

        painter.end()

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


def center(widget_frame, target_frame):
    widget_frame.moveCenter(target_frame.center())
    return widget_frame.topLeft()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_UI = Window()
    sys.exit(app.exec_())