# building off of chess engine project from high school
class piece:
    def __init__(self, identity=None):
        assert identity is None or type(identity) == str, "only accepts strings"
        assert identity in ["k", "q", "r", "b", "n", "p", "K", "Q", "R", "B", "N", "P", None], "bad identifier"
        self.identity = identity
        self.color = int(identity == identity.casefold())

class square:
    def __init__(self, row=None, column=None, occupier=None):
        assert row is None or type(row) == int, "row must be an integer"
        assert column is None or type(column) == int, "column must be an integer"
        assert occupier is None or type(occupier) == piece, "occupier must be a piece"
        assert row in (list(range(8)) + [None]), "0 <= row < 8"
        assert column in (list(range(8)) + [None]), "0 <= column < 8"
        self.row = row
        self.column = column
        self.occupier = occupier
        
class position:
    def __init__(self, pos: list, color: bool, castle: list, ep: square | None, clock: int, fullmove: int):
        assert len(castle) == 4, "invalid castle list"
        for element in castle:
            assert type(element) == bool, "invalid castle list"
        assert ep.occupier is None, "invalid ep square"
        for row in pos:
            for elem in row:
                assert type(elem) == square, "invalid position"
        self.color = color
        self.white_castle_short = castle[0]
        self.white_castle_long = castle[1]
        self.black_castle_short = castle[2]
        self.black_castle_long = castle[3]
        self.en_passant = ep
        self.clock = clock
        self.fullmove = fullmove
        self.descr = pos
def move_vision(current: position, highlight: square) -> list:
    id = highlight.occupier.identity
    assert not id is None, ("empty square: " + str(highlight.row) + ", " + str(highlight.column))
    squares = list()
    match id:
        case "P":
            #white pawn
            if current.descr[highlight.row][highlight.column + 1].occupier is None:
                #one square in front
                squares.append(current.descr[highlight.row][highlight.column + 1])
                if highlight.row == 1 and current.descr[highlight.row][highlight.column + 2].occupier is None:
                    #two squares in front, hasn't moved yet
                    squares.append(current.descr[highlight.row][highlight.column + 2])
        case "p":
            #black pawn
            if current.descr[highlight.row][highlight.column - 1].occupier is None:
                #one square in "front"
                squares.append(current.descr[highlight.row][highlight.column - 1])
                if highlight.row == 6 and current.descr[highlight.row][highlight.column - 2].occupier is None:
                    #two squares in "front", hasn't moved yet
                    squares.append(current.descr[highlight.row][highlight.column - 2])
        case _:
            match id.casefold():
                case "n":
                    #knight
                    x_coord = [1, 1, -1, -1, 2, 2, -2, -2]
                    y_coord = [2, -2, 2, -2, 1, -1, 1, -1]
                    for i in range(8):
                        try:
                            if not current.descr[highlight.row + x_coord[i]][highlight.column + y_coord[i]].occupier is None:
                                #square occupied
                                if highlight.occupier.color is current.descr[highlight.row + x_coord[i]][highlight.column + y_coord[i]].occupier.color:
                                    #same color, no capture possible
                                    continue
                            squares.append(current.descr[highlight.row + x_coord[i]][highlight.column + y_coord[i]])
                        except IndexError:
                            #beyond the confines of the board
                            continue
                case "b":
                    #bishop

                    #+, +
                    for i in range(1, 8):
                        if highlight.row + i > 7 or highlight.column + i > 7:
                            #beyond the confines of the board, exit loop
                            break
                        if current.descr[highlight.row + i][highlight.column + i].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row + i][highlight.column + i])
                        else:
                            if highlight.occupier.color is current.descr[highlight.row + i][highlight.column + i].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row + i][highlight.column + i])
                            break
                    #+, -
                    for i in range(1, 8):
                        if highlight.row + i > 7 or highlight.column - i < 0:
                            #beyond the confines of the board, exit loop
                            break
                        if current.descr[highlight.row + i][highlight.column - i].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row + i][highlight.column - i])
                        else:
                            if highlight.occupier.color is current.descr[highlight.row + i][highlight.column - i].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row + i][highlight.column - i])
                            break
                    #-, +
                    for i in range(1, 8):
                        if highlight.row - i < 0 or highlight.column + i > 7:
                            #beyond the confines of the board, exit loop
                            break
                        if current.descr[highlight.row - i][highlight.column + i].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row - i][highlight.column + i])
                        else:
                            if highlight.occupier.color is current.descr[highlight.row - i][highlight.column + i].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row - i][highlight.column + i])
                            break
                    #-, -
                    for i in range(1, 8):
                        if highlight.row - i < 0 or highlight.column - i < 0:
                            #beyond the confines of the board, exit loop
                            break
                        if current.descr[highlight.row - i][highlight.column - i].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row - i][highlight.column - i])
                        else:
                            #square occupied
                            if highlight.occupier.color is current.descr[highlight.row - i][highlight.column - i].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row - i][highlight.column - i])
                            break
                case "r":
                    #rook

                    # +x
                    for i in range(1, 8):
                        if highlight.row + i > 7:
                            #beyond the confines of the board, exit loop
                            break
                        if current.descr[highlight.row + i][highlight.column].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row + i][highlight.column])
                        else:
                            #square occupied
                            if highlight.occupier.color is current.descr[highlight.row + i][highlight.column].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row + i][highlight.column])
                            break
                    # +y
                    for i in range(1, 8):
                        if highlight.column + i > 7:
                            #beyond the confines of the board: exit loop
                            break
                        if current.descr[highlight.row][highlight.column + i].occupier is None:
                            #square empty
                            squares.append(current.descr[highlight.row][highlight.column + i])
                        else:
                            #square occupied
                            if highlight.occupier.color is current.descr[highlight.row][highlight.column].occupier.color:
                                #same color, no capture possible, exit loop
                                break
                            #different color, capture possible, add square then exit loop
                            squares.append(current.descr[highlight.row][highlight.column + i])
                            break
                    # -x
                    for i in range(1, 8):
                        pass
                    # -y
                    for i in range(1, 8):
                        pass
                case "q":
                    pass
                case "k":
                    pass
                case _:
                    raise Exception(id + " is not a piece")
    return squares
def capture_vision(current: position, highlight: square) -> list:
    if highlight.occupier.identity.casefold() == "p":
        pass
    else:
        return move_vision(current, highlight)
def convert(fen: str) -> position:
    splitter = fen.split()
    assert len(splitter[0].split("/")) == 8, "FEN: invalid position notation"
    assert splitter[1] in list("wb"), "FEN: invalid color to move"
    for letter in splitter[2]:
        assert letter in list("KQkq-"), "FEN: invalid castle rights"
    assert splitter[3][0] in list("abcdefgh-")
    try:
        assert splitter[3][1] in list("36")
    except IndexError:
        pass
    try:
        assert int(splitter[4]) >= 0, "FEN: halfmove cannot be negative"
    except ValueError:
        raise Exception("FEN: halfmove must be a number")
    try:
        assert int(splitter[5]) > 0, "FEN: fullmove must be positive"
    except ValueError:
        raise Exception("FEN: fullmove must be a number")
    row = 7
    column = 0
    color = True
    ep = square()
    castle = [False, False, False, False]
    output = list()
    for i in range(8):
        output.append([square()] * 8)
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
    return position(output, color, castle, ep, splitter[4], splitter[5])
        

def evaluate(sq: square) -> float:
    
    return 0.0