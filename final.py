import pygame as pg
from copy import deepcopy

width, height = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = width//COLS

# rgb
RED,WHITE,BLACK,BLUE,GREY = (255, 0, 0),(255, 255, 255),(0, 0, 0),(76, 252, 241),(169, 169, 169)
AGGIE = pg.transform.scale(pg.image.load('t.png'), (SQUARE_SIZE, SQUARE_SIZE))
LOSER = pg.transform.scale(pg.image.load('u.png'), (SQUARE_SIZE, SQUARE_SIZE))
CROWN = pg.transform.scale(pg.image.load('crown.png'), (SQUARE_SIZE, SQUARE_SIZE))
LOSERCROWN = pg.transform.scale(pg.image.load('ucrown.png'), (SQUARE_SIZE, SQUARE_SIZE))




class Piece:
    """Initializes the piece class"""
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

        """Calculates the position of the piece"""
    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

        """modifies the attribute the piece to become a king"""
    def make_king(self):
        self.king = True

    """draws the pieces on the board"""
    def draw(self, win):
        if self.color == RED:
            win.blit(AGGIE, (self.x - CROWN.get_width()//2, self.y - CROWN.get_height()//2))
        if self.color == WHITE:
            win.blit(LOSER, (self.x - CROWN.get_width()//2, self.y - CROWN.get_height()//2))
        if self.king:
            if self.color == RED:
                win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))
            if self.color == WHITE:
                win.blit(LOSERCROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))
    """Modifies coordinates of the piece class"""
    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)


class Board:
    """Initializes the board classes"""

    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    """draws the squares on the board"""

    def draw_squares(self, win):
        win.fill(GREY)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pg.draw.rect(win, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    """tells the ai what it should value and prioritize"""

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    """moves pieces"""

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1
        """returns the position of the piece for other functions"""

    def get_piece(self, row, col):
        return self.board[row][col]

        """puts pieces on their position on the board for the girst time"""

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        """displays the squaress to the window"""

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)
        """the code that lets you eat pieces"""

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    """determines winner"""

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

    """Determins what moves you can make at any time"""

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    """the code that moves the piece left"""

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves
        """code that moves the pieces to the right"""

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves


class Game:
    """initializes game class"""

    def __init__(self, win):
        self._init()
        self.win = win

    """updates the display with new gamestates"""

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pg.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pg.draw.rect(self.win, BLUE,
                         pg.Rect(width - SQUARE_SIZE * (8 - col), height - SQUARE_SIZE * (8 - row), SQUARE_SIZE,
                                 SQUARE_SIZE))

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()








def minimax(position, depth, max_player, game):
    if depth == 0 or position.winner() != None:
        return position.evaluate(), position

    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, WHITE, game):
            evaluation = minimax(move, depth - 1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move

        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, RED, game):
            evaluation = minimax(move, depth - 1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move

        return minEval, best_move


def simulate_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)

    return board


def get_all_moves(board, color, game):
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            draw_moves(game, board, piece)
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, game, skip)
            moves.append(new_board)

    return moves


def draw_moves(game, board, piece):
    valid_moves = board.get_valid_moves(piece)
    board.draw(game.win)
    pg.draw.circle(game.win, (0, 255, 0), (piece.x, piece.y), 50, 5)
    game.draw_valid_moves(valid_moves.keys())
    pg.display.update()
    # pg.time.delay(100)


FPS = 60

WIN = pg.display.set_mode((width, height))
pg.display.set_caption('Checkers')
icon = pg.image.load("icon.png")
pg.display.set_icon(icon)


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    run = True
    clock = pg.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.turn == WHITE:
            value, new_board = minimax(game.get_board(), 4, WHITE, game)
            game.ai_move(new_board)

        if game.winner() != None:
            print(game.winner())
            run = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()

    pg.quit()


mode = input("BOT or BUDDY: ")
if mode == "BOT":
    main()
