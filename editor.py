from PyQt4 import QtCore, QtGui, uic
import ConfigParser
import sys
import os
from map import Map
from game_painter import Paint

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


class Window(QtGui.QMainWindow):
    def __init__(self):
        # Initialize the window
        super(Window, self).__init__()

        self.ui = uic.loadUi(os.path.dirname(__file__) + file_locations['ui'] + 'editor.ui')

        # Create a canvas for the game to run inside
        self.map_canvas = MapCanvas(self)
        self.map_canvas.setFrameStyle(QtGui.QFrame.Box)

        # Set the game Canvas to be as big as possible
        self.map_canvas.setFixedSize(800, 800)

        self.ui.setCentralWidget(self.map_canvas)

        self.ui.setWindowTitle('Level Editor')
        self.ui.show()


class MapCanvas(QtGui.QFrame):
    def __init__(self, parent):
        # Initialize the UI element
        QtGui.QFrame.__init__(self, parent)

        self.map = Map(file_locations)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.drawFrame(painter)

        # Draw a frame of the game
        self.draw_game(painter)

        painter.end()

    def draw_game(self, painter):
        # Draw map backgrounds
        for background in self.map.background_list:
            background.draw(painter)

        # Draw obstacles
        for obj in self.map.obstacle_list:
            obj.draw(painter)

        # Draw powerups
        for obj in self.map.powerup_list:
            obj.draw(painter)


def center(widget_frame, target_frame):
    widget_frame.moveCenter(target_frame.center())
    return widget_frame.topLeft()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_UI = Window()
    sys.exit(app.exec_())