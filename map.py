from PyQt4 import QtGui
from PyQt4 import QtCore

# Object parameters:
# type: String (either 'player' or 'obstacle' atm)
# brush: QBrush (see texture)
# brush_color: QColor
# texture: String (location) (overrides brush setting. Best use only texture OR brush for one object)
# pen: QPen
# pen_color: QColor
#
# type 'player' exclusive:
#   position: QPoint
#   size: QSize
#   move_speed: Integer
#   turn_speed: Integer
#
# type 'obstacle' exclusives:
#   position: [QPoint, QPoint, ...]


# from flatuicolors.com
colors = {'Turquoise': QtGui.QColor().fromRgb(26, 188, 156),
          'Emerald': QtGui.QColor().fromRgb(46, 204, 113),
          'Peter River': QtGui.QColor().fromRgb(52, 152, 219),
          'Amethyst': QtGui.QColor().fromRgb(155, 89, 182),
          'Wet Asphalt': QtGui.QColor().fromRgb(52, 73, 94),
          'Green Sea': QtGui.QColor().fromRgb(22, 160, 133),
          'Nephritis': QtGui.QColor().fromRgb(39, 174, 96),
          'Belize Hole': QtGui.QColor().fromRgb(41, 128, 185),
          'Wisteria': QtGui.QColor().fromRgb(142, 68, 173),
          'Midnight Blue': QtGui.QColor().fromRgb(44, 62, 80),
          'Sun Flower': QtGui.QColor().fromRgb(241, 196, 15),
          'Carrot': QtGui.QColor().fromRgb(230, 126, 34),
          'Alizarin': QtGui.QColor().fromRgb(231, 76, 60),
          'Clouds': QtGui.QColor().fromRgb(236, 240, 241),
          'Concrete': QtGui.QColor().fromRgb(149, 165, 166),
          'Orange': QtGui.QColor().fromRgb(243, 156, 18),
          'Pumpkin': QtGui.QColor().fromRgb(211, 84, 0),
          'Pomegranate': QtGui.QColor().fromRgb(192, 57, 43),
          'Silver': QtGui.QColor().fromRgb(189, 195, 199),
          'Asbestos': QtGui.QColor().fromRgb(127, 140, 141)}


class Map():
    def __init__(self, load_type):
        # Contains every obstacle element that is present in the map
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlines_list = []

        # Save player information after map has been loaded
        self.player_information = []

        self.size = None
        self.view_size = None
        self.view_position = QtCore.QPoint(0, 0)

        # Init the map and declare which map to use
        if load_type == 'debug':
            # Just load the debug map
            self.load_test()
        else:
            print('load_type not supported')

    def add_object(self, d):
        if d['type'] == 'player':
            # Save the player object in the map class, until it is needed for creation of a player class
            self.player_information.append(d)
        elif d['type'] == 'obstacle':
            # Create an obstacle
            try:
                obstacle = Obstacle(d)
            except ValueError as e:
                print('Could not create obstacle because ' + e.message)
            else:
                # Add the obstacle to the lists obstacle_list and outlines_list
                self.obstacle_list.append(obstacle)
                self.outlines_list.append(obstacle.outlines())
        else:
            print('Could not create object. No type defined')

    def load_test(self):

        # This method loads up a test map
        self.size = QtCore.QSize(520, 500)
        self.view_size = QtCore.QSize(300, 300)
        self.view_position = QtCore.QPoint(0, 0)

        # Template:
        """
        self.add_object({'type': '',
                         'position': QtCore.QPoint(),
                         'brush': QtCore.Qt.,
                         'brush_color': QtCore.Qt.,
                         'pen': QtCore.Qt.,
                         'pen_color': QtCore.Qt.,
                         'texture': ''})
        """

        self.add_object({'type': 'player',
                         'position': QtCore.QPoint(10, 10),
                         'size': QtCore.QSize(10, 10),
                         'turn_speed': 2,
                         'move_speed': 3,
                         'brush': QtCore.Qt.SolidPattern,
                         'pen': QtCore.Qt.SolidLine,
                         'brush_color': QtCore.Qt.red,
                         'pen_color': QtCore.Qt.black,
                         'shot_pen': QtCore.Qt.DotLine,
                         'shot_pen_color': QtCore.Qt.red})

        self.add_object({'type': 'player',
                         'position': QtCore.QPoint(10, 50),
                         'size': QtCore.QSize(10, 10),
                         'turn_speed': 2,
                         'move_speed': 3,
                         'brush': QtCore.Qt.SolidPattern,
                         'pen': QtCore.Qt.SolidLine,
                         'brush_color': QtCore.Qt.green,
                         'pen_color': QtCore.Qt.black,
                         'shot_pen': QtCore.Qt.DotLine,
                         'shot_pen_color': QtCore.Qt.green})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 50),
                                      QtCore.QPoint(200, 50),
                                      QtCore.QPoint(200, 100),
                                      QtCore.QPoint(100, 100)],
                         'texture': 'cobblestone.bmp'})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(390, 50),
                                      QtCore.QPoint(500, 50),
                                      QtCore.QPoint(500, 100),
                                      QtCore.QPoint(390, 100)],
                         'texture': 'cobblestone.bmp'})

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
            # Raise an error
            raise ValueError('No positions were given')

        self.information = {}
        for key in d:
            if key != 'type' or key != 'position':
                self.information[key] = d[key]

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
        result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[len(self.polygon) - 1]),
                                    QtCore.QPointF(self.polygon[0])))
        return result

