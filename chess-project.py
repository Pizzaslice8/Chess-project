# building off of chess engine project from high school
openings = {
    #0 halfmoves
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": (0.2, "e2e4"), #starting position
    #1 halfmoves
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": (0.2, "e7e5"), #1. e4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": (0.2, "g8f6"), #1. d4
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": (0.1, "e7e5"), #1. c4
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": (0.1, "g8f6"), #1. Nf3
    #2 halfmoves, 1. e4
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.2, "g1f3"), #1. e4 e5
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.3, "g1f3"), #1. e4 c5
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.4, "d2d4"), #1. e4 e6
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": (0.3, "d2d4"), #1. e4 c6
    #2 halfmoves, 1. d4
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2": (0.2, "c2c4"), #1. d4 Nf6
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2": (0.3, "c2c4") #1. d4 d5
    #more to come
}
center = ("d4", "e4", "d5", "e5")
subcenter = ("c3", "c4", "c5", "c6", "d6", "e6", "f6", "f5", "f4", "f3", "e3", "d3")
def interpret(square: str) -> tuple:
    return (ord(square[0]) - 96, int(square[1]))
def compress(x: int, y: int) -> str:
    return str(chr(x + 96)) + str(y)
def translate(square: str, x_move: int, y_move: int) -> str:
    return compress(interpret(square)[0] + x_move, interpret(square)[1] + y_move)
