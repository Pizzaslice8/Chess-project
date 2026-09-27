# building off of chess engine project from high school
class piece:
    def __init__(self, identity: str | None):
        self.identity = identity
        self.color = 0
        if identity == identity.casefold():
            self.color = 1

class square:
    def __init__(self, row: int | None, column: int | None, occupier: piece | None):
        self.row = row
        self.column = column
        self.occupier = occupier
        
class position:
    def __init__(self, pos: list, color: bool, castle: list, ep: square | None, clock: int, fullmove: int):
        self.color = color
        self.white_castle_short = castle[0]
        self.white_castle_long = castle[1]
        self.black_castle_short = castle[2]
        self.black_castle_long = castle[3]
        self.en_passant = ep
        self.clock = clock
        self.fullmove = fullmove
        self.descr = pos


    

def convert(fen: str) -> position:
    row = 7
    column = 0
    color = True
    ep = square(None, None, None)
    castle = [False, False, False, False]
    output = list()
    splitter = fen.split()
    for i in range(8):
        output.append([None] * 8)
    for c in splitter[0]:
        try:
            column += int(c)
        except ValueError:
            if c == "/":
                row -= 1
                column = 0
            else:
                output[row][column] = square(row, column, piece(c))
                column += 1
    iterator = iter(splitter)
    next(iterator)
    castling = next(iterator)
    for char in castling:
        match char:
            case "K":
                castle[0] = True
            case "Q":
                castle[1] = True
            case "k":
                castle[2] = True
            case "q":
                castle[3] = True
    ep_square = next(iterator)
    if ep_square != "-":
        row_output = 0
        match ep_square[0]:
            case "b":
                row_output = 1
            case "c":
                row_output = 2
            case "d":
                row_output = 3
            case "e":
                row_output = 4
            case "f":
                row_output = 5
            case "g":
                row_output = 6
            case "h":
                row_output = 7
        ep = square(row_output, ep_square[1], None)    
    return position()
        

def evaluate(sq: square) -> float:
    
    return 0.0