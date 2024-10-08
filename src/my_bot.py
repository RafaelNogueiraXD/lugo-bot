import traceback
from abc import ABC
from typing import List
import math

import lugo4py
from settings import get_my_expected_position


from botMath import *

class MyBot(lugo4py.Bot, ABC):
    
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position
            
            move_order = self.determine_catchers(inspector, ball_position) # determina quem pega a bola

            catch_order = inspector.make_order_catch() # realiza a ação

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position

            move_order = self.determine_catchers(inspector, ball_position,2)
            # we can ALWAYS try to catch the ball
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            my_order = None
            kick_order= None
            opponent_goal = self.mapper.get_attack_goal()
            ball_position = inspector.get_ball().position
            me = inspector.get_me()
            my_team = inspector.get_my_team_players()
            enemy_team = inspector.get_opponent_team()

            dist_to_goal = lugo4py.distance_between_points(me.position, opponent_goal.get_center())
    
            close_enemys = self.nearest_players(
                enemy_team.players,
                me.position,
                3, # pega tres players mais proximos do time inimigo
                [1] # ignora goleiro
            )
            obstacles = self.find_obstacles(
                me.position,
                opponent_goal.get_center(),
                [opponent['player'].position for opponent in close_enemys],
                lugo4py.PLAYER_SIZE * 3
            )
            print("obstaculos = ", obstacles)

            print("inimigos proximos sao: ",end=" ")
            for enemy in close_enemys:
                print(enemy['number'],end=" " )
            print()

            if dist_to_goal <= 2200:
                my_order = self.kick_to_goal(me, inspector, opponent_goal)
            elif obstacles and lugo4py.distance_between_points(obstacles[0], me.position) < lugo4py.PLAYER_SIZE * 8:
                
                close_allies = self.nearest_players(
                    my_team,
                    me.position,
                    3, # pega tres players mais proximos do proprio time
                    [1, self.number] # ignora goleiro e eu mesmo
                )
                # my_order = self.drible(close_enemys=close_enemys, me=me, inspector=inspector)
                # if lugo4py.distance_between_points(close_enemys[0]['player'].position, me.position) < lugo4py.PLAYER_SIZE + 300:
                #     if close_enemys[0].position.y > me.position.y: 
                #         print("drible")
                #         return [inspector.make_order_move_max_speed(lugo4py.Point(me.position.x,0))]
                #     else:
                #         return [inspector.make_order_move_max_speed(lugo4py.Point(me.position.x,10000))]
                    
                print("aliados proximos sao: ",end=" ")
                for allies in close_allies:
                    print(allies['number'] ,end=" ")
                print()
                best_pass_player = self.find_best_pass(close_allies, me.position, inspector)
                if best_pass_player != None:
                    my_order = inspector.make_order_kick_max_speed(best_pass_player.position)
                else:
                    my_order = inspector.make_order_move_max_speed(opponent_goal.get_center())
                    # my_order = self.drible(close_enemys=close_enemys, me=me, inspector=inspector)
            else: 
                print("preciso correr e chutar!")
                my_order = inspector.make_order_move_max_speed(opponent_goal.get_center())


            
            #volta 4 jogadores para a defesa se a bola esta na zona 4 ou 5
            #if ball_position > self.zona3:
            #    self.defense_comeback(inspector, ball_position)

            return [my_order]

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            ball_position = inspector.get_ball().position
            me = inspector.get_me()
            
            # Determinar o destino inicial do movimento
            move_destination = get_my_expected_position(inspector, self.mapper, self.number)

            # Se o jogador com a bola for o número 1 e você for o número 2
            if inspector.get_ball().holder.number == 1 and self.number == 2: 
                move_destination = get_my_expected_position(inspector, self.mapper, self.number)

                # Verifica se o destino do movimento é igual à posição atual
                if move_destination != me.position:
                    my_order = inspector.make_order_move_max_speed(move_destination)
                    return [my_order]
                else:
                    print("Destino é igual à posição atual, sem movimento necessário.")
                    return []

            # Encontrar jogadores mais próximos da bola
            close_players = self.nearest_players(
                inspector.get_my_team_players(),
                ball_position,
                3,
                [1, inspector.get_ball().holder.position]
            )
            
            print("tenho que acompanhar", close_players)
            
            # Se o jogador atual estiver entre os mais próximos
            if any(player['number'] == self.number for player in close_players):
                dist_to_mate = lugo4py.distance_between_points(me.position, ball_position)
                
                # Decidir o destino com base na distância
                if dist_to_mate > lugo4py.PLAYER_SIZE * 4:
                    move_destination = ball_position
                else: 
                    opponent_goal = self.mapper.get_attack_goal()
                    goal_center = opponent_goal.get_center()
                    move_destination = goal_center

            # Posicionar aliados ao redor do jogador com a bola
            move_order = self.position_allies_around_holder(inspector)
            
            # Se não houver ordem de posicionamento, faça o movimento
            if move_order is None:
                if move_destination != me.position:
                    move_order = inspector.make_order_move_max_speed(move_destination)
                else:
                    move_order = inspector.make_order_move_max_speed(lugo4py.Point(me.position.x+1,me.position.y+1))

            # Ordem para pegar a bola
            catch_order = inspector.make_order_catch()

            # Retornar as ordens de movimento e captura
            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            return []

        except Exception as e:
            traceback.print_exc()
    # def tabelinha():
    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            position = inspector.get_ball().position

            if state != lugo4py.PLAYER_STATE.DISPUTING_THE_BALL:
                print(" o goleiro esta indo na !")

                position = self.mapper.get_attack_goal().get_center()

            if state == lugo4py.PLAYER_STATE.HOLDING_THE_BALL: 
                me = inspector.get_me()
                my_team = inspector.get_my_team_players()
                print(" o goleiro esta com a bola !")
                close_allies = self.nearest_players(
                my_team,
                me.position,
                3, # pega tres players mais proximos do proprio time
                [1] # ignora goleiro e eu mesmo
                )
                best_pass_player = None
                best_pass_player = self.find_best_pass(close_allies, me.position, inspector)
                if best_pass_player is None: 
                    print("ENTROU")
                    if self.best_direction_goalkeeper_kick_y(inspector):
                        if self.side == 0: 
                            position_pass = lugo4py.Point(3000, lugo4py.MAX_Y_COORDINATE)
                        else: 
                            position_pass = lugo4py.Point(17000, lugo4py.MAX_Y_COORDINATE)
                    else:
                        if self.side == 0: 
                            position_pass = lugo4py.Point(3000,0)
                        else: 
                            position_pass = lugo4py.Point(17000,0)
                else:
                    position_pass = best_pass_player.position
            
                print(f"chute na direção x = {position_pass.x} y = {position_pass.y}")
                my_order = inspector.make_order_kick_max_speed(position_pass)
                return [my_order]
            my_order = inspector.make_order_move_max_speed(position)

            return [my_order, inspector.make_order_catch()]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    # def drible(self,close_enemys, me, inspector : lugo4py.GameSnapshotInspector):
    #     if lugo4py.distance_between_points(close_enemys[0]['player'].position, me.position) < lugo4py.PLAYER_SIZE + 300:
    #         if close_enemys[0].position.y > me.position.y: 
    #             print("drible")
    #             return [inspector.make_order_move_max_speed(lugo4py.Point(self.mapper.get_attack_goal()._center.x, 0))]
    #         else:
    #             return [inspector.make_order_move_max_speed(lugo4py.Point(self.mapper.get_attack_goal()._center.x,10000))]


    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance


    def determine_catchers(self,inspector: lugo4py.GameSnapshotInspector, ball_position,n_catchers=2):
        me = inspector.get_me()  
        my_team = inspector.get_my_team_players()
        closest_players = self.get_closest_players(ball_position, my_team)

        catchers = closest_players[:n_catchers]

        if me in catchers:
            move_order = inspector.make_order_move_max_speed(ball_position)
        else:
            me = inspector.get_me()
            if lugo4py.distance_between_points(get_my_expected_position(inspector, self.mapper, self.number), me.position) > lugo4py.PLAYER_SIZE:
                move_order = inspector.make_order_move_max_speed(get_my_expected_position(inspector, self.mapper, self.number))
            else: 
                move_order = inspector.make_order_move(lugo4py.Point(me.position.x+1,me.position.y+1), 50)
        
        return move_order

    def kick_to_goal(self, me, inspector: lugo4py.GameSnapshotInspector, opponent_goal):
        goleiro = self.find_a_player(1, inspector.get_opponent_players())
        if goleiro.position.y > 5000:
            my_order = inspector.make_order_kick_max_speed(opponent_goal.get_bottom_pole())
        else:
            my_order = inspector.make_order_kick_max_speed(opponent_goal.get_top_pole())
        return my_order
    def get_closest_players(self, point, player_list):
        
        def sortkey(player):
            return lugo4py.geo.distance_between_points(point, player.position)

        closest_players = sorted(player_list, key=sortkey)
        return closest_players
    
    def get_free_allies(self, inspector: lugo4py.GameSnapshotInspector, dist = lugo4py.specs.PLAYER_SIZE):
        my_team = inspector.get_my_team_players()
        opponnent_team = inspector.get_opponent_players()
        free_players = []
        for ally in my_team:
            is_free = True
            
            for opponent in opponnent_team:
                dist_to_opponent  = lugo4py.distance_between_points(ally.position, opponent.position)
                if dist_to_opponent <= dist:
                    is_free = False
            
            if is_free == True:
                free_players.append(ally)

        return free_players
       
    def nearest_players(self, players, point_target, count, ignore):
        players_dist = []
        for player in players:
            if player.number in ignore: #lista de players a ignorar (goleiro, me e etc)
                continue
            players_dist.append({
                'dist': lugo4py.distance_between_points(player.position, point_target),
                'number': player.number,
                'player': player,
            })
        players_dist.sort(key=lambda x: x['dist'])
        return players_dist[:count]
    
    def find_obstacles(self, position_origin, target_path, elements, min_acceptable_dist):
        obstacles = []
        for element in elements:
                distance = get_distance(
                    element.x, element.y,
                    position_origin.x, position_origin.y,
                    target_path.x, target_path.y
                )
                if distance['between'] and distance['dist'] <= min_acceptable_dist:
                    obstacles.append(element)
        return obstacles
    
    def find_best_pass(self, close_teamates, my_position, inspector: lugo4py.GameSnapshotInspector):
        candidates = []
        opponents = [p.position for p in inspector.get_opponent_team().players]
        opponent_goal = self.mapper.get_attack_goal()
        goal_center = opponent_goal.get_center()
        me = inspector.get_me()

        for candidate in close_teamates:
            if candidate['dist'] > lugo4py.PLAYER_SIZE * 8:
                continue
            
            obstacles = self.find_obstacles(
                my_position,
                candidate['player'].position,
                opponents,
                lugo4py.PLAYER_SIZE * 5
            )
            candidates_obstacles_to_kick  = self.find_obstacles(
                candidate['player'].position,
                goal_center,
                opponents,
                lugo4py.PLAYER_SIZE * 5
            )
            dist_to_goal = lugo4py.distance_between_points(
                candidate['player'].position,
                goal_center
            )
            score = 0
            score -= len(obstacles) * 10
            score -= (candidate['dist'] / lugo4py.PLAYER_SIZE) / 2
            score -= (dist_to_goal / lugo4py.PLAYER_SIZE) * 2
            if not candidates_obstacles_to_kick:
                score += 30
            disqualified = False
            if lugo4py.distance_between_points(me.position, candidate['player'].position) > lugo4py.PLAYER_SIZE * 1.5: 
                for opponent_distance in opponents: 
                    if lugo4py.distance_between_points(candidate['player'].position, opponent_distance) < lugo4py.PLAYER_SIZE * 2.5:
                        disqualified = True

                if disqualified is False:
                    candidates.append({
                        'score': score,
                        'player': candidate['player']
                    })

        if not candidates:
            return None
        
        
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[0]['player']
    
    def position_allies_around_holder(self, inspector: lugo4py.GameSnapshotInspector):
        angle = {
            "upper_diagonal" : 45,
            "lower_diagonal": 315,
            "behind" : 180
        }
        if self.side == 1: 
            angle['upper_diagonal'] = 135
            angle['lower_diagonal'] = 225
            angle['behind'] = 0
        ball_holder = inspector.get_ball().holder
        ball_holder_position = ball_holder.position

        # Distância que os aliados devem manter do portador da bola
        distance = lugo4py.PLAYER_SIZE * 5

        my_team = inspector.get_my_team_players()
        closest_allies = self.nearest_players(
            my_team, 
            ball_holder_position,
            3,
            ignore=[ball_holder.number]
        )

        positions = []

        new_position_upper = calculate_new_position(ball_holder_position, distance, angle['upper_diagonal'])
        positions.append({
            'player': closest_allies[0]['player'],
            'position': new_position_upper
        })
        new_position_lower = calculate_new_position(ball_holder_position, distance, angle['lower_diagonal'])
        positions.append({
            'player': closest_allies[1]['player'],
            'position': new_position_lower
        })
        new_position_behind = calculate_new_position(ball_holder_position, distance, angle['behind'])
        positions.append({
            'player': closest_allies[2]['player'],
            'position': new_position_behind
        })
        move_order = None
        me = inspector.get_me()
        for ally in positions:
            if self.number == ally['player'].number and ally['position']["x"] > 0 and ally['position']["y"] > 0:
                if lugo4py.distance_between_points(me.position, lugo4py.Point(ally['position']["x"],ally['position']["y"])) < lugo4py.PLAYER_SIZE:
                    move_order = inspector.make_order_move_max_speed(self.mapper.get_defense_goal()._center)
                else: 
                    move_order = inspector.make_order_move_max_speed(lugo4py.Point(ally['position']["x"],ally['position']["y"]))
                print(f" eu tenho que estar em : x = { ally['position'] } ,  y = { ally['position'] }")
                



        return move_order

    def four_furthest_allies(self, inspector, ball_position):
        my_team = inspector.get_my_team_players()
        furthest_allies = list(reversed(self.get_closest_players(ball_position, my_team)))
        return[furthest_allies[:4]]
    

    def best_direction_goalkeeper_kick_y(self, inspector: lugo4py.GameSnapshotInspector):
        enemy_team = inspector.get_opponent_players()
        counterUp = 0
        counterDown = 0
        for enemy in enemy_team:
            if enemy.position.y <= 5000:
                counterDown += 1
            else:
                counterUp += 1
        
        if counterDown > counterUp:
            return True
        else:
            return False
    def find_a_player(self, number, team):
        for player in team:
            if number == player.number:
                return player
