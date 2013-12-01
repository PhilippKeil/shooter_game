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
        self.size = QtCore.QSize(800, 600)
        self.view_size = QtCore.QSize(300, 300)

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
                         'position': QtCore.QPoint(50, 50),
                         'size': QtCore.QSize(10, 10),
                         'turn_speed': 2,
                         'move_speed': 5,
                         'brush_color': colors['Turquoise'],
                         'shot_pen': QtCore.Qt.DotLine,
                         'shot_pen_color': QtCore.Qt.blue})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 0),
                                      QtCore.QPoint(100, 100),
                                      QtCore.QPoint(150, 100),
                                      QtCore.QPoint(150, 0)],
                         'pen': QtCore.Qt.SolidLine,
                         'pen_color': QtCore.Qt.black,
                         'texture': 'sand.bmp'})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(150, 0),
                                      QtCore.QPoint(150, 100),
                                      QtCore.QPoint(200, 100),
                                      QtCore.QPoint(200, 0)],
                         'pen': QtCore.Qt.SolidLine,
                         'pen_color': QtCore.Qt.black,
                         'texture': 'cobblestone.bmp'})

        # COLOR TESTS
        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(0, 200),
                                      QtCore.QPoint(20, 200),
                                      QtCore.QPoint(20, 220),
                                      QtCore.QPoint(0, 220)],
                         'brush_color': colors['Turquoise']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(20, 200),
                                      QtCore.QPoint(40, 200),
                                      QtCore.QPoint(40, 220),
                                      QtCore.QPoint(20, 220)],
                         'brush_color': colors['Emerald']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(40, 200),
                                      QtCore.QPoint(60, 200),
                                      QtCore.QPoint(60, 220),
                                      QtCore.QPoint(40, 220)],
                         'brush_color': colors['Peter River']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(60, 200),
                                      QtCore.QPoint(80, 200),
                                      QtCore.QPoint(80, 220),
                                      QtCore.QPoint(60, 220)],
                         'brush_color': colors['Amethyst']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(80, 200),
                                      QtCore.QPoint(100, 200),
                                      QtCore.QPoint(100, 220),
                                      QtCore.QPoint(80, 220)],
                         'brush_color': colors['Wet Asphalt']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 200),
                                      QtCore.QPoint(120, 200),
                                      QtCore.QPoint(120, 220),
                                      QtCore.QPoint(100, 220)],
                         'brush_color': colors['Sun Flower']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(120, 200),
                                      QtCore.QPoint(140, 200),
                                      QtCore.QPoint(140, 220),
                                      QtCore.QPoint(120, 220)],
                         'brush_color': colors['Carrot']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(140, 200),
                                      QtCore.QPoint(160, 200),
                                      QtCore.QPoint(160, 220),
                                      QtCore.QPoint(140, 220)],
                         'brush_color': colors['Alizarin']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(160, 200),
                                      QtCore.QPoint(180, 200),
                                      QtCore.QPoint(180, 220),
                                      QtCore.QPoint(160, 220)],
                         'brush_color': colors['Clouds']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(180, 200),
                                      QtCore.QPoint(200, 200),
                                      QtCore.QPoint(200, 220),
                                      QtCore.QPoint(180, 220)],
                         'brush_color': colors['Concrete']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(0, 220),
                                      QtCore.QPoint(20, 220),
                                      QtCore.QPoint(20, 240),
                                      QtCore.QPoint(0, 240)],
                         'brush_color': colors['Green Sea']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(20, 220),
                                      QtCore.QPoint(40, 220),
                                      QtCore.QPoint(40, 240),
                                      QtCore.QPoint(20, 240)],
                         'brush_color': colors['Nephritis']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(40, 220),
                                      QtCore.QPoint(60, 220),
                                      QtCore.QPoint(60, 240),
                                      QtCore.QPoint(40, 240)],
                         'brush_color': colors['Belize Hole']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(60, 220),
                                      QtCore.QPoint(80, 220),
                                      QtCore.QPoint(80, 240),
                                      QtCore.QPoint(60, 240)],
                         'brush_color': colors['Wisteria']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(80, 220),
                                      QtCore.QPoint(100, 220),
                                      QtCore.QPoint(100, 240),
                                      QtCore.QPoint(80, 240)],
                         'brush_color': colors['Midnight Blue']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(100, 220),
                                      QtCore.QPoint(120, 220),
                                      QtCore.QPoint(120, 240),
                                      QtCore.QPoint(100, 240)],
                         'brush_color': colors['Orange']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(120, 220),
                                      QtCore.QPoint(140, 220),
                                      QtCore.QPoint(140, 240),
                                      QtCore.QPoint(120, 240)],
                         'brush_color': colors['Pumpkin']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(140, 220),
                                      QtCore.QPoint(160, 220),
                                      QtCore.QPoint(160, 240),
                                      QtCore.QPoint(140, 240)],
                         'brush_color': colors['Pomegranate']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(160, 220),
                                      QtCore.QPoint(180, 220),
                                      QtCore.QPoint(180, 240),
                                      QtCore.QPoint(160, 240)],
                         'brush_color': colors['Silver']})

        self.add_object({'type': 'obstacle',
                         'position': [QtCore.QPoint(180, 220),
                                      QtCore.QPoint(200, 220),
                                      QtCore.QPoint(200, 240),
                                      QtCore.QPoint(180, 240)],
                         'brush_color': colors['Asbestos']})


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
        result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[len(self.polygon) - 1]), QtCore.QPointF(self.polygon[0])))
        return result

