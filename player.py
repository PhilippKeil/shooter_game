from PyQt4 import QtCore


class Player():
    def __init__(self, player_information, key_dict, player_id):
        self.pos = player_information['position']
        self.size = player_information['size']
        self.turn_speed = player_information['turn_speed']
        self.move_speed = player_information['move_speed']
        self.outlines_list = self.outlines()

        self.key_dict = key_dict
        self.player_id = player_id

        self.information = {}
        for key in player_information:
            if key != 'position' or key != 'size' or key != 'turn_speed' or key != 'move_speed':
                self.information[key] = player_information[key]

        self.shot = Shot()
        self.angle = 0
        self.indi_line_length = 30
        self.next_move_direction = QtCore.QPoint(0, 0)

    def __str__(self):
        """Returns the ID of the player. Starting with 1 as the first player"""
        return str(self.player_id + 1)

    def outlines(self):
        rect = QtCore.QRect(self.pos, self.size)
        return [QtCore.QLineF(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.bottomLeft())),
                QtCore.QLineF(QtCore.QPointF(rect.bottomLeft()), QtCore.QPointF(rect.bottomRight())),
                QtCore.QLineF(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.topRight())),
                QtCore.QLineF(QtCore.QPointF(rect.topRight()), QtCore.QPointF(rect.bottomRight()))]

    def try_move(self, move_direction, step_size, map_size, obstacle_list):
        """Returns the best possible (farthest with given step_size) new position for the player.
        Returns the current position of the player, if no other solution is possible."""

        # Translate the move direction into coordinates
        if move_direction == 'up':
            move_direction = QtCore.QPoint(0, -1)
        elif move_direction == 'down':
            move_direction = QtCore.QPoint(0, 1)
        elif move_direction == 'left':
            move_direction = QtCore.QPoint(-1, 0)
        elif move_direction == 'right':
            move_direction = QtCore.QPoint(1, 0)

        for a in range(step_size, 1, -1):
            new_rect = QtCore.QRect(QtCore.QPoint(self.pos.x() + move_direction.x() * a,
                                                  self.pos.y() + move_direction.y() * a),
                                    self.size)

            # Check if new positions are inside the viewable area of the map
            if new_rect.topLeft().x() >= 0 and new_rect.topLeft().y() >= 0 and \
                    new_rect.bottomRight().x() <= map_size.width() and \
                    new_rect.bottomRight().y() <= map_size.height():
                # Positions are inside the window
                # Check if player comes into contact with an obstacle
                # Check if uL or bR of the player are contained by an obstacle

                # Iterate through the list of obstacles
                for a in range(len(obstacle_list)):
                    if obstacle_list[a].polygon.containsPoint(new_rect.topLeft(),
                                                              QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].polygon.containsPoint(new_rect.topRight(),
                                                                   QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].polygon.containsPoint(new_rect.bottomRight(),
                                                                   QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].polygon.containsPoint(new_rect.bottomLeft(),
                                                                   QtCore.Qt.OddEvenFill) % 2 == 1:

                        # The player is inside an obstacle
                        # Break out of the loop because if player contains one obstacle its worthless to check any other
                        break
                    else:
                        # The player is outside of the obstacle
                        # Iterate to the next obstacle
                        continue
                else:
                    # Getting here means no break was thrown
                    # No obstacle in the way
                    return new_rect.topLeft()
            else:
                # Positions are outside the window
                pass
            continue
        else:
            # Not even the smallest possible step (1) was possible
            return self.pos

    def force_move(self, point):
        """Force a player move command."""
        self.pos = point

    def get_pos(self):
        return self.pos

    def get_size(self):
        return self.size


class Shot():
    def __init__(self):
        self.start_pos = QtCore.QPoint(0, 0)
        self.end_pos = QtCore.QPoint(0, 0)
        self.shot_up_time = 1000  # ms how long the shot should be visible
        self.max_length = 1000
        self.current_shot = []

        self.shot_timer = QtCore.QTimer()
        self.shot_timer.setInterval(self.shot_up_time)
        self.shot_timer.setSingleShot(True)

    def set(self, start_point, end_point, outline_list, map_size):
        if not self.shot_timer.isActive():
            self.current_shot = self.compute_whole(start_point, end_point, outline_list, map_size)
            self.shot_timer.start()

    def get(self):
        if self.shot_timer.isActive():
            return self.current_shot
        else:
            return False

    def compute_whole(self, start_point, ideal_end_point, outline_list, map_size):
        # Append the outlines of the map to outline_list so the shot gets reflected by the map borders too
        outline_list.append([QtCore.QLineF(QtCore.QPointF(0, 0),
                                           QtCore.QPointF(map_size.width(), 0)),
                             QtCore.QLineF(QtCore.QPointF(map_size.width(), 0),
                                           QtCore.QPointF(map_size.width(), map_size.height())),
                             QtCore.QLineF(QtCore.QPointF(0, 0),
                                           QtCore.QPointF(0, map_size.height())),
                             QtCore.QLineF(QtCore.QPointF(0, map_size.height()),
                                           QtCore.QPointF(map_size.width(), map_size.height()))])

        shot_start_pos = QtCore.QPointF(start_point)
        shot_end_pos = QtCore.QPointF(ideal_end_point)
        length = self.max_length

        angle = QtCore.QLineF(shot_start_pos, shot_end_pos).angle()
        shot_line_list = []

        while length > 0.0:
            shot_end_pos, angle, length = self.compute_section(shot_start_pos, angle, length, outline_list)

            shot_line_list.append(QtCore.QLineF(QtCore.QPointF(shot_start_pos), shot_end_pos))

            shot_start_pos = shot_end_pos

        return shot_line_list

    @staticmethod
    def compute_section(start_point,  angle, length, outline_list):
        # Returns the end point of the shot
        # whether its the actual end or just a collision with an obstacle can be seen in var Length
        # if remaining Length is 0 after calling the method, its the actual endpoint of the line
        # if remaining Length is not 0, call the method again with the remaining length

        # The method also returns the outgoing angle of the line if it has hit an obstacle
        # Therefore it CHANGES var angle and var length

        # Create the ideal line
        max_line = QtCore.QLineF(start_point, start_point + QtCore.QPointF(1, 0))
        max_line.setLength(length)
        max_line.setAngle(angle)

        # Find the intersection between that line and all obstacle outlines
        intersection = QtCore.QPointF()

        # Iterate trough all outlines
        for a in range(len(outline_list)):
            for b in range(len(outline_list[a])):
                if max_line.intersect(outline_list[a][b], intersection) == 1:
                    # Intersection of both lines in self.intersection
                    max_line = QtCore.QLineF(start_point, intersection)
                    # Compute the outgoing angle of the shot
                    # It is done here, because I need the obstacle outline to compute it
                    angle = max_line.angleTo(outline_list[a][b]) + outline_list[a][b].angle()

        # max_line is now as short as possible

        # Return the remaining length
        length -= round(max_line.length())

        # Get angle inside 0 - 360
        if angle >= 360:
            angle -= 360
        elif angle < 0:
            angle += 360

        # Set Length of max_line
        # If not done, the start point of the next line would instantly intersect the same outline again
        # Resulting in an infinite loop
        max_line.setLength(max_line.length() - 1)

        return max_line.p2(), angle, length