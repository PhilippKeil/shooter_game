from player import Player
from map import Map


class Game():
    gameCycleInterval = 10  # Time in ms
    
    def __init__(self):
        self.map = Map('debug')
        self.player_1 = Player(1, 1, 10, 10)

    def move_player(self, player, move_direction):
        """Tries to move the player. Returns True is it succeeded. False if player couldn't be moved"""
        new_player_pos = player.try_move(move_direction,
                                         self.player_1.move_speed,
                                         self.map.view_size,
                                         self.map.obstacle_list)
        if new_player_pos == player.pos:
            # Player wasn't moved
            return False
        else:
            # Player was moved
            player.force_move(new_player_pos)
            return True

    def turn_player(self, player, direction):
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

    def get_viewable_map_area(self):
        """Returns viewable map area"""
        return self.map.view_size

    def get_obstacle_list(self):
        return self.map.obstacle_list

    def get_shot(self, player):
        """Returns a list of lines which represent the shot the given player is currently firing.
           Returns an empty list if no shot is fired."""
        if not player.shot.timer.isActive():
            # Timer is not active. This means there is no shot fired.
            return []

        # Return the list of lines
        return player.shot.get_whole_shot(self.map.outlines_list)

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
    def try_shot(player, start_point, end_point):
        player.shot.try_shot(start_point, end_point)

    def change_viewable_map_area(self, size, frame_size):
        self.map.change_view_size(size.width(), size.height(), frame_size)