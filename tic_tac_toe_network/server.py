import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from game_logic import *

HOST = 'localhost'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

player_symbol = "X"
opponent_symbol = "O"
your_turn = True
board = create_board()
score = {"wins": 0, "losses": 0, "draws": 0}

# GUI setup
root = tk.Tk()
root.title("Tic Tac Toe - Server")

# 🎯 Ask for server player name
player_name = simpledialog.askstring("Enter Name", "Enter name (Player 1):", parent=root)
if not player_name:
    player_name = "Player X"

# Accept connection first
client_conn, client_addr = None, None

def update_score_label():
    score_label.config(text=f"Wins: {score['wins']}  Losses: {score['losses']}  Draws: {score['draws']}")

def update_buttons():
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text=board[i][j])

def animate_button_press(button):
    button.config(bg='lightblue')
    root.after(100, lambda: button.config(bg='lightcyan'))

def on_button_click(row, col):
    global your_turn
    if client_conn and your_turn and board[row][col] == "":
        make_move(board, row, col, player_symbol)
        animate_button_press(buttons[row][col])
        update_buttons()
        client_conn.send(f"{row},{col}".encode())
        your_turn = False

        if check_win(board, player_symbol):
            score["wins"] += 1
            update_score_label()
            messagebox.showinfo("Game Over", f"🎉 {player_name} wins!")
            client_conn.send("WIN".encode())
        elif check_draw(board):
            score["draws"] += 1
            update_score_label()
            messagebox.showinfo("Game Over", "🤝 It’s a draw!")
            client_conn.send("DRAW".encode())

def reset_game():
    global board, your_turn
    board = create_board()
    your_turn = player_symbol == "X"
    update_buttons()

def rematch():
    reset_game()
    if client_conn:
        client_conn.send("READY".encode())

def receive_move():
    global your_turn
    while True:
        try:
            data = client_conn.recv(1024).decode()
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
                client_conn.send("READY".encode())

            elif data == "READY":
                reset_game()

            else:
                row, col = map(int, data.split(","))
                make_move(board, row, col, opponent_symbol)
                animate_button_press(buttons[row][col])
                update_buttons()
                your_turn = True
        except:
            break  # Client disconnected

def accept_connection():
    global client_conn, client_addr, opponent_name
    print("Waiting for a connection...")
    client_conn, client_addr = server_socket.accept()
    print(f"Connected by {client_addr}")

    # 👂 Receive client name
    opponent_name = client_conn.recv(1024).decode()

    # 📤 Send server's name to client
    client_conn.send(player_name.encode())

    # 🎯 Show both names
    name_label.config(text=f"{player_name} (X) vs {opponent_name} (O)")

    threading.Thread(target=receive_move, daemon=True).start()

# 🎯 Top label for names
name_label = tk.Label(root, text="Waiting for players...", font=("Arial", 14, "bold"))
name_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

# 🎀 Buttons setup
buttons = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(root, text="", font=('Arial', 24), width=5, height=2,
                                  bg='lightcyan', activebackground='lightblue',
                                  command=lambda r=i, c=j: on_button_click(r, c))
        buttons[i][j].grid(row=i+1, column=j)

# 📊 Scoreboard
score_label = tk.Label(root, text="Wins: 0  Losses: 0  Draws: 0", font=("Arial", 12))
score_label.grid(row=4, column=0, columnspan=3)

# 🧠 Start the connection thread
threading.Thread(target=accept_connection, daemon=True).start()

root.mainloop()
