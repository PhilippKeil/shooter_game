from PyQt4 import QtCore


class Player():
    def __init__(self, x, y, w, h):
        self.pos = QtCore.QPoint(x, y)
        self.size = QtCore.QSize(w, h)
        self.shot = Shot()
        self.turn_speed = 2
        self.angle = 0
        self.indi_line_length = 30
        self.move_speed = 5
        self.next_move_direction = QtCore.QPoint(0, 0)

    def try_move(self, move_direction, step_size, viewable_map_area, obstacle_list):
        """Returns the best possible (farthest with given step_size) new position for the player.
        Returns the current position of the player, if no other solution is possible."""
        for a in range(step_size, 1, -1):
            new_rect = QtCore.QRect(QtCore.QPoint(self.pos.x() + move_direction.x() * a,
                                                  self.pos.y() + move_direction.y() * a),
                                    self.size)

            # Check if new positions are inside the viewable area of the map
            if new_rect.topLeft().x() >= 0 and new_rect.topLeft().y() >= 0 and \
                    new_rect.bottomRight().x() <= viewable_map_area.width() and \
                    new_rect.bottomRight().y() <= viewable_map_area.height():
                # Positions are inside the window
                # Check if player comes into contact with an obstacle
                # Check if uL or bR of the player are contained by an obstacle

                # Iterate through the list of obstacles
                for a in range(len(obstacle_list)):
                    if obstacle_list[a].containsPoint(new_rect.topLeft(), QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].containsPoint(new_rect.topRight(), QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].containsPoint(new_rect.bottomRight(), QtCore.Qt.OddEvenFill) % 2 == 1 or \
                            obstacle_list[a].containsPoint(new_rect.bottomLeft(), QtCore.Qt.OddEvenFill) % 2 == 1:

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

    def get_shot(self):
        """Returns shot of the player. Returns an empty list if no shot is fired"""

        # Return an empty list if no shot is fired
        if not self.shot.timer.isActive():
            return []

        # Return the list of lines
        return self.shot.compute_shot()


class Shot():
    def __init__(self):

        self.start_pos = QtCore.QPoint(0, 0)
        self.end_pos = QtCore.QPoint(0, 0)
        self.shot_up_time = 400  # ms how long the shot should be visible
        self.max_length = 1000
        self.current_shot = []

        # init a timer
        # A Timer to fade out the shot after a certain time is initiated
        self.timer = QtCore.QTimer()
        QtCore.QTimer.setInterval(self.timer, self.shot_up_time)
        QtCore.QTimer.setSingleShot(self.timer, True)
        self.timer.stop()

    def try_shot(self, s_point, e_point, outline_list):
        # Try to set new shot
        # This is only possible if the old shot has faded away
        if not self.timer.isActive():
            self.current_shot = self.get_whole_shot(s_point, e_point, outline_list)
            # The fade out timer is started
            self.timer.start()

    def compute_shot_section(self, start_point,  angle, length, outline_list):
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
                    print('intersection')
                    # Compute the outgoing angle of the shot
                    # It is done here, because I need the obstacle outline to compute it
                    angle = max_line.angleTo(outline_list[a][b]) + outline_list[a][b].angle()
                else:
                    print('No intersection')

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

    def get_whole_shot(self, start_point, ideal_end_point, outline_list):

        shot_start_pos = QtCore.QPointF(start_point)
        shot_end_pos = QtCore.QPointF(ideal_end_point)
        length = self.max_length

        angle = QtCore.QLineF(shot_start_pos, shot_end_pos).angle()
        shot_line_list = []

        # Iterate through the loop until the remaining length = 0
        # It then executes the else statement
        while length > 0.0:
            shot_end_pos, angle, length = self.compute_shot_section(shot_start_pos,
                                                                    angle,
                                                                    length,
                                                                    outline_list)

            shot_line_list.append(QtCore.QLineF(QtCore.QPointF(shot_start_pos), shot_end_pos))

            shot_start_pos = shot_end_pos

        return shot_line_list

