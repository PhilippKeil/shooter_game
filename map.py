from PyQt4 import QtGui
from PyQt4 import QtCore
import pickle
import os
import threading
import random

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

powerup_colors = {'turn_faster': QtCore.Qt.red,
                  'move_faster': QtCore.Qt.green,
                  'shot_longer': QtCore.Qt.blue}


class Map():
    def __init__(self, file_locations, save_file=None):
        # Contains every obstacle element that is present in the map
        # Used for drawing
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        # Used for collision
        self.outlines_list = []
        # Contains every powerup platform that is present in the map
        self.powerup_list = []
        # Contains every background
        self.background_list = []

        self.powerup_colors = powerup_colors

        # Save player information after map has been loaded
        self.player_information = []

        # Save locations to textures etc. locally
        self.file_locations = file_locations

        self.size = None
        self.view_size = None
        self.background = None
        self.view_position = QtCore.QPoint(0, 0)

        # Init the map and declare which map to use
        if save_file is not None:
            self.convert_data_to_level(self.load_from_file(save_file))
        else:
            # Just load the debug map
            self.convert_data_to_level(self.test_map())

    def get_player_information(self):
        return self.player_information

    def convert_data_to_level(self, data):
        # index 0: crucial map information (dict)
        self.map_init(data[0]['map_size'], data[0]['view_size'], data[0]['view_pos'])

        # index 1: player data (list of dict)
        for player_data in data[1]:
            self.add_player(player_data)

        # index 2: obstacle data (list of dict)
        for obj_data in data[2]:
            self.add_obstacle(obj_data)

        # index 3: powerup platform data (list of dict)
        for powerup_data in data[3]:
            self.add_powerup(powerup_data)

        # index 4: background data (dict)
        for background_data in data[4]:
            self.add_background(background_data)

    def map_init(self, map_size, view_size, view_pos):
        self.size = map_size
        self.view_size = view_size
        self.view_position = view_pos

    def add_player(self, data):
        """Save the player object in the map class, until it is needed for creation of a player class"""
        self.player_information.append(data)

    def add_obstacle(self, data):
        obstacle = Obstacle(data['position'], self.file_locations)
        if 'brush' in data:
            obstacle.set_brush(self.file_locations, brush=data['brush'])
        if 'pen' in data:
            obstacle.set_pen(pen=data['pen'])
        if 'brush_color' in data:
            obstacle.set_brush_color(brush_color=data['brush_color'])
        if 'pen_color' in data:
            obstacle.set_pen_color(pen_color=data['pen_color'])
        if 'texture' in data:
            obstacle.set_brush(self.file_locations, texture_file=data['texture'])

        self.obstacle_list.append(obstacle)
        self.outlines_list.append(obstacle.get_boundaries())

    def add_powerup(self, data):
        if 'cooldown' in data:
            powerup = Powerup(data['position'],
                              data['available_powerups'],
                              cooldown=data['cooldown'])
        else:
            powerup = Powerup(data['position'],
                              data['available_powerups'])

        self.powerup_list.append(powerup)

    def add_background(self, data):
        if 'dim_effect' in data:
            background = Background(data['texture'],
                                    self.file_locations,
                                    self.size,
                                    dim_effect=True,
                                    dim_effect_strength=data['dim_effect'])
        else:
            background = Background(data['texture'],
                                    self.file_locations,
                                    self.size)
        if 'area' in data:
            background.set_area(data['area'])

        self.background_list.append(background)

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
        # Map initialization for size, view_size, view_position
        init_data = {'map_size': QtCore.QSize(800, 600),
                     'view_size': QtCore.QSize(400, 400),
                     'view_pos': QtCore.QPoint(0, 0)}

        player_data = [{'position': QtCore.QPoint(30, 100),
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.red,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.red},

                       {'position': QtCore.QPoint(10, 30),
                        'size': QtCore.QSize(10, 10),
                        'turn_speed': 2,
                        'move_speed': 3,
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.blue,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.blue},

                       {'position': QtCore.QPoint(600, 50),
                        'size': QtCore.QSize(10, 10),
                        'turn_speed': 2,
                        'move_speed': 3,
                        'brush': QtCore.Qt.SolidPattern,
                        'pen': QtCore.Qt.SolidLine,
                        'brush_color': QtCore.Qt.green,
                        'pen_color': QtCore.Qt.black,
                        'shot_pen': QtCore.Qt.SolidLine,
                        'shot_pen_color': QtCore.Qt.green}]

        obstacle_data = [{'position': [QtCore.QPoint(290, 0),
                                       QtCore.QPoint(510, 0),
                                       QtCore.QPoint(510, 60),
                                       QtCore.QPoint(400, 60),
                                       QtCore.QPoint(400, 140),
                                       QtCore.QPoint(380, 140),
                                       QtCore.QPoint(380, 60),
                                       QtCore.QPoint(290, 60)],
                          'texture': 'planks_jungle.bmp'},

                         {'position': [QtCore.QPoint(290, 110),
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

                         {'position': [QtCore.QPoint(290, 270),
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

                         {'position': [QtCore.QPoint(290, 530),
                                       QtCore.QPoint(400, 530),
                                       QtCore.QPoint(400, 450),
                                       QtCore.QPoint(420, 450),
                                       QtCore.QPoint(420, 530),
                                       QtCore.QPoint(510, 530),
                                       QtCore.QPoint(510, 600),
                                       QtCore.QPoint(290, 600)],
                          'texture': 'planks_jungle.bmp'}]

        powerup_data = [{'position': [QtCore.QPoint(385, 275),
                                      QtCore.QPoint(415, 275),
                                      QtCore.QPoint(415, 305),
                                      QtCore.QPoint(385, 305)],
                         'available_powerups': {'move_faster': 10,
                                                'turn_faster': 5,
                                                'shot_longer': 2000},
                         'pen': QtCore.Qt.SolidLine,
                         'pen_color': QtCore.Qt.red},

                        {'position': [QtCore.QPoint(185, 275),
                                      QtCore.QPoint(215, 275),
                                      QtCore.QPoint(215, 305),
                                      QtCore.QPoint(185, 305)],
                         'available_powerups': {'move_faster': 5,
                                                'turn_faster': 5}},

                        {'position': [QtCore.QPoint(585, 275),
                                      QtCore.QPoint(615, 275),
                                      QtCore.QPoint(615, 305),
                                      QtCore.QPoint(585, 305)],
                         'available_powerups': {'move_faster': 5,
                                                'turn_faster': 5}}]

        background_data = [{'texture': 'stonebrick.bmp',
                            'dim_effect': 3}]

        # index 0: crucial map information (dict)
        # index 1: player data (list of dict)
        # index 2: obstacle data (list of dict)
        # index 3: powerup platform data (list of dict)
        # index 4: background data (dict)
        return [init_data, player_data, obstacle_data, powerup_data, background_data]


class Obj():
    def __init__(self, polygon_points):
        self.polygon = QtGui.QPolygon(polygon_points)
        self.brush = QtGui.QBrush()
        self.pen = QtGui.QPen()

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

    def draw(self, painter):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPolygon(self.polygon)


class Obstacle(Obj):
    def __init__(self, polygon_points, file_locations):
        """initiation"""
        Obj.__init__(self, polygon_points)

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


class Powerup(Obj):
    def __init__(self, polygon_points, powerups, cooldown=10.0):

        Obj.__init__(self, polygon_points)

        self.set_pen()
        self.set_pen_color()

        self.set_brush()
        self.set_brush_color()

        self.powerups = powerups
        self.powerup_colors = powerup_colors
        self.cooldown = cooldown

        self.current_powerup = None
        self.spawn_powerup()

    def apply_powerup(self, player):
        if self.current_powerup == 'move_faster':
            player.move_speed = self.powerups['move_faster']

    def pickup_powerup(self, player):
        self.apply_powerup(player)

        self.current_powerup = None
        self.set_brush_color()
        timer = threading.Timer(self.cooldown, self.spawn_powerup, [player])
        timer.start()

    def spawn_powerup(self, player=None):
        """Spawns a powerup on the platform. Resets player (if there is one) who had the powerup to default values"""
        if player is not None:
            player.apply_defaults()

        self.current_powerup = random.choice(self.powerups.keys())
        print(self.current_powerup)
        self.set_brush_color(self.powerup_colors[self.current_powerup])

    def set_brush(self, brush=QtCore.Qt.SolidPattern):
        self.brush.setStyle(brush)

    def set_brush_color(self, brush_color=QtCore.Qt.lightGray):
        self.brush.setColor(brush_color)

    def set_pen(self, pen=QtCore.Qt.SolidLine):
        self.pen.setStyle(pen)

    def set_pen_color(self, pen_color=QtCore.Qt.red):
        self.pen.setColor(pen_color)


class Background():
    def __init__(self, texture_file, file_locations, map_size, dim_effect=False, dim_effect_strength=1):

        self.texture = QtGui.QPixmap()
        self.area = QtCore.QRect(QtCore.QPoint(0, 0), map_size)

        if dim_effect:
            # Apply a dim effect to the image before setting the background
            texture_image = QtGui.QImage(os.path.dirname(__file__) + file_locations['textures'] + texture_file)
            self.texture.convertFromImage(self.add_dim(texture_image, dim_effect_strength))
        else:
            # Set the background from the file as it is
            self.texture.load(os.path.dirname(__file__) + file_locations['textures'] + texture_file)

        self.brush = QtGui.QBrush(self.texture)

    def set_area(self, area):
        """Set the area where the background is to be displayed"""
        self.area = QtCore.QRect(area)

    def draw(self, painter):
        painter.setBrush(self.brush)
        painter.drawRect(self.area)

    @staticmethod
    def add_dim(image, strength):
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                r = QtGui.qRed(pixel) / strength
                g = QtGui.qGreen(pixel) / strength
                b = QtGui.qBlue(pixel) / strength
                image.setPixel(x, y, QtGui.qRgba(r, g, b, 255))
        return image