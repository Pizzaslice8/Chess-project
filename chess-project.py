# building off of chess engine project from high school
import time, os, random
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
catalog = list()
def interpret(square: str) -> tuple:
    return (ord(square[0]) - 96, int(square[1]))
def compress(x: int, y: int) -> str:
    return str(chr(x + 96)) + str(y)
def translate(square: str, x_move: int, y_move: int) -> str:
    return compress(interpret(square)[0] + x_move, interpret(square)[1] + y_move)
def squares_between(start: str, end: str) -> list:
    start_x, start_y = interpret(start)
    end_x, end_y = interpret(end)
    step_x = (end_x > start_x) - (end_x < start_x)
    step_y = (end_y > start_y) - (end_y < start_y)
    output = list()
    x = start_x + step_x
    y = start_y + step_y
    while (x, y) != (end_x, end_y):
        output.append(compress(x, y))
        x += step_x
        y += step_y
    return output
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
    def reduce(self) -> str:
        output = ""
        for things in self.pieces.items():
            for square in things[1]:
                output += things[0] + square
        return output
    def repetition_key(self) -> tuple:
        pieces = tuple((piece, tuple(sorted(squares))) for piece, squares in self.pieces.items())
        castle = (self.white_castle_short, self.white_castle_long, self.black_castle_short, self.black_castle_long)
        return pieces, self.to_move, castle, self.ep_square
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
    def attack_map(self, square: str) -> list:
        vision = self.piece_vision(square)
        return [] if vision is None else [square + target for target in vision["capture"]]
    def attack_map_all(self, color_to_move: bool) -> list:
        output = list()
        attacker_color = -1 if color_to_move else 1
        for square in self.occupied_squares():
            if color(self.search(square)) == attacker_color:
                output.extend(self.attack_map(square))
        return output
    def is_attacked(self, square: str, attacker_color: int) -> bool:
        for source in self.occupied_squares():
            if color(self.search(source)) == attacker_color:
                vision = self.piece_vision(source)
                if square in vision["capture"]:
                    return True
        return False
    def legal_basic(self, move: str) -> bool:
        #does not account for if the king is in check
        try:
            assert len(move) == 4
            start = move[:2]
            end = move[2:]
            assert check_square(start) and check_square(end)
            assert self.search(start) is not None
            assert self.search(end) is None or color(self.search(start)) != color(self.search(end))
            delta_x = interpret(end)[0] - interpret(start)[0]
            delta_y = interpret(end)[1] - interpret(start)[1]
            distance_x = abs(delta_x)
            distance_y = abs(delta_y)
            #movement
            match self.search(start).casefold():
                case "p":
                    if delta_x != 0:
                        assert distance_x == 1
                        assert delta_y == color(self.search(start))
                        assert self.search(end) is not None or end == self.ep_square
                    else:
                        assert self.search(end) is None
                        assert distance_x == 0
                        direction = color(self.search(start))
                        if interpret(start)[1] in (2, 7):
                            assert delta_y in (direction, 2 * direction)
                            if abs(delta_y) == 2:
                                assert self.search(translate(start, 0, direction)) is None
                        else:
                            assert delta_y == direction
                case "n":
                    distance = (distance_x, distance_y)
                    assert distance == (1, 2) or distance == (2, 1)
                case "b":
                    assert distance_x == distance_y and distance_x != 0
                    between_full = squares_between(start, end)
                    for s in between_full:
                        assert self.search(s) is None
                case "r":
                    assert distance_x == 0 or distance_y == 0
                    assert not (distance_x == 0 and distance_y == 0)
                    between_full = squares_between(start, end)
                    for s in between_full:
                        assert self.search(s) is None
                case "q":
                    assert not (distance_x == 0 and distance_y == 0)
                    assert distance_x == 0 or distance_y == 0 or distance_x == distance_y
                    between_full = squares_between(start, end)
                    for s in between_full:
                        assert self.search(s) is None
                case "k":
                    distance = (distance_x, distance_y)
                    if color(self.search(start)) == 1:
                        #white king
                        if end == "g1":
                            assert start == "e1"
                            assert self.white_castle_short
                            assert self.search("f1") is None and self.search("g1") is None
                            assert self.search("h1") == "R"
                        elif end == "c1":
                            assert start == "e1"
                            assert self.white_castle_long
                            assert all(self.search(square) is None for square in ("b1", "c1", "d1"))
                            assert self.search("a1") == "R"
                        else:
                            assert distance == (0, 1) or distance == (1, 0) or distance == (1, 1)
                    else:
                        #black king
                        if end == "g8":
                            assert start == "e8"
                            assert self.black_castle_short
                            assert self.search("f8") is None and self.search("g8") is None
                            assert self.search("h8") == "r"
                        elif end == "c8":
                            assert start == "e8"
                            assert self.black_castle_long
                            assert all(self.search(square) is None for square in ("b8", "c8", "d8"))
                            assert self.search("a8") == "r"
                        else:
                            assert distance == (0, 1) or distance == (1, 0) or distance == (1, 1)
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
        change_x = list()
        change_y = list()
        match self.search(square).casefold():
            case "n":
                change_x = [2, 2, 1, 1, -2, -2, -1, -1]
                change_y = [1, -1, -2, 2, 1, -1, -2, 2]
            case "b":
                change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(1, 8)) + list(range(-1, -8, -1))
                change_y = list(range(1, 8)) + list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(-1, -8, -1))
            case "r":
                change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + [0] * 14
                change_y = [0] * 14 + list(range(1, 8)) + list(range(-1, -8, -1))
            case "q":
                change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(1, 8)) + list(range(-1, -8, -1))
                change_y = list(range(1, 8)) + list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(-1, -8, -1))
                change_x.extend(list(range(1, 8)) + list(range(-1, -8, -1)) + [0] * 14)
                change_y.extend([0] * 14 + list(range(1, 8)) + list(range(-1, -8, -1)))
            case "k":
                change_x = [1, 1, 0, -1, -1, -1, 0, 1]
                change_y = [0, 1, 1, 1, 0, -1, -1, -1]
            case "p":
                change_x = [1, -1, 0]
                change_y = [1, 1, 1] if color(self.search(square)) == 1 else [-1, -1, -1]
                if interpret(square)[1] == 2 and color(self.search(square)) == 1:
                    change_y.append(2)
                    change_x.append(0)
                elif interpret(square)[1] == 7 and color(self.search(square)) == -1:
                    change_y.append(-2)
                    change_x.append(0)
        candidates = [translate(square, x, y) for x, y in zip(change_x, change_y) if check_square(translate(square, x, y))]
        for sq in candidates:
            if self.search(square).casefold() == "p" and interpret(sq)[0] != interpret(square)[0]:
                capture_output.append(sq)
                continue
            if self.legal_basic(square + sq):
                if self.search(square).casefold() == "p":
                    if interpret(sq)[0] == interpret(square)[0]:
                        move_output.append(sq)
                    else:
                        capture_output.append(sq)
                else:
                    move_output.append(sq)
                    capture_output.append(sq)
        
        return {
            "move": move_output,
            "capture": capture_output
        }
    def make_move(self, move: str) -> dict:
        start = move[:2]
        end = move[2:]
        piece = self.search(start)
        target = self.search(end)
        assert piece is not None
        en_passant = piece.casefold() == "p" and end == self.ep_square and target is None and start[0] != end[0]
        captured_square = translate(end, 0, -color(piece)) if en_passant else end if target is not None else None
        captured_piece = self.search(captured_square) if captured_square is not None else None
        instructions = {
            "reverse": end + start,
            "moved_piece": piece,
            "moved_rook": None,
            "promotion": None,
            "captured_piece": captured_piece,
            "captured_square": captured_square,
            "ep_square": self.ep_square,
            "castle": (self.white_castle_short, self.white_castle_long, self.black_castle_short, self.black_castle_long),
            "half_move": self.half_move
        }
        if captured_square is not None:
            self.pieces[captured_piece].remove(captured_square)
        self.pieces[piece].remove(start)
        self.pieces[piece].append(end)
        if piece == "K" and end in ("c1", "g1"):
            rook_start, rook_end = ("a1", "d1") if end == "c1" else ("h1", "f1")
            self.pieces["R"].remove(rook_start)
            self.pieces["R"].append(rook_end)
            instructions["moved_rook"] = ("R", rook_start, rook_end)
        elif piece == "k" and end in ("c8", "g8"):
            rook_start, rook_end = ("a8", "d8") if end == "c8" else ("h8", "f8")
            self.pieces["r"].remove(rook_start)
            self.pieces["r"].append(rook_end)
            instructions["moved_rook"] = ("r", rook_start, rook_end)
        if piece == "K":
            self.white_castle_short = self.white_castle_long = False
        elif piece == "k":
            self.black_castle_short = self.black_castle_long = False
        elif piece == "R":
            if start == "a1": self.white_castle_long = False
            if start == "h1": self.white_castle_short = False
        elif piece == "r":
            if start == "a8": self.black_castle_long = False
            if start == "h8": self.black_castle_short = False
        if captured_piece == "R":
            if captured_square == "a1": self.white_castle_long = False
            if captured_square == "h1": self.white_castle_short = False
        elif captured_piece == "r":
            if captured_square == "a8": self.black_castle_long = False
            if captured_square == "h8": self.black_castle_short = False
        self.ep_square = None
        if piece in ("P", "p"):
            promotion_rank = "8" if piece == "P" else "1"
            if end[1] == promotion_rank:
                promoted_piece = "Q" if piece == "P" else "q"
                self.pieces[piece].remove(end)
                self.pieces[promoted_piece].append(end)
                instructions["promotion"] = promoted_piece
            if abs(int(end[1]) - int(start[1])) == 2:
                self.ep_square = translate(start, 0, color(piece))
        self.half_move = 0 if piece in ("P", "p") or captured_piece is not None else self.half_move + 1
        self.to_move = not self.to_move
        catalog.append(self.repetition_key())
        return instructions
    def undo_move(self, instructions: dict) -> None:
        catalog.remove(self.repetition_key())
        start = instructions["reverse"][2:]
        end = instructions["reverse"][:2]
        current_piece = instructions["promotion"] or instructions["moved_piece"]
        self.pieces[current_piece].remove(end)
        self.pieces[instructions["moved_piece"]].append(start)
        if instructions["moved_rook"] is not None:
            rook, rook_start, rook_end = instructions["moved_rook"]
            self.pieces[rook].remove(rook_end)
            self.pieces[rook].append(rook_start)
        if instructions["captured_piece"] is not None:
            self.pieces[instructions["captured_piece"]].append(instructions["captured_square"])
        self.ep_square = instructions["ep_square"]
        self.white_castle_short, self.white_castle_long, self.black_castle_short, self.black_castle_long = instructions["castle"]
        self.to_move = not self.to_move
        self.half_move = instructions["half_move"]
    def king_safe(self, move: str) -> bool:
        if not self.legal_basic(move):
            return False
        moving_color = color(self.search(move[:2]))
        opponent_color = -moving_color
        if move[:2] in ("e1", "e8") and move[2:] in ("c1", "g1", "c8", "g8"):
            transit = {"c1": "d1", "g1": "f1", "c8": "d8", "g8": "f8"}[move[2:]]
            if self.is_attacked(move[:2], opponent_color) or self.is_attacked(transit, opponent_color):
                return False
        reverse = self.make_move(move)
        try:
            king = self.pieces["k"][0] if moving_color == -1 else self.pieces["K"][0]
            return not self.is_attacked(king, opponent_color)
        finally:
            self.undo_move(reverse)
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
        for x in range(1, 9):
            for y in range(1, 9):
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
                total += 0.2 * int(pawn[1])
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
        if len(self.pieces["q"]) == 0 and len(self.pieces["Q"]) == 0:
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
                total -= 0.3 * int(self.search(square) == "p")
        return total
    def count(self) -> float:
        #basic evaluation of position
        return self.count_material() + self.square_control() + self.space() + self.king_safety()
    def legal_moves(self) -> list:
        output = list()
        for square in self.occupied_squares():
            if color(self.search(square)) == (1 if self.to_move else -1):
                change_x = list()
                change_y = list()
                match self.search(square).casefold():
                    case "n":
                        change_x = [2, 2, 1, 1, -2, -2, -1, -1]
                        change_y = [1, -1, -2, 2, 1, -1, -2, 2]
                    case "b":
                        change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(1, 8)) + list(range(-1, -8, -1))
                        change_y = list(range(1, 8)) + list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(-1, -8, -1))
                    case "r":
                        change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + [0] * 14
                        change_y = [0] * 14 + list(range(1, 8)) + list(range(-1, -8, -1))
                    case "q":
                        change_x = list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(1, 8)) + list(range(-1, -8, -1))
                        change_y = list(range(1, 8)) + list(range(1, 8)) + list(range(-1, -8, -1)) + list(range(-1, -8, -1))
                        change_x.extend(list(range(1, 8)) + list(range(-1, -8, -1)) + [0] * 14)
                        change_y.extend([0] * 14 + list(range(1, 8)) + list(range(-1, -8, -1)))
                    case "k":
                        change_x = [1, 1, 0, -1, -1, -1, 0, 1]
                        change_y = [0, 1, 1, 1, 0, -1, -1, -1]
                    case "p":
                        change_x = [1, -1, 0]
                        change_y = [1, 1, 1] if color(self.search(square)) == 1 else [-1, -1, -1]
                        if interpret(square)[1] == 2 and color(self.search(square)) == 1:
                            change_y.append(2)
                            change_x.append(0)
                        elif interpret(square)[1] == 7 and color(self.search(square)) == -1:
                            change_y.append(-2)
                            change_x.append(0)
                candidates = [translate(square, x, y) for x, y in zip(change_x, change_y) if check_square(translate(square, x, y))]
                if square == "e1" and self.white_castle_short:
                    candidates.append("g1")
                if square == "e1" and self.white_castle_long:
                    candidates.append("c1")
                if square == "e8" and self.black_castle_short:
                    candidates.append("g8")
                if square == "e8" and self.black_castle_long:
                    candidates.append("c8")
                for sq in candidates:
                    if self.legal(square + sq):
                        output.append(square + sq)
        return output
    def game_status(self) -> dict:
        #returns status and legal moves to avoid calling legal_moves() more than necessary
        output = {
            "status": None,
            "legal_moves": self.legal_moves()
        }
        if len(output["legal_moves"]) == 0:
            if self.to_move:
                #white to move
                output["status"] = "Checkmate: Black wins" if self.is_attacked(self.pieces["K"][0], -1) else "Draw: Stalemate"
            else:
                #black to move
                output["status"] = "Checkmate: White wins" if self.is_attacked(self.pieces["k"][0], 1) else "Draw: Stalemate"
        elif int(self.half_move) >= 100:
            #100 half-moves since last pawn move/capture
            output["status"] = "Draw: 50-move rule"
        elif self.insufficient_material():
            output["status"] = "Draw: Insufficient material"
        elif catalog.count(self.repetition_key()) >= 3:
            output["status"] = "Draw: Threefold repetition"
        return output
    def insufficient_material(self) -> bool:
        if any(self.pieces[piece] for piece in "PpQqRr"):
            return False
        minors = [(piece, square) for piece in "NnBb" for square in self.pieces[piece]]
        if len(minors) <= 1:
            return True
        if all(piece.casefold() == "b" for piece, _ in minors):
            bishop_colors = {(ord(square[0]) + int(square[1])) % 2 for _, square in minors}
            return len(bishop_colors) == 1
        return False
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
    assert splitter[4].isdigit() and int(splitter[4]) >= 0, "FEN element 5 invalid"
    assert splitter[5].isdigit() and int(splitter[5]) > 0, "FEN element 6 invalid"
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
    return position(pieces, splitter[1] == "w", tuple(castling), splitter[3], int(splitter[4]))

