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
            'border_pen_color': QtCore.Qt.red,
            'powerup_brush': QtCore.Qt.SolidPattern,
            'powerup_pen': QtCore.Qt.DotLine,
            'powerup_pen_color': QtCore.Qt.black}

player_defaults = {'move_speed': 2,
                   'turn_speed': 3,
                   'size': QtCore.QSize(10, 10),
                   'powerup_duration': 2000,
                   'shot_length': 1000}

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


class Window(QtGui.QMainWindow):
    def __init__(self):
        # Initialize the window
        super(Window, self).__init__()

        self.graphics = 'high'

        # Create a canvas for the game to run inside
        self.game_canvas = GameCanvas(self, self.graphics)
        self.game_canvas.setFrameStyle(QtGui.QFrame.Box)
        self.game_canvas.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Show the Window
        self.showFullScreen()
        # Set the game Canvas to be as big as possible
        self.game_canvas.setFixedSize(self.height(), self.height())

        self.setCentralWidget(self.game_canvas)

        self.setWindowTitle('Shooter')


class GameCanvas(QtGui.QFrame):
    def __init__(self, parent, graphics):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        # Create a game instance
        self.game = Game(player_defaults, player_key_setup, debug_key_setup, file_locations)

        # Var definition
        self.key_list = []
        self.graphics = graphics

        self.game.game_cycle_timer = QtCore.QBasicTimer()
        self.game.game_cycle_timer.start(self.game.game_cycle_interval, self)

    def heightForWidth(self, w):
        return w

    def timerEvent(self, event):
        if event.timerId() == self.game.game_cycle_timer.timerId():
            # The game_cycle_timer fired the event

            # Handle key presses
            for key in self.key_list:
                self.game.handle_key(key)

            # Handle collision of player with a shot
            for player in self.game.players:
                # Check if the player is vulnerable
                if not player.invulnerability_timer.isActive():
                    # Generate a list of all players except for the current one
                    remaining_players = copy.copy(self.game.players)
                    remaining_players.remove(player)

                    # Check if one of the shots of all those players hits the current player
                    for shooter in remaining_players:
                        if self.game.get_shot_intersection_with_player(player, shooter):
                            self.game.hit_action(player, shooter)

            self.update()

    def paintEvent(self, event):
        """Reimplementation of the paint Event"""
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.drawFrame(painter)

        # Painter transformation setup
        scaling = ((self.width() / float(self.game.get_viewable_map_area_size().width()),
                    self.height() / float(self.game.get_viewable_map_area_size().height())))
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