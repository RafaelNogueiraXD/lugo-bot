import traceback
from abc import ABC
from typing import List

import lugo4py
from settings import get_my_expected_position


class MyBot(lugo4py.Bot, ABC):
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position
            # print("ta na disputa")
            move_order = self.determine_catchers(inspector, ball_position) # determina quem pega a bola

            catch_order = inspector.make_order_catch() # realiza a ação

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position
            # print("defendendo! ")

            #pegando os jogadores mais proximos       
      

            move_order = self.determine_catchers(inspector, ball_position,2)
            # we can ALWAYS try to catch the ball
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            my_order = None
            kick_order= None
            opponent_goal = self.mapper.get_attack_goal()
            me = inspector.get_me()
            my_team = inspector.get_my_team_players()

            free_players = self.get_free_allies(inspector, 500)
            closest_to_goal = self.get_closest_players(opponent_goal.get_center(), my_team)
            goal_region = self.mapper.get_region_from_point(opponent_goal.get_center())
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)
            dist_to_goal = lugo4py.distance_between_points(me.position, opponent_goal.get_center())


            if dist_to_goal <= 2200:
                
                if me.position.y > 5000:

                    my_order = inspector.make_order_kick_max_speed(opponent_goal.get_bottom_pole())
                else:
                    my_order = inspector.make_order_kick_max_speed(opponent_goal.get_top_pole())
            # 
            if my_order is None:
                my_order = inspector.make_order_move_max_speed(opponent_goal.get_center())

            # for ally in closest_to_goal:
            #     if ally in free_players and (ally.number != me.number) and (lugo4py.distance_between_points(me.position,opponent_goal.get_center()) > lugo4py.distance_between_points(ally.position, opponent_goal.get_center())):
            #         kick_order = inspector.make_order_kick(ally.position, 200)
            #         print(f"passando a bola para {ally.number} na posicao {ally.position}")
            #         # break
            #         return [kick_order]
            # self.make_pass(inspector)
            # for ally in clo
            
            return [my_order]

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
    
        try:
            # ball_holder_position = inspector.get_ball().position
            ball_position = inspector.get_ball().position

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            # ball_holder_region = self.mapper.get_region_from_point(ball_holder_position)
            # my_region = self.mapper.get_region_from_point(inspector.get_me().position)

            # if self.is_near(ball_holder_region, my_region):
            #     move_dest = ball_holder_position
            # else:
            #     move_dest = get_my_expected_position(inspector, self.mapper, self.number)
            move_order = self.determine_catchers(inspector, ball_position,1)

            # move_order = inspector.make_order_move_max_speed(move_dest)
            return [move_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            position = inspector.get_ball().position

            if state != lugo4py.PLAYER_STATE.DISPUTING_THE_BALL:
                position = self.mapper.get_attack_goal().get_center()

            my_order = inspector.make_order_move_max_speed(position)

            return [my_order, inspector.make_order_catch()]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance


    def determine_catchers(self,inspector, ball_position,n_catchers=2):
        me = inspector.get_me()  
        my_team = inspector.get_my_team_players()
        closest_players = self.get_closest_players(ball_position, my_team)

        catchers = closest_players[:n_catchers]

        if me in catchers:
            move_order = inspector.make_order_move_max_speed(ball_position)
        else:
            move_order = inspector.make_order_move_max_speed(get_my_expected_position(inspector, self.mapper, self.number))
        
        return move_order


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
    
    def make_pass(self, inspector: lugo4py.GameSnapshotInspector) -> lugo4py.Order:
        """
        Função para realizar um passe para o jogador aliado mais bem posicionado.
        O passe é feito para o jogador mais próximo do gol adversário e que esteja livre de adversários.
        """
        try:
            me = inspector.get_me()
            opponent_goal = self.mapper.get_attack_goal()
            my_team = inspector.get_my_team_players()

            # Pega os jogadores livres
            free_players = self.get_free_allies(inspector)

            if not free_players:
                # Se não houver jogadores livres, mova-se em direção ao gol
                return inspector.make_order_move_max_speed(opponent_goal.get_center())

            # Encontra o jogador mais próximo do gol adversário
            closest_to_goal = self.get_closest_players(opponent_goal.get_center(), free_players)

            # Se o jogador mais próximo do gol não for o próprio jogador, passe a bola
            for ally in closest_to_goal:
                if ally.number != me.number:
                    # Cria a ordem de passe para o aliado mais próximo do gol
                    pass_order = inspector.make_order_kick(ally.position, 200)  # Potência de 200 para o passe
                    print(f"Passando a bola para o jogador {ally.number}")
                    return pass_order

            # Se não houver uma boa opção de passe, mova-se em direção ao gol
            return inspector.make_order_move_max_speed(opponent_goal.get_center())

        except Exception as e:
            print(f"Erro ao tentar passar a bola: {e}")
            traceback.print_exc()
