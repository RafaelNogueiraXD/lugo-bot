import lugo4py
import lugo4py.mapper as mapper

# MAPPER_COLS and MAPPER_ROWS define the number of regions on the field.
# great values leads to more precision
# Use this tool to help you to decide about it https://github.com/mauriciorobertodev/strategy-creator-lugo-bots
MAPPER_COLS = 20
MAPPER_ROWS = 9

# Example how to create your custom initial positions
PLAYER_INITIAL_POSITIONS = {
     1: {'Col': 0, 'Row': 4},
     2: {'Col': 3, 'Row': 4},
     3: {'Col': 4, 'Row': 6},
     4: {'Col': 4, 'Row': 2},
     5: {'Col': 6, 'Row': 7},
     6: {'Col': 6, 'Row': 5},
     7: {'Col': 6, 'Row': 3},
     8: {'Col': 6, 'Row': 1},
     9: {'Col': 9, 'Row': 6},
     10: {'Col': 8, 'Row': 4},
     11: {'Col': 9, 'Row': 2},
}

#inspector = informações do jogo

def get_my_expected_position(inspector: lugo4py.GameSnapshotInspector, my_mapper: mapper.Mapper, number: int):
    mapper_cols = MAPPER_COLS

    player_tactic_positions = {
        'EXTREME_DEFENSIVE':{
            2: {'Col': 1, 'Row': 7},
            3: {'Col': 2, 'Row': 3},
            4: {'Col': 2, 'Row': 4},
            5: {'Col': 2, 'Row': 6},
            6: {'Col': 3, 'Row': 1},
            7: {'Col': 5, 'Row': 3},
            8: {'Col': 2, 'Row': 5},
            9: {'Col': 5, 'Row': 7},
            10: {'Col': 5, 'Row': 5},
            11: {'Col': 5, 'Row': 1},
        },
        'DEFENSIVE': {
            2: {'Col': 2, 'Row': 2},
            3: {'Col': 3, 'Row': 3},
            4: {'Col': 3, 'Row': 4},
            5: {'Col': 2, 'Row': 5},
            6: {'Col': 5, 'Row': 1},
            7: {'Col': 5, 'Row': 3},
            8: {'Col': 5, 'Row': 5},
            9: {'Col': 5, 'Row': 7},
            10: {'Col': 8, 'Row': 6},
            11: {'Col': 8, 'Row': 2},
        },
        'NORMAL': {
            2: {'Col': 2, 'Row': 1},
            3: {'Col': 4, 'Row': 2},
            4: {'Col': 4, 'Row': 3},
            5: {'Col': 2, 'Row': 4},
            6: {'Col': 6, 'Row': 1},
            7: {'Col': 8, 'Row': 2},
            8: {'Col': 8, 'Row': 3},
            9: {'Col': 6, 'Row': 4},
            10: {'Col': 7, 'Row': 4},
            11: {'Col': 7, 'Row': 1},
        },
        'OFFENSIVE': {
            2: {'Col': 7, 'Row': 3},
            3: {'Col': 12, 'Row': 3},
            4: {'Col': 12, 'Row': 5},
            5: {'Col': 7, 'Row': 5},
            6: {'Col': 7, 'Row': 1},
            7: {'Col': 17, 'Row': 4},
            8: {'Col': 8, 'Row': 4},
            9: {'Col': 14, 'Row': 6},
            10: {'Col': 17, 'Row': 5},
            11: {'Col': 17, 'Row': 3},
        },
        'EXTREME_OFFENSIVE': {
            2: {'Col': 13, 'Row': 2},
            3: {'Col': 12, 'Row': 3},
            4: {'Col': 13, 'Row': 6},
            5: {'Col': 12, 'Row': 5},
            6: {'Col': 15, 'Row': 1},
            7: {'Col': 15, 'Row': 7},
            8: {'Col': 17, 'Row': 6},
            9: {'Col': 17, 'Row': 5},
            10: {'Col': 17, 'Row': 4},
            11: {'Col': 17, 'Row': 2},
        },

    }

    ball_region = my_mapper.get_region_from_point(inspector.get_ball().position)
    field_fifth = mapper_cols / 5
    ball_cols = ball_region.get_col()

    if ball_cols < field_fifth:
        team_state = "EXTREME_DEFENSIVE"
    elif ball_cols < field_fifth * 2:
        team_state = "DEFENSIVE"
    elif ball_cols < field_fifth * 3:
        team_state = "NORMAL"
    elif ball_cols < field_fifth * 4:
        team_state = "OFFENSIVE"
    else:
        team_state = "EXTREME_OFFENSIVE"

    expected_region = my_mapper.get_region(player_tactic_positions[team_state][number]['Col'],
                                           player_tactic_positions[team_state][number]['Row'])
    return expected_region.get_center()

#def come_back()
        #'COME_BACK':{
         #   team[0]:{'Col': 2, 'Row': 6},
          #  team[1]:{'Col': 3, 'Row': 5},
           # team[2]:{'Col': 3, 'Row': 4},
            #team[3]:{'Col': 2, 'Row': 3}
        #}