import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QPoint as Qp
from PyQt4.QtCore import QPointF as Qpf
from PyQt4.QtCore import QRect as Qr
from PyQt4.QtCore import QLine as Ql
from PyQt4.QtCore import QLineF as Qlf

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
            'shot_pen_color': QtCore.Qt.red,
            'border_brush': QtCore.Qt.CrossPattern,
            'border_brush_color': QtCore.Qt.red,
            'border_pen': QtCore.Qt.SolidLine,
            'border_pen_color': QtCore.Qt.red}

player_key_setup = [{'move_up': QtCore.Qt.Key_W,
                     'move_down': QtCore.Qt.Key_S,
                     'move_left': QtCore.Qt.Key_A,
                     'move_right': QtCore.Qt.Key_D,
                     'turn_left': QtCore.Qt.Key_Q,
                     'turn_right': QtCore.Qt.Key_E,
                     'shoot': QtCore.Qt.Key_Space},

                    {'move_up': QtCore.Qt.Key_Up,
                     'move_down': QtCore.Qt.Key_Down,
                     'move_left': QtCore.Qt.Key_Left,
                     'move_right': QtCore.Qt.Key_Right,
                     'turn_left': QtCore.Qt.Key_B,
                     'turn_right': QtCore.Qt.Key_M,
                     'shoot': QtCore.Qt.Key_N},

                    {'move_up': QtCore.Qt.Key_T,
                     'move_down': QtCore.Qt.Key_G,
                     'move_left': QtCore.Qt.Key_F,
                     'move_right': QtCore.Qt.Key_H,
                     'turn_left': QtCore.Qt.Key_R,
                     'turn_right': QtCore.Qt.Key_Z,
                     'shoot': QtCore.Qt.Key_V}]

debug_key_setup = {'debug_zoom_out': QtCore.Qt.Key_O,
                   'debug_zoom_in': QtCore.Qt.Key_U,
                   'debug_area_move_up': QtCore.Qt.Key_I,
                   'debug_area_move_down': QtCore.Qt.Key_K,
                   'debug_area_move_left': QtCore.Qt.Key_J,
                   'debug_area_move_right': QtCore.Qt.Key_L}


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

        self.fullscreen = True

        if self.fullscreen:
            self.setGeometry(QtGui.QDesktopWidget.availableGeometry(QtGui.QApplication.desktop()))
            self.game_window.setFixedSize(self.height(), self.height())
            self.showFullScreen()
            print('starting in fullscreen')
        else:
            self.setGeometry(1, 1, 500, 500)
            self.move(center(self.frameGeometry(), QtGui.QDesktopWidget().frameGeometry()))
            self.game_window.setFixedSize(self.width(), self.height())
            self.show()


