# building off of chess engine project from high school
class position:
    def __init__(self, p: dict, t: bool, c: list, e: str, h: int):
        """
        piece position (pieces): dictionary
        to move (to_move): bool, True if white to move, False if black to move
        Castling rights:

        white castling short (white_castle_short): bool
        white castling long (white_castle_long): bool
        black castling short (black_castle_short): bool
        black castling long (black_castle_long): bool

        en-passant square (ep_square): str
        50-move timer (half_move): int, evaluation automatically goes to 0.0 if this goes above 100
        """
        self.pieces = p
        self.to_move = t
        self.white_castle_short = c[0]
        self.white_castle_long = c[1]
        self.black_castle_short = c[2]
        self.black_castle_long = c[3]
        self.ep_square = e
        self.half_move = h
def check_square(square: str) -> bool:
    if len(square) != 2:
        return False
    return square[0] in "abcdefgh" and square[1] in "36"
def convert(fen: str) -> position:
    splitter = fen.split()
    assert len(splitter) == 6, "FEN has too few or too many elements"
    assert len(splitter[0].split("/")) == 8, "FEN element 1 has too few or too many elements"
    for part in splitter[0].split("/"):
        for letter in part:
            assert letter in "abcdefgh12345678", "FEN element 1 invalid"
    
    assert len(splitter[1]) == 1 and splitter[1] in "wb", "FEN element 2 invalid"
    assert splitter[2] == "-" or (element in ["K, Q, k, q"] for element in splitter[2]), "FEN element 3 invalid"
    assert splitter[3] == "-" or check_square(splitter[3]), "FEN element 4 invalid"
    assert len(splitter[4]) == 1 and int(splitter[4]) >= 0, "FEN element 5 invalid"
    assert len(splitter[5]) == 1 and int(splitter[5]) > 0, "FEN element 6 invalid"

    pieces = {
        "white_pawns": list(),
        "black_pawns": list(),
        "white_knights": list(),
        "black_knights": list(),
        "white_bishops": list(),
        "black_bishops": list(),
        "white_rooks": list(),
        "black_rooks": list(),
        "white_queen": "",
        "black_queen": "",
        "white_king": "",
        "black_king": "",
    }
    castling = [False] * 4
    row = 8
    column = 1
    for char in splitter[0]:
        #piece positions
        if type(char) == int:
            column += char
        else:
            match char:
                case _:
                    pass
        if column == 9:
            column = 1
            row -= 1
    for char in splitter[2]:
        #castling rights
        pass

def interpret(square: str) -> dict:
    return {"x": ord(square[0]) - 96, "y": square[1]}

def evaluate() -> float:
    
    return 0.0