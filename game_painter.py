from PyQt4.QtCore import QPoint as Qp
from PyQt4.QtCore import QPointF as Qpf
from PyQt4.QtCore import QRect as Qr
from PyQt4.QtCore import QLine as Ql
from PyQt4.QtCore import QLineF as Qlf
from PyQt4 import QtGui

import os


class Paint():
    def __init__(self):
        pass

    @staticmethod
    def draw_background(painter, background, map_size):
        brush = QtGui.QBrush()
        brush.setTexture(background)

        painter.setBrush(brush)
        painter.drawRect(Qr(Qp(0, 0), map_size))

    @staticmethod
    def draw_map_borders(painter, view_position, view_size, map_size, default_values):
        brush = QtGui.QBrush()
        brush.setStyle(default_values['border_brush'])
        brush.setColor(default_values['border_brush_color'])
        painter.setBrush(brush)

        pen = QtGui.QPen()
        pen.setStyle(default_values['border_pen'])
        pen.setColor(default_values['border_pen_color'])
        painter.setPen(pen)

        if view_position.x() < 0:
            print('view leaves map in x (lower than 0)')
            painter.drawRect(view_position.x(), 0, abs(view_position.x()), map_size.height())

        if view_position.y() < 0:
            print('view leaves map in y (lower than 0)')
            painter.drawRect(0, view_position.y(), map_size.width(), abs(view_position.y()))

        if view_position.x() + view_size.width() > map_size.width():
            print('view leaves map in x (higher than map width)')
            painter.drawRect(map_size.width(), 0, map_size.width() + view_position.x(), map_size.height())

        if view_position.y() + view_size.height() > map_size.height():
            print('view leaves map in y (higher than map height)')
            painter.drawRect(0, map_size.height(), map_size.width(), view_position.y())

    @staticmethod
    def draw_indicator_line(painter,
                            player,
                            player_pos,
                            player_size,
                            player_turn_angle,
                            player_indicator_line_len,
                            default_values):
        pen = QtGui.QPen()

        if 'shot_pen' in player.information:
            pen.setStyle(player.information['shot_pen'])
        else:
            pen.setStyle(default_values['shot_pen'])

        if 'shot_pen_color' in player.information:
            pen.setColor(player.information['shot_pen_color'])
        else:
            pen.setColor(default_values['shot_pen_color'])

        painter.setPen(pen)

        player_rectangle = Qr(player_pos, player_size)
        line = Qlf(Qpf(player_rectangle.center().x(),
                       player_rectangle.center().y()),
                   Qpf(player_rectangle.center() + Qp(1, 0)))

        line.setLength(player_indicator_line_len)
        line.setAngle(player_turn_angle)

        painter.drawLine(line)

    @staticmethod
    def draw_shot(painter, player, default_values, shot_line_list):
        """Draws shot of the player"""

        pen = QtGui.QPen()

        if 'shot_pen' in player.information:
            pen.setStyle(player.information['shot_pen'])
        else:
            pen.setStyle(default_values['shot_pen'])

        if 'shot_pen_color' in player.information:
            pen.setColor(player.information['shot_pen_color'])
        else:
            pen.setColor(default_values['shot_pen_color'])

        painter.setPen(pen)

        if not shot_line_list:
            return

        for line in shot_line_list:
            painter.drawLine(Ql(Qp(line.p1().x(),
                                   line.p1().y()),
                                Qp(line.p2().x(),
                                   line.p2().y())))

    @staticmethod
    def draw_obstacles(painter, obstacle_list, default_values, file_locations):
        """Draws obstacles"""

        for polygon in obstacle_list:
            point_list = []

            brush = QtGui.QBrush()
            pen = QtGui.QPen()

            if 'brush' in polygon.information:
                brush.setStyle(polygon.information['brush'])
            else:
                brush.setStyle(default_values['obstacle_brush'])

            if 'brush_color' in polygon.information:
                brush.setColor(polygon.information['brush_color'])
            else:
                brush.setColor(default_values['obstacle_brush_color'])

            if 'pen' in polygon.information:
                pen.setStyle(polygon.information['pen'])
            else:
                pen.setStyle(default_values['obstacle_pen'])

            if 'pen_color' in polygon.information:
                pen.setColor(polygon.information['pen_color'])
            else:
                pen.setColor(default_values['obstacle_pen_color'])

            if 'texture' in polygon.information:
                texture = QtGui.QPixmap()
                texture.load(os.path.dirname(__file__) + file_locations['textures'] + polygon.information['texture'])
                brush.setTexture(texture)

            painter.setBrush(brush)
            painter.setPen(pen)

            for point in polygon.polygon:
                point_list.append(Qp(point.x(), point.y()))
            painter.drawPolygon(QtGui.QPolygon(point_list))

    @staticmethod
    def draw_player(painter, player, default_values, file_locations):
        """Draws the player"""
        rect = Qr(player.pos, player.size)

        brush = QtGui.QBrush()
        pen = QtGui.QPen()

        if 'brush' in player.information:
            brush.setStyle(player.information['brush'])
        else:
            brush.setStyle(default_values['player_brush'])

        if 'brush_color' in player.information:
            brush.setColor(player.information['brush_color'])
        else:
            brush.setColor(default_values['brush_color'])

        if 'pen' in player.information:
            pen.setStyle(player.information['pen'])
        else:
            pen.setStyle(default_values['player_pen'])

        if 'pen_color' in player.information:
            pen.setColor(player.information['pen_color'])
        else:
            pen.setColor(default_values['player_pen_color'])

        if 'texture' in player.information:
                texture = QtGui.QPixmap()
                texture.load(os.path.dirname(__file__) + file_locations['textures'] + player.information['texture'])
                brush.setTexture(texture)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawRect(Qr(Qp(rect.topLeft().x(),
                               rect.topLeft().y()),
                            Qp(rect.bottomRight().x(),
                               rect.bottomRight().y())))
