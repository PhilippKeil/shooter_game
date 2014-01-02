import sys
import copy
import ConfigParser
from PyQt4 import QtGui
from PyQt4 import QtCore

from main import Game

config_file = 'config.cfg'

config = ConfigParser.RawConfigParser()
config.read(config_file)
file_locations = {'textures': config.get('locations', 'textures'),
                  'sounds': config.get('locations', 'sounds'),
                  'levels': config.get('locations', 'levels')}

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
            'border_brush': QtCore.Qt.NoBrush,
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

        self.fullscreen = False
        self.graphics = 'low'

        # Create a canvas for the game to run inside
        self.game_frame = GameFrame(self, self.graphics)
        self.game_frame.setFixedSize(550, 510)

        # Layout management
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()

        hbox.addWidget(self.game_frame)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setWindowTitle('Shooter')
        self.show()


class GameFrame(QtGui.QFrame):
    def __init__(self, parent, graphics):
        QtGui.QFrame.__init__(self, parent)

        self.game_canvas = GameCanvas(self, graphics)
        self.game_canvas.setFixedSize(500, 500)

        self.game_canvas.setFrameStyle(QtGui.QFrame.Box)
        self.game_canvas.setFocusPolicy(QtCore.Qt.StrongFocus)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game_canvas)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)


class GameCanvas(QtGui.QFrame):
    def __init__(self, parent, graphics):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        # Create a game instance
        self.game = Game(player_key_setup, debug_key_setup, file_locations)

        # Var definition
        self.key_list = []
        self.graphics = graphics

    def paintEvent(self, event):
        """Reimplementation of the paint Event"""
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.drawFrame(painter)

        # Painter transformation setup
        scaling = ((self.width() / float(self.game.get_viewable_map_area_size().width()),
                    self.width() / float(self.game.get_viewable_map_area_size().height())))
        translate = self.game.get_viewable_map_area_pos()
        transform = QtGui.QTransform()
        transform.scale(scaling[0], scaling[1])
        transform.translate(-translate.x(), -translate.y())
        painter.setTransform(transform)

        # Draw a frame of the game
        self.game.draw_game(painter, self.graphics, defaults, file_locations)

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