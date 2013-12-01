import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QPoint as Qp
from PyQt4.QtCore import QPointF as Qpf
from PyQt4.QtCore import QRect as Qr
from PyQt4.QtCore import QLine as Ql
from PyQt4.QtCore import QLineF as Qlf
from PyQt4.QtCore import QSize as Qs

from main import Game

defaults = {'obstacle_brush': QtCore.Qt.SolidPattern,
            'obstacle_brush_color': QtCore.Qt.black,
            'obstacle_pen': QtCore.Qt.SolidLine,
            'obstacle_pen_color': QtCore.Qt.black,
            'player_brush': QtCore.Qt.Dense5Pattern,
            'player_brush_color': QtCore.Qt.red,
            'player_pen': QtCore.Qt.SolidLine,
            'player_pen_color': QtCore.Qt.red,
            'shot_pen': QtCore.Qt.DotLine,
            'shot_pen_color': QtCore.Qt.red}


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

        # Var definition
        self.key_list = []

        self.game_cycle_timer = QtCore.QBasicTimer()
        self.game_cycle_timer.start(Game.gameCycleInterval, self)

    def draw_player(self, painter, player, default_values):
        """Draws the player"""
        rect = Qr(player.pos, player.size)

        brush = QtGui.QBrush()
        pen = QtGui.QPen()

        if 'brush' in player.information:
            brush.setStyle(player.information['brush'])
        else:
            brush.setStyle(default_values['player_brush'])

        if 'brush_color' in player.information:
            brush.setColor(player.information['brush_color'])
        else:
            brush.setColor(default_values['brush_color'])

        if 'pen' in player.information:
            pen.setStyle(player.information['pen'])
        else:
            pen.setStyle(default_values['player_pen'])

        if 'pen_color' in player.information:
            pen.setColor(player.information['pen_color'])
        else:
            pen.setColor(default_values['player_pen_color'])

        if 'texture' in player.information:
                texture = QtGui.QPixmap()
                texture.load(player.information['texture'])
                brush.setTexture(texture)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawRect(Qr(Qp(rect.topLeft().x() * self.x_stretch,
                               rect.topLeft().y() * self.y_stretch),
                            Qp(rect.bottomRight().x() * self.x_stretch,
                               rect.bottomRight().y() * self.y_stretch)))

    def draw_obstacles(self, painter, obstacle_list, default_values):
        """Draws obstacles"""

        for polygon in obstacle_list:
            point_list = []

            brush = QtGui.QBrush()
            pen = QtGui.QPen()

            if 'brush' in polygon.information:
                brush.setStyle(polygon.information['brush'])
            else:
                brush.setStyle(default_values['obstacle_brush'])

            if 'brush_color' in polygon.information:
                brush.setColor(polygon.information['brush_color'])
            else:
                brush.setColor(default_values['obstacle_brush_color'])

            if 'pen' in polygon.information:
                pen.setStyle(polygon.information['pen'])
            else:
                pen.setStyle(default_values['obstacle_pen'])

            if 'pen_color' in polygon.information:
                pen.setColor(polygon.information['pen_color'])
            else:
                pen.setColor(default_values['obstacle_pen_color'])

            if 'texture' in polygon.information:
                texture = QtGui.QPixmap()
                texture.load(polygon.information['texture'])
                brush.setTexture(texture)

            painter.setBrush(brush)
            painter.setPen(pen)

            for point in polygon.polygon:
                point_list.append(Qp(point.x() * self.x_stretch, point.y() * self.y_stretch))
            painter.drawPolygon(QtGui.QPolygon(point_list))

    def draw_shot(self, painter, player, default_values):
        """Draws shot of the player"""

        pen = QtGui.QPen()

        if 'shot_pen' in player.information:
            pen.setStyle(player.information['shot_pen'])
        else:
            pen.setStyle(default_values['shot_pen'])

        if 'shot_pen_color' in player.information:
            pen.setColor(player.information['shot_pen_color'])
        else:
            pen.setColor(default_values['shot_pen_color'])

        painter.setPen(pen)

        shot_line_list = self.game.get_shot(player)
        if not shot_line_list:
            return

        for line in shot_line_list:
            painter.drawLine(Ql(Qp(line.p1().x() * self.x_stretch,
                                   line.p1().y() * self.y_stretch),
                                Qp(line.p2().x() * self.x_stretch,
                                   line.p2().y() * self.y_stretch)))

    def draw_direction_indicator_line(self, painter, player, default_values):
        pen = QtGui.QPen()

        if 'shot_pen' in player.information:
            pen.setStyle(player.information['shot_pen'])
        else:
            pen.setStyle(default_values['shot_pen'])

        if 'shot_pen_color' in player.information:
            pen.setColor(player.information['shot_pen_color'])
        else:
            pen.setColor(default_values['shot_pen_color'])

        painter.setPen(pen)

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

        self.draw_player(painter, self.game.player_1, defaults)
        self.draw_shot(painter, self.game.player_1, defaults)

        self.draw_obstacles(painter, self.game.get_obstacle_list(), defaults)

        # Draw angle indicator
        self.draw_direction_indicator_line(painter, self.game.player_1, defaults)

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