def do(fen: str, deep: int):
    #returns (evaluation, best_move)
    start = time.time()
    current = convert(fen)
    def eval_depth_1(pos: position, legal_moves: list) -> list:
        out = dict()
        for move in legal_moves:
            reverse = None
            try:
                reverse = pos.make_move(move)
                out[move] = pos.count()
            finally:
                if reverse is not None:
                    pos.undo_move(reverse)
        output = ["", float("-inf") if pos.to_move else float("inf")]
        for potential in out.items():
            if pos.to_move:
                #Maximize evaluation
                if potential[1] > output[1]:
                    output[0] = potential[0]
                    output[1] = potential[1]
            else:
                #Minimize evaluation
                if potential[1] < output[1]:
                    output[0] = potential[0]
                    output[1] = potential[1]
        return output
    def eval_depth(pos: position, depth: int) -> list:
        #[best move, evaluation]
        if time.time() - start > 15.0:
            raise TimeoutError
        game = pos.game_status()
        if game["status"] is not None:
            match game["status"]:
                case "Checkmate: White wins":
                    return ["", float("inf")]
                case "Checkmate: Black wins":
                    return ["", float("-inf")]
                case _:
                    return ["", 0.0]
        if depth == 1:
            return eval_depth_1(pos, game["legal_moves"])
        else:
            out = dict()
            for move in game["legal_moves"]:
                reverse = None
                try:
                    reverse = pos.make_move(move)
                    thing = eval_depth(pos, depth - 1)
                    candidate_evaluation = thing[1]
                    out[move] = candidate_evaluation
                finally:
                    if reverse is not None:
                        pos.undo_move(reverse)
            output = ["", float("-inf") if pos.to_move else float("inf")]
            for potential in out.items():
                if pos.to_move:
                    #Maximize evaluation
                    if potential[1] > output[1]:
                        output[0] = potential[0]
                        output[1] = potential[1]
                else:
                    #Minimize evaluation
                    if potential[1] < output[1]:
                        output[0] = potential[0]
                        output[1] = potential[1]
            return output
    catalog.clear()
    catalog.append(current.repetition_key())
    assert current.game_status()["status"] is None
    for i in range(0, deep):
        yield tuple(eval_depth(current, i + 1))
def run() -> None:
    fen = input("FEN: ")
    depth = int(input("Depth: "))
    if fen in openings.keys():
        print("Running at depth: Infinity")
        print("Evaluation:", openings[fen][0])
        print("Best move:", openings[fen][1])
    else:
        print("Running at depth:", depth)
        if depth == 0:
            print("Running at depth: 0")
            print("Evaluation:", convert(fen).count())
            print("Best move: None")
            return None
        output = None
        try:
            generator = do(fen, depth)
            for i in range(0, depth):
                output = next(generator)
            print("Evaluation:", str(output[1]))
            print("Best move:", str(output[0]))
        except AssertionError:
            print("Game already over")
        except TimeoutError:
            print("Search exceeded execution time at depth", i + 1)
            if output is None:
                print("No search iteration completed")
            else:
                print("Evaluation:", output[1])
                print("Best move:", output[0])
        except Exception as e:
            print("Error: " + str(repr(e)))
run()