import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from game_logic import *

HOST = 'localhost'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

player_symbol = "O"
opponent_symbol = "X"
your_turn = False
board = create_board()
score = {"wins": 0, "losses": 0, "draws": 0}

# 🎮 GUI setup
root = tk.Tk()
root.title("Tic Tac Toe - Client")

# 💬 Ask for player name (Client)
player_name = simpledialog.askstring("Enter Name", "Enter name (Player 2):", parent=root)
if not player_name:
    player_name = "Player O"
client.send(player_name.encode())  # Send client name to server

# 👂 Receive opponent's name (Server)
opponent_name = client.recv(1024).decode()

# 🎯 Show both names
name_label = tk.Label(root, text=f"{opponent_name} (X) vs {player_name} (O)", font=("Arial", 14, "bold"))
name_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

buttons = [[None for _ in range(3)] for _ in range(3)]
score_label = tk.Label(root, text="Wins: 0  Losses: 0  Draws: 0", font=("Arial", 12))
score_label.grid(row=4, column=0, columnspan=3)

def update_score_label():
    score_label.config(text=f"Wins: {score['wins']}  Losses: {score['losses']}  Draws: {score['draws']}")

def update_buttons():
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text=board[i][j])

def animate_button_press(button):
    button.config(bg='lightpink')
    root.after(100, lambda: button.config(bg='mistyrose'))

def on_button_click(row, col):
    global your_turn
    if your_turn and board[row][col] == "":
        make_move(board, row, col, player_symbol)
        animate_button_press(buttons[row][col])
        update_buttons()
        client.send(f"{row},{col}".encode())
        your_turn = False

        if check_win(board, player_symbol):
            score["wins"] += 1
            update_score_label()
            messagebox.showinfo("Game Over", f"🎉 {player_name} wins!")
            client.send("WIN".encode())
        elif check_draw(board):
            score["draws"] += 1
            update_score_label()
            messagebox.showinfo("Game Over", "🤝 It’s a draw!")
            client.send("DRAW".encode())

def reset_game():
    global board, your_turn
    board = create_board()
    your_turn = player_symbol == "X"
    update_buttons()

def rematch():
    reset_game()
    client.send("READY".encode())

def receive_move():
    global your_turn
    while True:
        data = client.recv(1024).decode()
        if data in ["WIN", "DRAW"]:
            if data == "WIN":
                score["losses"] += 1
                update_score_label()
                messagebox.showinfo("Game Over", f"💀 {opponent_name} wins!")
            else:
                score["draws"] += 1
                update_score_label()
                messagebox.showinfo("Game Over", "🤝 It’s a draw!")
            reset_game()
            client.send("READY".encode())

        elif data == "READY":
            reset_game()

        else:
            row, col = map(int, data.split(","))
            make_move(board, row, col, opponent_symbol)
            animate_button_press(buttons[row][col])
            update_buttons()
            your_turn = True

# 🎀 Create buttons with pastel style
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(root, text="", font=('Arial', 24), width=5, height=2,
                                  bg='mistyrose', activebackground='lightpink',
                                  command=lambda r=i, c=j: on_button_click(r, c))
        buttons[i][j].grid(row=i+1, column=j)  # Push down for name label

threading.Thread(target=receive_move, daemon=True).start()

root.mainloop()
