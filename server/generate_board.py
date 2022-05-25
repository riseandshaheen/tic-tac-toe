from math import sqrt,floor

#print board globals
TOP_LEFT = '╔'
TOP_RIGHT = '╗'
BOTTOM_LEFT = '╚'
BOTTOM_RIGHT = '╝'
VERTICAL = '║'
HORIZONTAL = '═'
VERTICAL_LEFT = '╠'
VERTICAL_RIGTH = '╣'
HORIZONTAL_TOP = '╦'
HORIZONTAL_BOTTOM = '╩'
CENTRAL = '╬'


def generate_board_pretty_str(board_state):
    pretty_board_str = "\n"

    board_size = floor(sqrt(len(board_state.keys())))
    print(type(board_size))
    print(board_size)

    top_line = f"{TOP_LEFT}{(board_size-1)*(HORIZONTAL+HORIZONTAL_TOP)}{HORIZONTAL+TOP_RIGHT}"
    separator_line = f"{VERTICAL_LEFT}{(HORIZONTAL+CENTRAL) * (board_size-1)}{HORIZONTAL + VERTICAL_RIGTH}"
    bottom_line = f"{BOTTOM_LEFT}{(board_size-1)*(HORIZONTAL+HORIZONTAL_BOTTOM)}{HORIZONTAL+BOTTOM_RIGHT}"

    pretty_board_str = top_line + '\n'
    first = True
    for line in range(0,board_size):
        if first:
            first = False
        else:
            pretty_board_str += separator_line + '\n'
        current_line = VERTICAL
        for row in range(0,board_size):
            current_line += f"{board_state[(line,row)]}{VERTICAL}"
        pretty_board_str += current_line + '\n'
    pretty_board_str += bottom_line + '\n'

    return pretty_board_str

