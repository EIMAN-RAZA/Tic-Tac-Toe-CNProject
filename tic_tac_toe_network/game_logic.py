def create_board():
    return [["" for _ in range(3)] for _ in range(3)]

def make_move(board, row, col, player):
    if board[row][col] == "":
        board[row][col] = player
        return True
    return False

def check_win(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)) or all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def check_draw(board):
    return all(cell != "" for row in board for cell in row)