class GameWindow(QtGui.QFrame):
    def __init__(self, parent):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        # Create a game instance
        self.game = Game(player_key_setup, debug_key_setup)

        # Var definition
        self.key_list = []

        self.game_cycle_timer = QtCore.QBasicTimer()
        self.game_cycle_timer.start(Game.gameCycleInterval, self)

    @staticmethod
    def draw_player(painter, player, default_values):
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
                texture.load(os.path.dirname(__file__) + '/data/textures/' + player.information['texture'])
                brush.setTexture(texture)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawRect(Qr(Qp(rect.topLeft().x(),
                               rect.topLeft().y()),
                            Qp(rect.bottomRight().x(),
                               rect.bottomRight().y())))

    @staticmethod
    def draw_obstacles(painter, obstacle_list, default_values):
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
                texture.load(os.path.dirname(__file__) + '/data/textures/' + polygon.information['texture'])
                brush.setTexture(texture)

            painter.setBrush(brush)
            painter.setPen(pen)

            for point in polygon.polygon:
                point_list.append(Qp(point.x(), point.y()))
            painter.drawPolygon(QtGui.QPolygon(point_list))

    @staticmethod
    def draw_shot(painter, player, default_values, shot_line_list):
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

        if not shot_line_list:
            return

        for line in shot_line_list:
            painter.drawLine(Ql(Qp(line.p1().x(),
                                   line.p1().y()),
                                Qp(line.p2().x(),
                                   line.p2().y())))

    @staticmethod
    def draw_direction_indicator_line(painter,
                                      player,
                                      player_pos,
                                      player_size,
                                      player_turn_angle,
                                      player_direction_indicator_line_length,
                                      default_values):
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

        player_rectangle = Qr(player_pos, player_size)
        line = Qlf(Qpf(player_rectangle.center().x(),
                       player_rectangle.center().y()),
                   Qpf(player_rectangle.center() + Qp(1, 0)))

        line.setLength(player_direction_indicator_line_length)
        line.setAngle(player_turn_angle)

        painter.drawLine(line)

    @staticmethod
    def draw_map_borders(painter, view_position, view_size, map_size, default_values):
        brush = QtGui.QBrush()
        brush.setStyle(default_values['border_brush'])
        brush.setColor(default_values['border_brush_color'])
        painter.setBrush(brush)

        pen = QtGui.QPen()
        pen.setStyle(default_values['border_pen'])
        pen.setColor(default_values['border_pen_color'])
        painter.setPen(pen)

        if view_position.x() < 0:
            print('view leaves map in x (lower than 0)')
            painter.drawRect(view_position.x(), 0, abs(view_position.x()), map_size.height())

        if view_position.y() < 0:
            print('view leaves map in y (lower than 0)')
            painter.drawRect(0, view_position.y(), map_size.width(), abs(view_position.y()))

        if view_position.x() + view_size.width() > map_size.width():
            print('view leaves map in x (higher than map width)')
            painter.drawRect(map_size.width(), 0, map_size.width() + view_position.x(), map_size.height())

        if view_position.y() + view_size.height() > map_size.height():
            print('view leaves map in y (higher than map height)')
            painter.drawRect(0, map_size.height(), map_size.width(), view_position.y())

    @staticmethod
    def draw_background(painter, background, map_size):
        brush = QtGui.QBrush()
        brush.setTexture(background)

        painter.setBrush(brush)
        painter.drawRect(Qr(Qp(0, 0), map_size))

    def timerEvent(self, event):
        if event.timerId() == self.game_cycle_timer.timerId():
            # The game_cycle_timer fired the event
            for a in range(len(self.key_list)):
                key = self.key_list[a]
                self.game.handle_key(key)

            self.update()

    def paintEvent(self, event):
        """Reimplementation of the paint Event"""
        painter = QtGui.QPainter()

        painter.begin(self)

        # Painter setup
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw a border around the game frame
        self.drawFrame(painter)

        # Painter transformation setup
        scaling = ((self.width() / float(self.game.get_viewable_map_area_size().width()),
                    self.width() / float(self.game.get_viewable_map_area_size().height())))
        translate = self.game.get_viewable_map_area_pos()
        transform = QtGui.QTransform()
        transform.scale(scaling[0], scaling[1])
        transform.translate(-translate.x(), -translate.y())
        painter.setTransform(transform)

        self.draw_background(painter, self.game.get_map_background(), self.game.get_map_size())
        self.draw_map_borders(painter,
                              self.game.get_viewable_map_area_pos(),
                              self.game.get_viewable_map_area_size(),
                              self.game.get_map_size(),
                              defaults)
        self.draw_obstacles(painter, self.game.get_obstacle_list(), defaults)

        for player in self.game.players:
            self.draw_player(painter, player, defaults)
            self.draw_direction_indicator_line(painter,
                                               player,
                                               self.game.get_player_pos(player),
                                               self.game.get_player_size(player),
                                               self.game.get_player_angle(player),
                                               self.game.get_player_direction_indicator_line_length(player),
                                               defaults)
            self.draw_shot(painter, player, defaults, self.game.get_shot(player))

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