from player import Player
from map import Map


class Game():
    gameCycleInterval = 10  # Time in ms
    
    def __init__(self, list_of_key_setups):
        self.map = Map('debug')
        self.players = []
        try:
            for player_id in range(len(self.map.player_information)):
                # Create as many players in the game as there are objects of players in the map
                self.players.append(Player(self.map.player_information[player_id],
                                           list_of_key_setups[player_id],
                                           player_id))
        except IndexError:
            print('Not enough key_setups defined for so many players')

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
        for player in self.players:
            action = 'NONE'

            # Go through every key in the players key_dict and find the action associated with the key
            for player_key in player.key_dict:
                if player.key_dict[player_key] == key:
                    action = player_key

            # Perform the action if there is any
            if action == 'move_up':
                self.move_player(player, 'up')
            elif action == 'move_down':
                self.move_player(player, 'down')
            elif action == 'move_left':
                self.move_player(player, 'left')
            elif action == 'move_right':
                self.move_player(player, 'right')
            elif action == 'turn_left':
                self.turn_player(player, 'left')
            elif action == 'turn_right':
                self.turn_player(player, 'right')
            elif action == 'NONE':
                print('No event triggered in player ' + str(player))
            else:
                print('Unknown event (' + action + ') in player ' + str(player))


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

    @staticmethod
    def get_shot(player):
        """Returns a list of lines which represent the shot the given player is currently firing.
           Returns an empty list if no shot is fired."""
        if not player.shot.timer.isActive():
            # Timer is not active. This means there is no shot fired.
            return []

        # Return the list of lines
        return player.shot.current_shot

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

    def try_shot(self, player, start_point, end_point):
        player.shot.try_shot(start_point, end_point, self.map.outlines_list, self.map.size)