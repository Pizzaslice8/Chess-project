# building off of chess engine project from high school
openings = {
    #0 halfmoves
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": (0.2, "e4"), #starting position
    #1 halfmoves
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": (0.2, "e5"), #1. e4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": (0.2, "Nf6"), #1. d4
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": (0.1, "e5"), #1. c4
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": (0.1, "Nf6"), #1. Nf3
    #2 halfmoves, 1. e4
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.2, "Nf3"), #1. e4 e5
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.3, "Nf3"), #1. e4 c5
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.4, "d4"), #1. e4 e6
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.3, "d4"), #1. e4 c6
    #2 halfmoves, 1. d4
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2": (0.2, "c4"), #1. d4 Nf6
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2": (0.3, "c4") #1. d4 d5
    #more to come
}
def interpret(square: str) -> tuple:
    return (ord(square[0]) - 96, int(square[1]))
def compress(x: int, y: int) -> str:
    return str(chr(x + 96)) + str(y)
def translate(square: str, x_move: int, y_move: int) -> str:
    return compress(interpret(square)[0] + x_move, interpret(square)[1] + y_move)
def piece_color(piece: str) -> bool:
    #White: True, black: False
    return piece != piece.casefold()
class position:
    def __init__(self, p: dict, t: bool, c: tuple, e: str, h: int):
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
        self.ep_square = None if e == "-" else e
        self.half_move = h
    def search(self, square: str) -> str | None:
        for letter in "PNBRQKpnbrqk":
            for squares in self.pieces[letter]:
                if square in squares:
                    return letter
    def piece_vision(self, square: str) -> dict | None:
        move_output = list()
        capture_output = list()
        piece = self.search(square)
        if piece is None:
            return None
        match piece.casefold():
            case "p":
                #White: 2 * int(True) - 1 = 1, Black: 2 * int(False) - 1 = -1
                if square[0] != "h":
                    candidate = translate(square, 2 * int(piece_color(piece)) - 1, 1)
                    if self.search(candidate) is None:
                        capture_output.append(candidate)
                    elif piece_color(self.search(candidate)) != piece_color(piece):
                        capture_output.append(candidate)
                if square[0] != "a":
                    candidate = translate(square, 2 * int(piece_color(piece)) - 1, -1)
                    if self.search(candidate) is None:
                        capture_output.append(candidate)
                    elif piece_color(self.search(candidate)) != piece_color(piece):
                        capture_output.append(candidate)
                in_front = translate(square, 2 * int(piece_color(piece)) - 1, 0)
                if self.search(in_front) is None:
                    move_output.append(in_front)
                in_front = translate(square, 4 * int(piece_color(piece)) - 2, 0)
                if self.search(in_front) is None:
                    if piece_color(piece):
                        #white
                        if square[1] == "2":
                            move_output.append(in_front)
                    else:
                        #black
                        if square[1] == "7":
                            move_output.append(in_front)
            case _:
                #I'll figure out all the other pieces later
                pass
        return {
            "move": tuple(move_output),
            "capture": tuple(capture_output)
        }
    def check(self) -> bool:
        if self.to_move:
            #white to move, check if black sees white king
            king_square = self.pieces["K"][0]
            for letter in "pnbqrk":
                for square in self.pieces[letter]:
                    if king_square in self.piece_vision(square):
                        return True
            return False
        else:
            #black to move, check if white sees black king
            king_square = self.pieces["k"][0]
            for letter in "PNBQRK":
                for square in self.pieces[letter]:
                    if king_square in self.piece_vision(square):
                        return True
            return False
    def legal(self) -> bool:
        return True # for now
    def count_material(self) -> int:
        white_material = len(self.pieces["P"]) + 3 * len(self.pieces["N"]) + 3 * len(self.pieces["B"]) + 5 * len(self.pieces["R"]) + 9 * len(self.pieces["Q"])
        black_material = len(self.pieces["p"]) + 3 * len(self.pieces["n"]) + 3 * len(self.pieces["b"]) + 5 * len(self.pieces["r"]) + 9 * len(self.pieces["q"])
        return white_material - black_material
def check_square(square: str) -> bool:
    if len(square) != 2:
        return False
    return square[0] in "abcdefgh" and square[1] in "12345678"
def check_fen(fen: str) -> None:
    splitter = fen.split()
    assert len(splitter) == 6, "FEN has too few or too many elements"
    board = splitter[0].split("/")
    assert len(board) == 8, "FEN element 1 has too few or too many elements"
    assert list(splitter[0]).count("K") == 1, "White has too many kings"
    assert list(splitter[0]).count("k") == 1, "Black has too many kings"
    for row in board:
        row_sum = 0
        for char in row:
            assert char in "pnbrqkPNBRQK12345678", "FEN element 1 has an unrecognized character"
            try:
                row_sum += int(char)
            except ValueError:
                row_sum += 1
        assert row_sum == 8, "FEN has invalid boardstate"
    assert (len(splitter[1]) == 1 and splitter[1] in "wb"), "FEN element 2 has unrecognized character(s)"
    assert len(splitter[2]) in range(1, 5), "FEN element 3 invalid"
    for char in splitter[2]:
        assert char in ["K", "Q", "k", "q", "-"], "FEN element 3 has unrecognized character(s)"
    assert list(splitter[2]).count("K") <= 1, "FEN element 3 invalid"
    assert list(splitter[2]).count("k") <= 1, "FEN element 3 invalid"
    assert list(splitter[2]).count("Q") <= 1, "FEN element 3 invalid"
    assert list(splitter[2]).count("q") <= 1, "FEN element 3 invalid"
    assert (splitter[3] == "-" or (check_square(splitter[3]) and splitter[3][1] in "36")), "FEN element 4 invalid"
    assert (len(splitter[4]) == 1 and int(splitter[4]) >= 0), "FEN element 5 invalid"
    assert (len(splitter[5]) == 1 and int(splitter[5]) > 0), "FEN element 6 invalid"    
def convert(fen: str) -> position:
    check_fen(fen)
    splitter = fen.split()

    pieces = {
        "P": list(),
        "p": list(),
        "N": list(),
        "n": list(),
        "B": list(),
        "b": list(),
        "R": list(),
        "r": list(),
        "Q": list(),
        "q": list(),
        "K": list(),
        "k": list()
    }
    castling = [False] * 4
    row = 8
    column = 1
    for element in splitter[0].split("/"):
        #piece positions
        for char in element:
            try:
                #empty squares
                column += int(char)
            except ValueError:
                #piece
                pieces[char].append(compress(column, row))
                column += 1
            if column == 9:
                row -= 1
                column = 1
    for char in splitter[2]:
        match char:
            case "K":
                castling[0] = True
            case "Q":
                castling[1] = True
            case "k":
                castling[2] = True
            case "q":
                castling[3] = True
    return position(pieces, splitter[1] == "w", tuple(castling), splitter[3], splitter[4])

def run():
    """
    fen = input("FEN: ")
    depth = int(input("Depth: "))
    if fen in openings.keys():
        print("Running at depth: Infinity")
        print("Evaluation:", openings[fen][0])
        print("Best move:", openings[fen][1])
    else:
        print("Running at depth:", depth)
    """
try:
    run()
except Exception as e:
    print(repr(e))