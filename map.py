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
        # Used for drawing
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        # Used for collision
        self.outlines_list = []
        # Contains every powerup platform that is present in the map
        self.powerup_list = []
        # Contains effects for every powerup on the map
        self.powerup_effect_dict = {}

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
            obstacle = Obstacle(d['position'], self.file_locations)
            if 'brush' in d:
                obstacle.set_brush(self.file_locations, brush=d['brush'])
            if 'pen' in d:
                obstacle.set_pen(pen=d['pen'])
            if 'brush_color' in d:
                obstacle.set_brush_color(brush_color=d['brush_color'])
            if 'pen_color' in d:
                obstacle.set_pen_color(pen_color=d['pen_color'])
            if 'texture' in d:
                obstacle.set_brush(self.file_locations, texture_file=d['texture'])

            self.obstacle_list.append(obstacle)
            self.outlines_list.append(obstacle.get_boundaries())
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
        elif d['type'] == 'powerup':
            # Create a powerup
            try:
                powerup = Powerup(d)
            except ValueError as e:
                print('Could not create powerup because ' + e.message)
            else:
                self.powerup_list.append(powerup)
                for key in iter(d['available_powerups']):
                    # Iterate through every available powerup on that powerup platform
                    # Append the powerup effects to powerup_effect_dict if they are not present yet
                    if not key in self.powerup_effect_dict:
                        # The powerup available on that platform is not yet inside the dict of powerup effects
                        self.powerup_effect_dict[key] = d['available_powerups'][key]
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
                        'position': QtCore.QPoint(600, 50),
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
                        'texture': 'planks_jungle.bmp'},

                       {'type': 'powerup',
                        'position': [QtCore.QPoint(385, 275),
                                     QtCore.QPoint(415, 275),
                                     QtCore.QPoint(415, 305),
                                     QtCore.QPoint(385, 305)],
                        'available_powerups': {'move_faster': 10,
                                               'turn_faster': 5,
                                               'shot_longer': 2000},
                        'pen': QtCore.Qt.SolidLine,
                        'pen_color': QtCore.Qt.red},

                       {'type': 'powerup',
                        'position': [QtCore.QPoint(185, 275),
                                     QtCore.QPoint(215, 275),
                                     QtCore.QPoint(215, 305),
                                     QtCore.QPoint(185, 305)],
                        'available_powerups': {'move_faster': 5,
                                               'turn_faster': 5}},

                       {'type': 'powerup',
                        'position': [QtCore.QPoint(585, 275),
                                     QtCore.QPoint(615, 275),
                                     QtCore.QPoint(615, 305),
                                     QtCore.QPoint(585, 305)],
                        'available_powerups': {'move_faster': 5,
                                               'turn_faster': 5}}]

        result = [init_data]
        for obj in object_data:
            result.append(obj)

        return result


class Obj():
    def __init__(self, polygon_points):
        self.polygon = QtGui.QPolygon(polygon_points)

    def check_collision(self, rect):
        if self.polygon.containsPoint(rect.topLeft(), QtCore.Qt.OddEvenFill) or\
           self.polygon.containsPoint(rect.topRight(), QtCore.Qt.OddEvenFill) or\
           self.polygon.containsPoint(rect.bottomLeft(), QtCore.Qt.OddEvenFill) or\
           self.polygon.containsPoint(rect.bottomRight(), QtCore.Qt.OddEvenFill):
            return True
        else:
            return False

    def get_boundaries(self):
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


class Obstacle(Obj):
    def __init__(self, polygon_points, file_locations):
        """initiation"""
        Obj.__init__(self, polygon_points)
        self.brush = QtGui.QBrush()
        self.pen = QtGui.QPen()

        self.set_pen()
        self.set_pen_color()

        self.set_brush(file_locations)
        self.set_brush_color()

    def set_brush(self, file_locations, brush=QtCore.Qt.SolidPattern, texture_file=None):
        # Sets the brush to texture
        # If no texture is given, set brush to parameter brush and brush_color
        if texture_file is None:
            self.brush.setStyle(brush)
        else:
            try:
                texture = QtGui.QPixmap(os.path.dirname(__file__) + file_locations['textures'] + texture_file)
                self.brush.setTexture(texture)
            except:
                self.brush.setStyle(brush)

    def set_brush_color(self, brush_color=QtCore.Qt.red):
        self.brush.setColor(brush_color)

    def set_pen(self, pen=QtCore.Qt.SolidLine):
        self.pen.setStyle(pen)

    def set_pen_color(self, pen_color=QtCore.Qt.green):
        self.pen.setColor(pen_color)

    def draw(self, painter):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPolygon(self.polygon)


class Powerup(Obj):
    def __init__(self, d):
        Obj.__init__(self, d)
        self.available_powerups = d['available_powerups']