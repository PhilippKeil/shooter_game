from PyQt4 import QtGui
from PyQt4 import QtCore

# New object structure:
#
# dict(type: either obstacle or player
#      type: player
#            position: QPoint()
#            size: QSize()
#      type: obstacle
#            position: [QPoint(), QPoint()]
#      all types:
#            brush: QBrush()
#            pen: QPen()
#            color: QColor()
#            texture: String of location
#
# New file structure:


class Map():
    def __init__(self, load_type):
        # Contains every obstacle element that is present in the map
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlines_list = []

        # Save player information after map has been loaded
        self.player_information = None

        # def load_from_test variable definition
        self.size = 0
        self.view_size = 0

        # Init the map and declare which map to use
        if load_type == 'debug':
            # Just load the debug map
            self.load_test()
        else:
            print('load_type not supported')

    def add_object(self, d):
        if d['type'] == 'player':
            # Save the player object in the map class, until it is needed for creation of a player class
            self.player_information = d
        elif d['type'] == 'obstacle':
            # Create an obstacle
            obstacle = Obstacle(d)
            # Add the obstacle to the lists obstacle_list and outlines_list
            self.obstacle_list.append(obstacle)
            self.outlines_list.append(obstacle.outlines())
        else:
            print('Could not create object. No type defined')

    def load_test(self):

        # This method loads up a test map
        self.size = QtCore.QSize(800, 600)
        self.view_size = QtCore.QSize(300, 300)

        self.add_object({'type': 'player',
                         'position': QtCore.QPoint(50, 50),
                         'size': QtCore.QSize(10, 10),
                         'turn_speed': 2,
                         'move_speed': 5,
                         'brush': QtCore.Qt.SolidPattern})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 0),
                                      QtCore.QPoint(100, 100),
                                      QtCore.QPoint(200, 100),
                                      QtCore.QPoint(200, 0)],
                         'color': QtCore.Qt.blue,
                         'brush': QtCore.Qt.TexturePattern,
                         'texture': 'wood_texture.bmp',
                         'pen': QtCore.Qt.DotLine})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 200),
                                      QtCore.QPoint(100, 400),
                                      QtCore.QPoint(400, 400),
                                      QtCore.QPoint(200, 200)],
                         'color': QtCore.Qt.red,
                         'brush': QtCore.Qt.Dense5Pattern,
                         'pen': QtCore.Qt.SolidLine})

    def change_view_size(self, width, height, frame_size):
        if width <= frame_size.width():
            self.view_size.setWidth(width)
        if height <= frame_size.height():
            self.view_size.setHeight(height)

    def get_player_information(self):
        return self.player_information


class Obj():
    def __init__(self):
        self.pos = None
        self.size = None
        self.polygon = None

    def center(self):
        return QtCore.QRect(self.pos, self.size).center()


class Obstacle():
    def __init__(self, d):
        if 'position' in d:
            self.polygon = QtGui.QPolygon(d['position'])
        else:
            print('No position parameter given')

        if 'color' in d:
            self.color = d['color']
        else:
            print('No color parameter given')

        if 'brush' in d:
            self.brush = d['brush']
        else:
            print('No brush parameter given')

        if 'pen' in d:
            self.pen = d['pen']
        else:
            print('no pen parameter given')

        if 'texture' in d:
            self.texture = d['texture']
        else:
            print('No texture parameter given')

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
            result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[a-1]), QtCore.QPointF(self.polygon[a])))
            # append the last line from the last index to
        result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[len(self.polygon) - 1]), QtCore.QPointF(self.polygon[0])))
        return result

