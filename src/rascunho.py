from lugo4py import Lugo, GameSnapshotReader, SPECS, Bot, Mapper, geo
from settings import get_my_expected_position


TEAM_HOME = Lugo.Team.Side.HOME
TEAM_AWAY = Lugo.Team.Side.AWAY


class MyBot(Bot):
    def __init__(self, side: Lugo.Team.Side, number: int, init_position: Lugo.Point, mapper: Mapper):
        self.side = side
        self.number = number
        self.mapper = mapper
        self.init_position = init_position

    def on_disputing(self, order_set, snapshot):
        try:
            reader, me = self.make_reader(snapshot)
            ball_position = snapshot.get_ball().get_position()

            ball_region = self.mapper.get_region_from_point(ball_position)
            my_region = self.mapper.get_region_from_point(me.get_position())

            # By default, return to tactic position
            move_destination = get_my_expected_position(reader, self.mapper, self.number)
            order_set.set_debug_message("returning to my position")

            # If the ball is at most 2 blocks away, move toward it
            if self.should_i_catch_the_ball(reader, me):
                move_destination = ball_position
                order_set.set_debug_message("trying to catch the ball")

            move_order = reader.make_order_move_max_speed(me.get_position(), move_destination)
            catch_order = reader.make_order_catch()

            order_set.set_orders_list([move_order, catch_order])
            return order_set
        except Exception as e:
            print(f'did not play this turn: {e}')

    def on_defending(self, order_set, snapshot):
        try:
            reader, me = self.make_reader(snapshot)
            ball_position = snapshot.get_ball().get_position()

            ball_region = self.mapper.get_region_from_point(ball_position)
            my_region = self.mapper.get_region_from_point(me.get_position())

            # Default: return to tactic position
            move_destination = get_my_expected_position(reader, self.mapper, self.number)
            order_set.set_debug_message("returning to my position")

            if self.should_i_catch_the_ball(reader, me):
                move_destination = ball_position
                order_set.set_debug_message("trying to catch the ball")

            move_order = reader.make_order_move_max_speed(me.get_position(), move_destination)
            catch_order = reader.make_order_catch()

            order_set.set_orders_list([move_order, catch_order])
            return order_set
        except Exception as e:
            print(f'did not play this turn: {e}')

    def on_holding(self, order_set, snapshot):
        try:
            reader, me = self.make_reader(snapshot)
            my_goal_center = self.mapper.get_region_from_point(reader.get_opponent_goal().get_center())
            current_region = self.mapper.get_region_from_point(me.get_position())

            if self.is_i_near(current_region, my_goal_center, 0):
                my_order = reader.make_order_kick_max_speed(snapshot.get_ball(), reader.get_opponent_goal().get_center())
            else:
                close_opponents = self.nearest_players(
                    reader.get_opponent_team().get_players_list(),
                    me.get_position(),
                    3, [1]
                )
                obstacles = self.find_obstacles(
                    me.get_position(),
                    reader.get_opponent_goal().get_center(),
                    [opponent.get_position() for opponent in close_opponents],
                    SPECS.PLAYER_SIZE * 3
                )

                if obstacles and geo.distance_between_points(obstacles[0], me.get_position()) < SPECS.PLAYER_SIZE * 5:
                    close_mate = self.nearest_players(
                        reader.get_my_team().get_players_list(),
                        me.get_position(),
                        3, [1, self.number]
                    )
                    best_pass_player = self.find_best_pass(close_mate, me.get_position(), reader)
                    my_order = reader.make_order_kick_max_speed(reader.get_ball(), best_pass_player.get_position())
                else:
                    my_order = reader.make_order_move_max_speed(me.get_position(), reader.get_opponent_goal().get_center())

            order_set.set_debug_message("attack!")
            order_set.set_orders_list([my_order])
            return order_set
        except Exception as e:
            print(f'did not play this turn: {e}')

    def on_supporting(self, order_set, snapshot):
        try:
            reader, me = self.make_reader(snapshot)
            ball_position = snapshot.get_ball().get_position()

            move_destination = get_my_expected_position(reader, self.mapper, self.number)
            order_set.set_debug_message("returning to my position")

            if reader.get_ball().get_holder().get_number() == 1 and self.number == 2:
                move_destination = get_my_expected_position(reader, self.mapper, self.number)
                my_order = reader.make_order_move_max_speed(me.get_position(), move_destination)
                order_set.set_debug_message("assisting the goalkeeper")
                order_set.set_orders_list([my_order])
                return order_set

            close_players = self.nearest_players(reader.get_my_team().get_players_list(), ball_position, 3,
                                                 [1, snapshot.get_ball().get_holder().get_number()])

            if any(info['number'] == self.number for info in close_players):
                dist_to_mate = geo.distance_between_points(me.get_position(), ball_position)
                if dist_to_mate > SPECS.PLAYER_SIZE * 4:
                    move_destination = ball_position
                else:
                    move_destination = reader.get_opponent_goal().get_center()

            move_order = reader.make_order_move_max_speed(me.get_position(), move_destination)
            catch_order = reader.make_order_catch()

            order_set.set_orders_list([move_order, catch_order])
            return order_set
        except Exception as e:
            print(f'did not play this turn: {e}')

    def as_goalkeeper(self, order_set, snapshot, state):
        try:
            reader, me = self.make_reader(snapshot)
            position = reader.get_ball().get_position()
            if state != Lugo.PLAYER_STATE.DISPUTING_THE_BALL:
                position = reader.get_my_goal().get_center()

            if state == Lugo.PLAYER_STATE.HOLDING_THE_BALL:
                position = reader.get_player(self.side, 2).get_position()
                if snapshot.get_turns_ball_in_goal_zone() > SPECS.BALL_TIME_IN_GOAL_ZONE * 0.80:
                    order_set.set_debug_message("returning the ball")
                    kick = reader.make_order_kick_max_speed(reader.get_ball(), position)
                    order_set.set_orders_list([kick])
                    return order_set

            my_order = reader.make_order_move_max_speed(me.get_position(), position)
            order_set.set_debug_message("supporting")
            order_set.set_orders_list([my_order, reader.make_order_catch()])
            return order_set
        except Exception as e:
            print(f'did not play this turn: {e}')

    def getting_ready(self, snapshot):
        pass  # Empty function for setup when score changes or before the game starts

    def is_i_near(self, my_position, target_position, min_dist):
        col_dist = my_position.get_col() - target_position.get_col()
        row_dist = my_position.get_row() - target_position.get_row()
        return (col_dist**2 + row_dist**2) ** 0.5 <= min_dist

    def make_reader(self, snapshot):
        reader = GameSnapshotReader(snapshot, self.side)
        me = reader.get_player(self.side, self.number)
        if not me:
            raise Exception("did not find myself in the game")
        return reader, me

    def should_i_catch_the_ball(self, reader, me):
        my_distance = geo.distance_between_points(me.get_position(), reader.get_ball().get_position())
        closer_player = 0
        for player in reader.get_my_team().get_players_list():
            if player.get_number() == me.get_number() or player.get_number() == 1:
                continue
            player_dist = geo.distance_between_points(player.get_position(), reader.get_ball().get_position())
            if player_dist < my_distance:
                closer_player += 1
                if closer_player >= 2:
                    return False
        return True

    def nearest_players(self, players, point_target, count, ignore):
        players_dist = []
        for player in players:
            if player.get_number() in ignore:
                continue
            players_dist.append({
                'dist': geo.distance_between_points(player.get_position(), point_target),
                'number': player.get_number(),
                'player': player,
            })
        players_dist.sort(key=lambda x: x['dist'])
        return players_dist[:count]

    def find_obstacles(self, origin, target, elements, min_acceptable_dist):
        obstacles = []
        for element in elements:
            dist, between = self.get_distance(
                element.get_x(), element.get_y(),
                origin.get_x(), origin.get_y(),
                target.get_x(), target.get_y()
            )
            if between and dist <= min_acceptable_dist:
                obstacles.append(element)
        return obstacles

    def get_distance(self, obstacle_x, obstacle_y, x1, y1, x2, y2):
        A = obstacle_x - x1
        B = obstacle_y - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D
        param = -1 if len_sq == 0 else dot / len_sq

        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D

        dx = obstacle_x - xx
        dy = obstacle_y - yy
        return {
            'dist': (dx**2 + dy**2) ** 0.5,
            'between': param >= 0 and param <= 1
        }

    def find_best_pass(self, close_mates, my_position, reader):
        candidates = []
        opponents = [p.get_position() for p in reader.get_opponent_team().get_players_list()]
        goal_center = reader.get_opponent_goal().get_center()

        for candidate in close_mates:
            if candidate['dist'] > SPECS.PLAYER_SIZE * 8:
                continue

            obstacles = self.find_obstacles(my_position, candidate['player'].get_position(), opponents, SPECS.PLAYER_SIZE * 2)
            candidates_obstacles_to_kick = self.find_obstacles(candidate['player'].get_position(), goal_center, opponents, SPECS.PLAYER_SIZE * 2)

            dist_to_goal = geo.distance_between_points(candidate['player'].get_position(), goal_center)

            score = 0
            score -= len(obstacles) * 10
            score -= (candidate['dist'] / SPECS.PLAYER_SIZE) / 2
            score -= (dist_to_goal / SPECS.PLAYER_SIZE) * 2

            if not candidates_obstacles_to_kick:
                score += 30

            candidates.append({
                'score': score,
                'player': candidate['player']
            })

        if not candidates:
            return None

        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[0]['player']
