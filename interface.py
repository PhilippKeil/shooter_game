import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QPoint as Qp
from PyQt4.QtCore import QPointF as Qpf
from PyQt4.QtCore import QRect as Qr
from PyQt4.QtCore import QLine as Ql
from PyQt4.QtCore import QLineF as Qlf
from PyQt4.QtCore import QSize as Qs

from main import Game


class Window(QtGui.QWidget):
    def __init__(self):
        # Initialize the window
        super(Window, self).__init__()

        # Create a canvas for the game to run inside
        self.game_window = GameWindow(self)
        self.game_window.setFrameStyle(QtGui.QFrame.Box)
        self.game_window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Layout management
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game_window)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setWindowTitle('Shooter')

        self.fullscreen = False

        if self.fullscreen:
            self.setGeometry(QtGui.QDesktopWidget.availableGeometry(QtGui.QApplication.desktop()))
            self.game_window.setFixedSize(self.height(), self.height())
            self.game_window.change_stretch()
            self.showFullScreen()
            print('starting in fullscreen')
        else:
            self.setGeometry(1, 1, 500, 500)
            self.move(center(self.frameGeometry(), QtGui.QDesktopWidget().frameGeometry()))
            self.game_window.setFixedSize(self.width(), self.height())
            self.game_window.change_stretch()
            self.show()


class GameWindow(QtGui.QFrame):
    def __init__(self, parent):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        # Create a game instance
        self.game = Game()

        # Painter setup
        self.texture_list = ['wood_texture.bmp', 'player_texture.bmp']
        self.textures = []
        for texture in self.texture_list:
            self.textures.append(QtGui.QPixmap())
            if self.textures[len(self.textures) - 1].load(texture):
                print('loaded ' + texture)
            else:
                print('Failed to load ' + texture)

        self.obstacle_pen = QtGui.QPen()
        self.obstacle_pen.setStyle(QtCore.Qt.SolidLine)
        self.obstacle_pen.setWidth(0)

        self.obstacle_brush = QtGui.QBrush()
        self.obstacle_brush.setTexture(self.textures[0])
        self.obstacle_brush.setStyle(QtCore.Qt.TexturePattern)

        self.player_pen = QtGui.QPen()
        self.player_pen.setStyle(QtCore.Qt.SolidLine)
        self.player_pen.setWidth(0)

        self.player_brush = QtGui.QBrush()
        self.player_brush.setTexture(self.textures[1])
        self.player_brush.setStyle(QtCore.Qt.TexturePattern)

        self.shot_pen = QtGui.QPen()
        self.shot_pen.setStyle(QtCore.Qt.DashLine)
        self.shot_pen.setColor(QtCore.Qt.blue)

        # End of painter setup

        # Var definition
        self.key_list = []

        self.game_cycle_timer = QtCore.QBasicTimer()
        self.game_cycle_timer.start(Game.gameCycleInterval, self)

    def draw_player(self, painter, player):
        """Draws the player"""
        rect = Qr(player.pos, player.size)
        painter.setBrush(self.player_brush)
        painter.setPen(self.player_pen)

        painter.drawRect(Qr(Qp(rect.topLeft().x() * self.x_stretch,
                               rect.topLeft().y() * self.y_stretch),
                            Qp(rect.bottomRight().x() * self.x_stretch,
                               rect.bottomRight().y() * self.y_stretch)))

    def draw_obstacles(self, painter, obstacle_list):
        """Draws obstacles"""
        painter.setBrush(self.obstacle_brush)
        painter.setPen(self.obstacle_pen)

        for polygon in obstacle_list:
            point_list = []
            for point in polygon:
                point_list.append(Qp(point.x() * self.x_stretch, point.y() * self.y_stretch))
            painter.drawPolygon(QtGui.QPolygon(point_list))

    def draw_shot(self, painter, player):
        """Draws shot of the player"""
        painter.setPen(self.shot_pen)

        shot_line_list = self.game.get_shot(player)
        if not shot_line_list:
            return

        for line in shot_line_list:
            painter.drawLine(Ql(Qp(line.p1().x() * self.x_stretch,
                                   line.p1().y() * self.y_stretch),
                                Qp(line.p2().x() * self.x_stretch,
                                   line.p2().y() * self.y_stretch)))

    def draw_direction_indicator_line(self, painter, player):
        painter.setPen(self.shot_pen)

        player_rectangle = Qr(self.game.get_player_pos(player), self.game.get_player_size(player))
        line = Qlf(Qpf(player_rectangle.center().x() * self.x_stretch,
                       player_rectangle.center().y() * self.y_stretch),
                   Qpf(player_rectangle.center() + Qp(1, 0)))

        line.setLength(self.game.get_player_direction_indicator_line_length(player))
        line.setAngle(self.game.get_player_angle(player))

        painter.drawLine(line)

    def timerEvent(self, event):
        if event.timerId() == self.game_cycle_timer.timerId():
            # The game_cycle_timer fired the event

            # Check for key presses and save next move in next_move_dir
            # Reset next_move_dir
            next_move_dir = Qp(0, 0)

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
                    tmp_line = Qlf(Qpf(self.game.get_player_pos(self.game.player_1)),
                                   Qpf(self.game.get_player_pos(self.game.player_1) + Qp(1, 0)))

                    tmp_line.setAngle(self.game.get_player_angle(self.game.player_1))
                    tmp_line.setLength(self.game.get_shot_maximum_length(self.game.player_1))
                    self.game.try_shot(self.game.player_1,
                                       Qr(self.game.get_player_pos(self.game.player_1),
                                          self.game.get_player_size(self.game.player_1)).center(), tmp_line.p2())

                elif key == QtCore.Qt.Key_X:
                    # Zoom
                    self.game.change_viewable_map_area(self.game.get_viewable_map_area() + Qs(1, 1),
                                                       self.size())
                    self.change_stretch()

            # The next move is the player position + next_move_dir
            # to amplify move Speed, the next_move_dir is multiplied with self.move_speed
            if next_move_dir.x() != 0 or next_move_dir.y() != 0:
                self.game.move_player(self.game.player_1, next_move_dir)

            # do all logic here in the future

            # Update the scene AFTER all logic work
            self.update()

    def change_stretch(self):
        self.x_stretch = self.width() / float(self.game.get_viewable_map_area().width())
        self.y_stretch = self.height() / float(self.game.get_viewable_map_area().height())

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