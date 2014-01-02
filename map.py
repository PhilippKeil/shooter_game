from PyQt4 import QtGui
from PyQt4 import QtCore
import pickle
import os

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
    def __init__(self, file_locations, load_type, save_file=None):
        # Contains every obstacle element that is present in the map
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlines_list = []

        # Save player information after map has been loaded
        self.player_information = []
        # Save locations to textures and whatnot locally
        self.file_locations = file_locations

        self.size = None
        self.view_size = None
        self.background = None
        self.view_position = QtCore.QPoint(0, 0)

        # Init the map and declare which map to use
        if load_type == 'test':
            # Just load the debug map
            self.convert_data_to_level(self.test_map())
        elif load_type == 'file':
            self.convert_data_to_level(self.load_from_file(save_file))

    def get_player_information(self):
        return self.player_information

    def convert_data_to_level(self, data):
        for obj in data:
            # obj is either a list, containing basic information about the level,
            # which is needed for every level (size and stuff)
            # OR it is a dict which contains information about an object which should be loaded into the map
            if type(obj) == dict:
                self.add_object(obj)
            elif type(obj) == list:
                self.map_initialization(obj)

    def map_initialization(self, data):
        self.size = QtCore.QSize(data[0][0], data[0][1])
        self.view_size = QtCore.QSize(data[1][0], data[1][1])
        self.view_position = QtCore.QPoint(data[2][0], data[2][1])

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
        elif d['type'] == 'background':
            if 'shadow' in d:
                shadow = d['shadow']
            else:
                shadow = 1

            image = QtGui.QImage()
            image.load(os.path.dirname(__file__) + self.file_locations['textures'] + d['texture'])
            for y in range(image.height()):
                for x in range(image.width()):
                    pixel = image.pixel(x, y)
                    r = QtGui.qRed(pixel) / shadow
                    g = QtGui.qGreen(pixel) / shadow
                    b = QtGui.qBlue(pixel) / shadow
                    image.setPixel(x, y, QtGui.qRgba(r, g, b, 255))
            self.background = QtGui.QPixmap()
            self.background.convertFromImage(image, QtCore.Qt.DiffuseAlphaDither)
        else:
            print('Could not create object. Type (' + d['type'] + ') is unknown')

    def load_from_file(self, filename):
        try:
            with open(os.path.dirname(__file__) + self.file_locations['levels'] + filename, 'rb') as f:
                return pickle.load(f)
        except IOError as e:
            print('File could not be handled (' + e.message + ')')

    def save_to_file(self, filename, data):
        try:
            with open(os.path.dirname(__file__) + self.file_locations['levels'] + filename, 'wb') as f:
                pickle.dump(data, f)
        except IOError as e:
            print('File could not be handled (' + e.message + ')')

    @staticmethod
    def test_map():
        """
        {'type': '',
         'position': QtCore.QPoint(),
         'brush': QtCore.Qt.,
         'brush_color': QtCore.Qt.,
         'pen': QtCore.Qt.,
         'pen_color': QtCore.Qt.,
         'texture': ''})
        """
        # Map initialization for size, view_size, view_position
        init_data = [(800, 600), (400, 400), (0, 0)]

        object_data = [{'type': 'player',
                        'position': QtCore.QPoint(30, 100),
                        'size': QtCore.QSize(10, 10),
                        'turn_speed': 2,
                        'move_speed': 3,
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.red,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.red},

                       {'type': 'player',
                        'position': QtCore.QPoint(10, 30),
                        'size': QtCore.QSize(10, 10),
                        'turn_speed': 2,
                        'move_speed': 3,
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.blue,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.blue},

                       {'type': 'player',
                        'position': QtCore.QPoint(10, 50),
                        'size': QtCore.QSize(10, 10),
                        'turn_speed': 2,
                        'move_speed': 3,
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.green,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.green},

                       {'type': 'background',
                        'texture': 'stonebrick.bmp',
                        'shadow': 3},

                       {'type': 'obstacle',
                        'position': [QtCore.QPoint(290, 0),
                                     QtCore.QPoint(510, 0),
                                     QtCore.QPoint(510, 60),
                                     QtCore.QPoint(400, 60),
                                     QtCore.QPoint(400, 140),
                                     QtCore.QPoint(380, 140),
                                     QtCore.QPoint(380, 60),
                                     QtCore.QPoint(290, 60)],
                        'texture': 'planks_jungle.bmp'},

                       {'type': 'obstacle',
                        'position': [QtCore.QPoint(290, 110),
                                     QtCore.QPoint(310, 110),
                                     QtCore.QPoint(310, 190),
                                     QtCore.QPoint(490, 190),
                                     QtCore.QPoint(490, 110),
                                     QtCore.QPoint(510, 110),
                                     QtCore.QPoint(510, 310),
                                     QtCore.QPoint(490, 310),
                                     QtCore.QPoint(490, 210),
                                     QtCore.QPoint(310, 210),
                                     QtCore.QPoint(310, 220),
                                     QtCore.QPoint(290, 220)],
                        'texture': 'planks_jungle.bmp'},

                       {'type': 'obstacle',
                        'position': [QtCore.QPoint(290, 270),
                                     QtCore.QPoint(310, 270),
                                     QtCore.QPoint(310, 370),
                                     QtCore.QPoint(490, 370),
                                     QtCore.QPoint(490, 360),
                                     QtCore.QPoint(510, 360),
                                     QtCore.QPoint(510, 470),
                                     QtCore.QPoint(490, 470),
                                     QtCore.QPoint(490, 390),
                                     QtCore.QPoint(310, 390),
                                     QtCore.QPoint(310, 470),
                                     QtCore.QPoint(290, 470)],
                        'texture': 'planks_jungle.bmp'},

                       {'type': 'obstacle',
                        'position': [QtCore.QPoint(290, 530),
                                     QtCore.QPoint(400, 530),
                                     QtCore.QPoint(400, 450),
                                     QtCore.QPoint(420, 450),
                                     QtCore.QPoint(420, 530),
                                     QtCore.QPoint(510, 530),
                                     QtCore.QPoint(510, 600),
                                     QtCore.QPoint(290, 600)],
                        'texture': 'planks_jungle.bmp'}]


        result = [init_data]
        for obj in object_data:
            result.append(obj)

        return result


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
        # Index 0 is skipped because it has nothing to draw a line to
        # Start at index 1. Make a line from 0 to 1
        for a in range(1, len(self.polygon)):
            result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[a-1]), QtCore.QPointF(self.polygon[a])))
            # append the last line from the last index to
        result.append(QtCore.QLineF(QtCore.QPointF(self.polygon[len(self.polygon) - 1]),
                                    QtCore.QPointF(self.polygon[0])))
        return result