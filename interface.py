import sys
import os
import copy
import ConfigParser
import glob
from PyQt4 import QtGui, QtCore, uic

from main import Game

config_file = 'config.cfg'

config = ConfigParser.RawConfigParser()
config.read(config_file)
file_locations = {'textures': config.get('locations', 'textures'),
                  'sounds': config.get('locations', 'sounds'),
                  'levels': config.get('locations', 'levels'),
                  'ui': config.get('locations', 'ui')}

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

powerup_colors = {'turn_faster': QtCore.Qt.red,
                  'move_faster': QtCore.Qt.green,
                  'shot_longer': QtCore.Qt.blue}

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

        self.main_frame = uic.loadUi(os.path.dirname(__file__) + file_locations['ui'] + 'main_menu.ui')
        self.settings_frame = uic.loadUi(os.path.dirname(__file__) + file_locations['ui'] + 'settings_menu.ui')
        self.pre_game_frame = uic.loadUi(os.path.dirname(__file__) + file_locations['ui'] + 'pre_game_menu.ui')

        self.widget_stack = QtGui.QStackedWidget()
        self.widget_stack.addWidget(self.main_frame)      # 0
        self.widget_stack.addWidget(self.settings_frame)  # 1
        self.widget_stack.addWidget(self.pre_game_frame)  # 2

        self.main_frame.play_button.clicked.connect(lambda: self.widget_stack.setCurrentIndex(2))
        self.main_frame.settings_menu_button.clicked.connect(lambda: self.widget_stack.setCurrentIndex(1))
        self.settings_frame.back_button.clicked.connect(lambda: self.widget_stack.setCurrentIndex(0))

        self.pre_game_frame.back_button.clicked.connect(lambda: self.widget_stack.setCurrentIndex(0))
        self.pre_game_frame.add_player_button.clicked.connect(self.add_player)
        self.pre_game_frame.remove_player_button.clicked.connect(self.remove_player)
        self.pre_game_frame.update_level_list_button.clicked.connect(self.populate_level_list)
        self.pre_game_frame.play_button.clicked.connect(self.init_game)

        self.setCentralWidget(self.widget_stack)

        self.setWindowTitle('SHOOTER')
        self.show()

    def add_player(self):
        highest_player_id = self.pre_game_frame.player_tabs.count()
        new_player_id = highest_player_id + 1
        self.pre_game_frame.player_tabs.addTab(PlayerTab(new_player_id), 'PLAYER %s' % str(new_player_id))

    def remove_player(self):
        self.pre_game_frame.player_tabs.removeTab(self.pre_game_frame.player_tabs.count() - 1)

    def populate_level_list(self):
        self.pre_game_frame.level_list.clear()
        for fl in glob.glob(os.path.dirname(__file__) + file_locations['levels'] + '*.map'):
            self.pre_game_frame.level_list.addItem(fl.replace('\\', '/'))

    def init_game(self):
        selected_level = str(self.pre_game_frame.level_list.currentItem().text()).split('/')
        player_count = self.pre_game_frame.player_tabs.count()
        print('lvl: %s ; players: %s' % (selected_level, str(player_count)))
        stripped_level = selected_level[len(selected_level) - 1]
        print('stripped level: %s' % stripped_level)

        self.widget_stack.addWidget(GameCanvas(self, stripped_level))
        self.widget_stack.setCurrentIndex(3)


class PlayerTab(QtGui.QWidget):
    def __init__(self, player_id):
        QtGui.QWidget.__init__(self)

        self.player_label = QtGui.QLabel('PLAYER %s' % str(player_id))
        self.key_list_widget = QtGui.QListWidget()

        self.populate_key_list_view(player_id)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.player_label)
        vbox.addWidget(self.key_list_widget)

        self.setLayout(vbox)

    def populate_key_list_view(self, player_id):
        curr_key_dict = player_key_setup[player_id - 1]
        for key in curr_key_dict:
            self.key_list_widget.addItem('%s : %s' % (key, str(curr_key_dict[key])))


class GameCanvas(QtGui.QFrame):
    def __init__(self, parent, selected_level):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        self.setFixedSize(500, 500)

        # Create a game instance
        self.game = Game(selected_level, player_defaults, player_key_setup, debug_key_setup, file_locations)

        # Var definition
        self.key_list = []
        self.graphics = 'low'

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

            # Handle creation of a powerup
            self.game.try_create_powerup()

            # Handle removal of eventual powerups from players
            for player in self.game.players:
                player.try_remove_powerup()

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
        self.game.draw_game(painter, self.graphics, defaults, powerup_colors, file_locations)

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