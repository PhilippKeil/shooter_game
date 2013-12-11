from player import Player
from map import Map
from game_painter import Paint

from PyQt4.QtCore import QSize, QPoint, QPointF, QRect, QLineF


class Game():
    # no effect???
    gameCycleInterval = 10  # Time in ms
    
    def __init__(self, list_of_key_setups, debug_key_setup):
        self.map = Map('debug')
        self.players = []
        self.debug_key_setup = debug_key_setup
        try:
            for player_id in range(len(self.map.player_information)):
                # Create as many players in the game as there are objects of players in the map
                self.players.append(Player(self.map.player_information[player_id],
                                           list_of_key_setups[player_id],
                                           player_id))
        except IndexError:
            print('Not enough key setups defined for so many players')

    def move_player(self, player, move_direction):
        """Tries to move the player. Returns True is it succeeded. False if player couldn't be moved"""
        new_player_pos = player.try_move(move_direction,
                                         player.move_speed,
                                         self.map.size,
                                         self.map.obstacle_list)
        if new_player_pos == player.pos:
            # Player wasn't moved
            return False
        else:
            # Player was moved
            player.force_move(new_player_pos)
            return True

    def handle_key(self, key):
        action = (None, None)

        # Check keys of the players
        for player in self.players:
            # Go through every key in the players key_dict and find the action associated with the key
            for player_key in player.key_dict:
                if player.key_dict[player_key] == key:
                    action = player, player_key

        # Check if there are debugging actions for the key and override the player action is necessary
        for debug_key in self.debug_key_setup:
            if self.debug_key_setup[debug_key] == key:
                # Assign a debug action
                action = 'DEBUG', debug_key

        # Perform a player action
        if action[1] == 'move_up':
            self.move_player(action[0], 'up')
        elif action[1] == 'move_down':
            self.move_player(action[0], 'down')
        elif action[1] == 'move_left':
            self.move_player(action[0], 'left')
        elif action[1] == 'move_right':
            self.move_player(action[0], 'right')
        elif action[1] == 'turn_left':
            self.turn_player(action[0], 'left')
        elif action[1] == 'turn_right':
            self.turn_player(action[0], 'right')
        elif action[1] == 'shoot':
            self.player_shoot(action[0])
        elif action[1] is None:
            print('No player event triggered')

        # Perform a debugging action
        if action[0] == 'DEBUG':
            print('DEBUG EVENT (' + action[1] + ')')
            if action[1] == 'debug_zoom_in':
                self.set_viewable_map_area_size(self.get_viewable_map_area_size() - QSize(1, 1))
            elif action[1] == 'debug_zoom_out':
                self.set_viewable_map_area_size(self.get_viewable_map_area_size() + QSize(1, 1))
            elif action[1] == 'debug_area_move_up':
                self.set_viewable_map_area_position(self.get_viewable_map_area_pos() - QPoint(0, 1))
            elif action[1] == 'debug_area_move_down':
                self.set_viewable_map_area_position(self.get_viewable_map_area_pos() + QPoint(0, 1))
            elif action[1] == 'debug_area_move_left':
                self.set_viewable_map_area_position(self.get_viewable_map_area_pos() - QPoint(1, 0))
            elif action[1] == 'debug_area_move_right':
                self.set_viewable_map_area_position(self.get_viewable_map_area_pos() + QPoint(1, 0))
            else:
                print('No action defined for DEBUG_EVENT (' + action[1] + ')')

    def draw_game(self, painter, graphic_setting, defaults):
        # Draw the map background
        if graphic_setting == 'high':
            Paint.draw_background(painter, self.get_map_background(), self.get_map_size())

        # Draw the map limits
        Paint.draw_map_borders(painter,
                               self.get_viewable_map_area_pos(),
                               self.get_viewable_map_area_size(),
                               self.get_map_size(),
                               defaults)

        # Draw obstacles
        Paint.draw_obstacles(painter, self.get_obstacle_list(), defaults)

        # Draw the model, indicator line and shot of every player
        for player in self.players:
            Paint.draw_player(painter, player, defaults)
            Paint.draw_indicator_line(painter,
                                      player,
                                      self.get_player_pos(player),
                                      self.get_player_size(player),
                                      self.get_player_angle(player),
                                      self.get_player_direction_indicator_line_length(player),
                                      defaults)
            Paint.draw_shot(painter, player, defaults, self.get_shot(player))

    def player_shoot(self, player):
        tmp_line = QLineF(QPointF(player.pos), QPointF(player.pos + QPoint(1, 0)))
        tmp_line.setAngle(player.angle)
        tmp_line.setLength(player.shot.max_length)
        self.try_shot(player, QRect(player.pos, player.size).center(), tmp_line.p2())

    def get_viewable_map_area_size(self):
        """Returns size of viewable area on the map"""
        return self.map.view_size

    def get_viewable_map_area_pos(self):
        """Returns position of viewable area on the map"""
        return self.map.view_position

    def get_map_size(self):
        return self.map.size

    def set_viewable_map_area_size(self, size):
        if size.width() <= self.map.size.width() and size.height() <= self.map.size.height():
            self.map.view_size = size

    def set_viewable_map_area_position(self, position):
        self.map.view_position = position

    def get_obstacle_list(self):
        return self.map.obstacle_list

    def get_map_background(self):
        return self.map.background

    def try_shot(self, player, start_point, end_point):
        player.shot.set(start_point, end_point, self.map.outlines_list, self.map.size)

    @staticmethod
    def turn_player(player, direction):
        """Turns the player in direction. Returns False if direction was not specified correctly."""
        result = False

        if direction == 'left':
            player.angle += player.turn_speed
            result = True
        elif direction == 'right':
            player.angle -= player.turn_speed
            result = True

        if player.angle >= 360:
            player.angle -= 360
        elif player.angle < 0:
            player.angle += 360

        return result

    @staticmethod
    def get_shot(player):
        """Returns a list of lines which represent the shot the given player is currently firing.
           Returns an empty list if no shot is fired."""
        shot = player.shot.get()
        if not shot:
            # No shot is fired
            return []
        else:
            return shot

    def get_shot_intersection_with_player(self, victim, shooter):
        outlines = victim.outlines()
        shot = self.get_shot(shooter)

        for section in shot:
            for outline in outlines:
                intersection = QPointF()
                section.intersect(outline, intersection)

                # Check if intersection point is on the line or not
                if section.intersect(outline, intersection) == 1:
                    # Both lines cross each other withing start/end point
                    return True
        return False

    @staticmethod
    def get_shot_maximum_length(player):
        return player.shot.max_length

    @staticmethod
    def get_player_pos(player):
        return player.pos

    @staticmethod
    def get_player_size(player):
        return player.size

    @staticmethod
    def get_player_direction_indicator_line_length(player):
        return player.indi_line_length

    @staticmethod
    def get_player_angle(player):
        return player.angle

    @staticmethod
    def hit_action(victim, shooter):
        print(str(victim) + ' was hit by ' + str(shooter))