def color(piece: str) -> int:
    #White: 1, black: -1
    return 2 * int(piece != piece.casefold()) - 1
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
    def occupied_squares(self) -> list:
        output = list()
        for stuff in self.pieces.values():
            output.extend(stuff)
        return output
    def legal_basic(self, move: str) -> bool:
        #does not account for if the king is in check
        try:
            assert len(move) == 4
            start = move[:2]
            end = move[2:]
            assert check_square(self.search(start)) and check_square(self.search(end))
            assert not self.search(start) is None
            assert self.search(end) is None or color(self.search(start)) != color(self.search(end))
            distance_x = abs(interpret(start)[0] - interpret(end)[0])
            distance_y = abs(interpret(start)[1] - interpret(end)[1])
            #movement
            match self.search(start).casefold():
                case "p":
                    if self.search(end) is None or self.search(end) is self.ep_square:
                        #capture
                        assert distance_x in (1, -1)
                        assert distance_y == color(self.search(start))
                    else:
                        #move
                        assert distance_x == 0
                        if color(self.search(start)) == 1:
                            #white
                            if interpret(start)[1] == 2:
                                assert distance_y in (1, 2)
                            else:
                                assert distance_y == 1
                        else:
                            #black
                            if interpret(start)[1] == 7:
                                assert distance_y in (-1, -2)
                            else:
                                assert distance_y == -1
                case "n":
                    distance = (distance_x, distance_y)
                    assert distance is (1, 2) or distance is (2, 1)
                case "b":
                    assert distance_x == distance_y
                    between_x = list(range(interpret(start)[0], interpret(end)[0]))
                    between_x.pop(0)
                    between_y = list(range(interpret(start)[1], interpret(end)[1]))
                    between_y.pop(0)
                    between_full = [compress(i, j) for i, j in zip(between_x, between_y)]
                    for s in between_full:
                        assert self.search(s) is None
                case "r":
                    assert distance_x == 0 or distance_y == 0
                    assert not (distance_x == 0 and distance_y == 0)
                    if distance_y == 0:
                        between_x = list(range(interpret(start)[0], interpret(end)[0]))
                        between_x.pop(0)
                        between_full = [compress(i, interpret(start)[1]) for i in between_x]
                        for s in between_full:
                            assert self.search(s) is None
                    elif distance_x == 0:
                        between_y = list(range(interpret(start)[1], interpret(end)[1]))
                        between_y.pop(0)
                        between_full = [compress(interpret(start)[0], j) for j in between_y]
                        for s in between_full:
                            assert self.search(s) is None
                    else:
                        return False
                case "q":
                    assert not (distance_x == 0 and distance_y == 0)
                    if distance_x == 0:
                        between_y = list(range(interpret(start)[1], interpret(end)[1]))
                        between_y.pop(0)
                        between_full = [compress(interpret(start)[0], j) for j in between_y]
                        for s in between_full:
                            assert self.search(s) is None
                    elif distance_y == 0:
                        between_x = list(range(interpret(start)[0], interpret(end)[0]))
                        between_x.pop(0)
                        between_full = [compress(i, interpret(start)[1]) for i in between_x]
                        for s in between_full:
                            assert self.search(s) is None
                    else:
                        assert distance_x == distance_y
                        between_x = list(range(interpret(start)[0], interpret(end)[0]))
                        between_x.pop(0)
                        between_y = list(range(interpret(start)[1], interpret(end)[1]))
                        between_y.pop(0)
                        between_full = [compress(i, j) for i, j in zip(between_x, between_y)]
                        for s in between_full:
                            assert self.search(s) is None
                case "k":
                    distance = (distance_x, distance_y)
                    if color(self.search(start)) == 1:
                        #white king
                        if end == "g1":
                            assert self.white_castle_short
                        elif end == "c1":
                            assert self.white_castle_long
                        else:
                            assert distance is (0, 1) or distance is (1, 0) or distance is (1, 1)
                    else:
                        #black king
                        if end == "g8":
                            assert self.black_castle_short
                        elif end == "c8":
                            assert self.black_castle_long
                        else:
                            assert distance is (0, 1) or distance is (1, 0) or distance is (1, 1)
                case _:
                    return False
        except AssertionError:
            return False
        return True
    def piece_vision(self, square: str) -> dict | None:
        move_output = list()
        capture_output = list()
        if self.search(square) is None:
            return None
        if self.search(square).casefold() == "p":
            for i in range(1, 9):
                for j in range(1, 9):
                    candidate = square + compress(i, j)
                    if self.legal_basic(candidate):
                        if interpret(square)[0] == i:
                            move_output.append(candidate)
                        else:
                            capture_output.append(candidate)
        else:
            for i in range(1, 9):
                for j in range(1, 9):
                    candidate = square + compress(i, j)
                    if self.legal_basic(candidate):
                        move_output.append(candidate)
                        capture_output.append(candidate)
        return {
            "move": move_output,
            "capture": capture_output
        }
    def make_move(self, move: str) -> None:
        assert len(move) == 4
        start = move[:2]
        end = move[2:]
        piece = self.search(start)
        target = self.search(end)
        if end is self.ep_square:
            sq = translate(end, 0, -1 * color(start))
            target = self.search(sq)
            self.pieces[piece].remove(start)
            self.pieces[piece].append(end)
            self.pieces[target].remove(sq)
        elif self.search(end) is None:
            if piece == "K" and target in ("c1", "g1"):
                self.pieces[piece].remove(start)
                self.pieces[piece].append(end)
                if target == "c1":
                    self.pieces["R"].remove("a1")
                    self.pieces["R"].append("d1")
                else:
                    self.pieces["R"].remove("h1")
                    self.pieces["R"].append("f1")
            elif piece == "k" and target in ("c8", "g8"):
                self.pieces[piece].remove(start)
                self.pieces[piece].append(end)
                if target == "c8":
                    self.pieces["r"].remove("a8")
                    self.pieces["r"].append("d8")
                else:
                    self.pieces["r"].remove("h8")
                    self.pieces["r"].append("f8")
            else:
                self.pieces[piece].remove(start)
                self.pieces[piece].append(end)
        else:
            self.pieces[piece].remove(start)
            self.pieces[piece].append(end)
            self.pieces[target].remove(end)
        self.ep_square = None
        match piece:
            case "r":
                if start == "a8":
                    self.black_castle_long = False
                if start == "h8":
                    self.black_castle_short = False
            case "R":
                if start == "a1":
                    self.white_castle_long = False
                if start == "h1":
                    self.white_castle_short = False
            case "k":
                self.black_castle_long = False
                self.black_castle_short = False
            case "K": 
                self.white_castle_long = False
                self.white_castle_short = False
            case "p":
                if target[1] == 1:
                    #too lazy to account for underpromotion
                    self.pieces["p"].remove(target)
                    self.pieces["q"].append(target)
                if target[1] == 5:
                    pawn_squares = (translate(target, 1, 0), translate(target, -1, 0))
                    if self.search(pawn_squares[0]) == "P" or self.search(pawn_squares[1]) == "P":
                        self.ep_square = translate(target, 0, 1)
            case "P":
                if target[1] == 8:
                    self.pieces["P"].remove(target)
                    self.pieces["Q"].append(target)
                if target[1] == 4:
                    pawn_squares = (translate(target, 1, 0), translate(target, -1, 0))
                    if self.search(pawn_squares[0]) == "p" or self.search(pawn_squares[1]) == "p":
                        self.ep_square = translate(target, 0, -1)
    def king_safe(self, move: str) -> bool:
        try:
            assert self.legal_basic(move)
            self.make_move(move)
            for place in self.occupied_squares():
                king = ""
                piece = self.search(place)
                if self.to_move:
                    #white to move, check black pieces
                    king = self.pieces["K"][0]
                    if color(piece) == -1:
                        assert not king in self.piece_vision(piece)["capture"]
                else:
                    #black to move, check white pieces
                    king = self.pieces["k"][0]
                    if color(piece) == 1:
                        assert not king in self.piece_vision(piece)["capture"]
        except AssertionError:
            self.make_move(move[2:] + move[:2])
            return False
        self.make_move(move[2:] + move[:2])
        return True
    def legal(self, move: str) -> bool:
        return self.legal_basic(move) and self.king_safe(move)
    def count_material(self) -> int:
        white_material = len(self.pieces["P"]) + 3 * len(self.pieces["N"]) + 3 * len(self.pieces["B"]) + 5 * len(self.pieces["R"]) + 9 * len(self.pieces["Q"])
        black_material = len(self.pieces["p"]) + 3 * len(self.pieces["n"]) + 3 * len(self.pieces["b"]) + 5 * len(self.pieces["r"]) + 9 * len(self.pieces["q"])
        return white_material - black_material
    def square_control(self) -> float:
        total = 0.0
        white_squares = list()
        black_squares = list()
        for x in range(1, 8):
            for y in range(1, 8):
                square = compress(x, y)
                stuff = self.piece_vision(square)
                if not stuff is None:
                    if self.search(square) != self.search(square).casefold():
                        white_squares.append(square)
                    else:
                        black_squares.append(square)
        for item in white_squares:
            if item in center:
                total += 0.3
            elif item in subcenter:
                total += 0.2
            else:
                total += 0.1
        for item in black_squares:
            if item in center:
                total -= 0.3
            elif item in subcenter:
                total -= 0.2
            else:
                total -= 0.1
        return total
    def space(self) -> float:
        total = 0.0
        for pawn in self.pieces["P"]:
            if pawn[0] in "abgh":
                total += 0.1 * int(pawn[1])
            else:
                total += 0.2 * int(pawn[0])
        for pawn in self.pieces["p"]:
            if pawn[0] in "abgh":
                total -= 0.1 * (8 - int(pawn[1]))
            else:
                total -= 0.2 * (8 - int(pawn[1]))
        return total
    def king_safety(self) -> float:
        white_king_position = self.pieces["K"][0]
        black_king_position = self.pieces["k"][0]
        endgame = False
        total = 0.0
        if len(self.pieces["q"]) == 0 and len(self.pieces["Q"] == 0):
            #endgame OR queenless middlegame
            endgame = len(self.pieces["r"]) < 2 and len(self.pieces["R"]) < 2
        else:
            #middlegame OR queen endgame
            if len(self.pieces["r"]) > 0 or len(self.pieces["R"]) > 0:
                endgame = False
            if len(self.pieces["n"]) + len(self.pieces["N"]) + len(self.pieces["b"]) + len(self.pieces["B"]) > 2:
                endgame = False
        if endgame:
            total += (0.2 * int(white_king_position in center) + 0.1 * int(white_king_position in subcenter))
            total -= (0.2 * int(black_king_position in center) + 0.1 * int(black_king_position in subcenter))
        else:
            total -= (0.2 * int(white_king_position in center) + 0.1 * int(white_king_position in subcenter))
            total += (0.2 * int(black_king_position in center) + 0.1 * int(black_king_position in subcenter))
            #measuring how many pawns you have in front your king
            umbrella_white = (translate(white_king_position, -1, 1), translate(white_king_position, 0, 1), translate(white_king_position, 1, 1))
            umbrella_black = (translate(black_king_position, -1, -1), translate(black_king_position, 0, -1), translate(black_king_position, 1, -1))
            for square in umbrella_white:
                if not check_square(square): continue
                if self.search(square) is None: continue
                total += 0.3 * int(self.search(square) == "P")
            for square in umbrella_black:
                if not check_square(square): continue
                if self.search(square) is None: continue
                total += 0.3 * int(self.search(square) == "p")
        return total
    def count(self) -> float:
        return self.count_material() + self.square_control() + self.space() + self.king_safety()

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