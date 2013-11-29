from PyQt4 import QtGui
from PyQt4 import QtCore


class Map():

    def __init__(self, load_type):

        # Contains every obstacle element that is present in the map
        self.obstacle_list = []
        # Contains the outlines of every obstacle element that is in the map
        self.outlines_list = []

        # def load_from_test variable definition
        self.size = 0
        self.view_size = 0

        # Init the map and declare which map to use
        if load_type == 'debug':
            # Just load the debug map
            self.load_from_test()
        else:
            print('load_type not supported')

    def add_obstacle(self, point_list):

        # Create the obstacle
        obstacle = Obstacle(point_list)

        # Add the obstacle to the lists obstacle_list and outlines_list
        self.obstacle_list.append(obstacle.polygon)
        self.outlines_list.append(obstacle.outlines())

    def load_from_test(self):

        # This method loads up a debugging map which is declared in here
        self.size = QtCore.QSize(800, 600)
        self.view_size = QtCore.QSize(300, 300)
        self.add_obstacle([QtCore.QPoint(100, 100),
                          QtCore.QPoint(390, 100),
                          QtCore.QPoint(390, 290),
                          QtCore.QPoint(100, 290)])

        self.add_obstacle([QtCore.QPoint(500, 500),
                          QtCore.QPoint(690, 500),
                          QtCore.QPoint(790, 590),
                          QtCore.QPoint(500, 590)])

    def change_view_size(self, width, height, frame_size):
        if width <= frame_size.width():
            self.view_size.setWidth(width)
        if height <= frame_size.height():
            self.view_size.setHeight(height)

        main_UI.game_window.change_stretch()


class Obj():
    def __init__(self):
        self.pos = None
        self.size = None
        self.polygon = None

    def center(self):
        return QtCore.QRect(self.pos, self.size).center()

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


class Obstacle(Obj):
    def __init__(self, point_list):
        Obj.__init__(self)
        self.polygon = QtGui.QPolygon(point_list)