if mode == "BUDDY":
    # Set up the game and its window
    pg.init()
    width = 800
    dimensions = 8
    height = 800
    sqSize = height // dimensions
    display = pg.display.set_mode((width, height))
    pg.display.set_caption('Checkers')
    icon = pg.image.load("icon.png")
    pg.display.set_icon(icon)
    window = pg.display.set_mode((width, width))
    ut_left = 12
    tamu_left = 12
    ut_score = 0
    tamu_score = 0

    # Set up the images of the pieces to put onto the board
    Orange = pg.transform.scale(pg.image.load("u.png"), (sqSize, sqSize))
    Red = pg.transform.scale(pg.image.load("t.png"), (sqSize, sqSize))
    OrangeKing = pg.transform.scale(pg.image.load("ucrown.png"), (sqSize, sqSize))
    RedKing = pg.transform.scale(pg.image.load("crown.png"), (sqSize, sqSize))

    # Create colors for the board and highlighting
    WHITE, BLACK, ORANGE, BLUE = (169, 169, 169), (0, 0, 0), (235, 168, 52), (76, 252, 241)


    class Node:
        def __init__(self, row, col, width):
            self.row = row
            self.col = col
            self.x = int(row * width)
            self.y = int(col * width)
            self.colour = WHITE
            self.piece = None

        def draw(self, window):
            pg.draw.rect(window, self.colour, (self.x, self.y, width / dimensions, width / dimensions))
            if self.piece:
                window.blit(self.piece.image, (self.x, self.y))


    class Piece:
        def __init__(self, team):
            self.team = team
            self.image = Orange if self.team == "UT" else Red
            self.type = None


    def update_display(win, grid, rows, width):
        '''Display the chessboard with all elements onto the screen'''
        for row in grid:
            for spot in row:
                spot.draw(win)
        pg.display.update()


    def make_grid(rows, width):
        '''This function creates an array of the board and places the pieces to be utilized in calculations'''
        grid = []
        gap = width // rows
        count = 0
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                node = Node(j, i, gap)
                if abs(i - j) % 2 == 0:
                    node.colour = BLACK
                if (abs(i + j) % 2 == 0) and (i < 3):
                    node.piece = Piece("UT")
                elif (abs(i + j) % 2 == 0) and i > 4:
                    node.piece = Piece("TAMU")
                count = count + 1
                grid[i].append(node)
        return grid


    def getNode(grid, rows, width):
        '''This function obtains the square that the user clicked the mouse on'''
        gap = width // rows
        RowX, RowY = pg.mouse.get_pos()
        Row = RowX // gap
        Col = RowY // gap
        return (Col, Row)


    def reset_colors(grid, node):
        '''This function removes the previous highlighting on the board'''
        positions = createMoves(node, grid)
        positions.append(node)

        for colouredNodes in positions:
            nodeX, nodeY = colouredNodes
            grid[nodeX][nodeY].colour = BLACK if abs(nodeX - nodeY) % 2 == 0 else WHITE


    def color_moves(piecePosition, grid):
        '''This function colors the squares blue for possible moves in order to display the legal moves'''
        positions = createMoves(piecePosition, grid)
        for position in positions:
            Column, Row = position
            grid[Column][Row].colour = BLUE


    def opposite(team):
        '''This function will alternate the player turns'''
        return "UT" if team == "TAMU" else "TAMU"


    def createMoves(nodePosition, grid):
        '''This function utilizes the grid array to generate possible positions each piece can move'''
        checker = lambda x, y: x + y >= 0 and x + y < 8
        positions = []
        column, row = nodePosition
        if grid[column][row].piece:
            vectors = [[1, -1], [1, 1]] if grid[column][row].piece.team == "UT" else [[-1, -1], [-1, 1]]
            if grid[column][row].piece.type == 'KING':
                vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]
            for vector in vectors:
                columnVector, rowVector = vector
                if checker(columnVector, column) and checker(rowVector, row):
                    pass
                    if not grid[(column + columnVector)][(row + rowVector)].piece:
                        positions.append((column + columnVector, row + rowVector))
                    elif grid[column + columnVector][row + rowVector].piece and grid[column + columnVector][
                        row + rowVector].piece.team == opposite(grid[column][row].piece.team):
                        if checker((2 * columnVector), column) and checker((2 * rowVector), row) and not \
                                grid[(2 * columnVector) + column][(2 * rowVector) + row].piece:
                            positions.append((2 * columnVector + column, 2 * rowVector + row))
        return positions


    def highlight(ClickedNode, Grid, OldHighlight):
        '''This function highlights the possible moves and square clicked'''
        Column, Row = ClickedNode
        Grid[Column][Row].colour = ORANGE
        if OldHighlight:
            reset_colors(Grid, OldHighlight)
        color_moves(ClickedNode, Grid)
        return (Column, Row)


    def move(grid, piecePosition, newPosition):
        '''This function moves the pieces and images, determine if a piece has become a king, and handle taking pieces'''
        reset_colors(grid, piecePosition)
        newColumn, newRow = newPosition
        oldColumn, oldRow = piecePosition

        piece = grid[oldColumn][oldRow].piece
        grid[newColumn][newRow].piece = piece
        grid[oldColumn][oldRow].piece = None

        if newColumn == 7 and grid[newColumn][newRow].piece.team == "UT":
            grid[newColumn][newRow].piece.type = 'KING'
            grid[newColumn][newRow].piece.image = OrangeKing
        if newColumn == 0 and grid[newColumn][newRow].piece.team == "TAMU":
            grid[newColumn][newRow].piece.type = 'KING'
            grid[newColumn][newRow].piece.image = RedKing
        if abs(newColumn - oldColumn) == 2 or abs(newRow - oldRow) == 2:
            grid[int((newColumn + oldColumn) / 2)][int((newRow + oldRow) / 2)].piece = None
            global tamu_left
            global ut_left
            if piece.team == "UT":
                tamu_left -= 1
            elif piece.team == "TAMU":
                ut_left -= 1
            return grid[newColumn][newRow].piece.team
        return opposite(grid[newColumn][newRow].piece.team)


    def win():
        '''This function determines if a side has won if all pieces of a side is eliminated'''
        if tamu_left == 0:
            return "UT"
        elif ut_left == 0:
            return "TAMU"


    def main(width, dimensions):
        grid = make_grid(dimensions, width)
        highlightedPiece = None
        while True:
            try:
                turn = input("Who goes first (TAMU or UT): ")
                int(turn)
                print("You entered a number... 👎")
            except:
                if turn == "UT":
                    CurrentTurn = "UT"
                    break
                elif turn == "TAMU":
                    CurrentTurn = "TAMU"
                    break
                else:
                    print("Not the write input")
        running = True

        while running:
            if win() != None:
                print(win(), "won")
                if win() == "TAMU":
                    global tamu_score
                    tamu_score += 1
                elif win() == "UT":
                    global ut_score
                    ut_score += 1
                running = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    clickedNode = getNode(grid, dimensions, width)
                    ClickedPositionColumn, ClickedPositionRow = clickedNode
                    if grid[ClickedPositionColumn][ClickedPositionRow].colour == BLUE:
                        if highlightedPiece:
                            pieceColumn, pieceRow = highlightedPiece
                        if CurrentTurn == grid[pieceColumn][pieceRow].piece.team:
                            reset_colors(grid, highlightedPiece)
                            CurrentTurn = move(grid, highlightedPiece, clickedNode)
                    else:
                        if grid[ClickedPositionColumn][ClickedPositionRow].piece:
                            if CurrentTurn == grid[ClickedPositionColumn][ClickedPositionRow].piece.team:
                                highlightedPiece = highlight(clickedNode, grid, highlightedPiece)
            update_display(window, grid, dimensions, width)


    main(width, dimensions)

    print("Final score:")
    print("UT SCORE:", ut_score)
    print("TAMU SCORE:", tamu_score)