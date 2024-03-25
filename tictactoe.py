"""A tic-tac-toe game built with Python and Tkinter."""

import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green"),
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def has_winner(self):
        """Return True if the game has a winner, and False otherwise."""
        return self._has_winner

    def toggle_player(self):
        """Return a toggled player."""
        self.current_player = next(self._players)

    def reset_game(self):
        """Reset the game state to play again."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
        
    def ai(self, cells_left):
        best_score = -float("inf")
        best_move = None
        max_cells = self.board_size**2

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self._current_moves[row][col].label == "":
                    self._current_moves[row][col] = Move(row, col, "O")  # Simulate move for AI
                    score = self.minimax(False, -float("inf"), float("inf"),2 + int(((max_cells - cells_left) / max_cells) * 2) )
                    self._current_moves[row][col] = Move(row, col)  # Undo move

                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        return best_move

    def minimax(self, is_maximizing, alpha, beta, max_depth, depth=0):
        winner, _ = self.get_winner()
        if max_depth == depth or winner is not None:
            if winner == "X":
                return -10+depth
            elif winner == "O":
                return 10-depth
            elif winner == "TIE":
                return 0
            else:
                return self.heuristic_evaluation()

        if is_maximizing:
            best_score = -float("inf")
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self._current_moves[row][col].label == "":
                        self._current_moves[row][col] = Move(row, col, "O")  # Simulate move for AI
                        score = self.minimax(False, alpha, beta, max_depth, depth + 1)
                        self._current_moves[row][col] = Move(row, col)  # Undo move

                        best_score = max(best_score, score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
            return best_score
        else:
            best_score = float("inf")
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self._current_moves[row][col].label == "":
                        self._current_moves[row][col] = Move(row, col, "X")  # Simulate move for opponent
                        score = self.minimax(True, alpha, beta, max_depth, depth + 1)
                        self._current_moves[row][col] = Move(row, col)  # Undo move

                        best_score = min(best_score, score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
            return best_score
        
    def heuristic_evaluation(self):
        player_score = 0
        opponent_score = 0

        for combo in self._winning_combos:
            player_in_combo = any(self._current_moves[r][c].label == "O" for r, c in combo)
            opponent_in_combo = any(self._current_moves[r][c].label == "X" for r, c in combo)
            
            # Line is open for the AI player
            if player_in_combo and not opponent_in_combo:
                player_score += 1
            # Line is open for the opponent
            elif opponent_in_combo and not player_in_combo:
                opponent_score += 1

        return player_score - opponent_score


    def get_winner(self):
        # Check for a winner
        for combo in self._winning_combos:
            if all(self._current_moves[n][m].label == "X" for n, m in combo):
                return "X",combo
            if all(self._current_moves[n][m].label == "O" for n, m in combo):
                return "Y", combo

        # Check for a tie if no winner
        if all(move.label for row in self._current_moves for move in row):
            return "TIE", []

        # No winner and no tie means the game is still in progress
        return None, []        


class TicTacToeBoard(tk.Tk):
    def __init__(self, game, board_size):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._cells_left = board_size**2
        self._buttons = {}
        self._game = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="Menu", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                self._buttons[(row, col)] = button
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)

        # Exit if the move is not valid
        if not self._game.is_valid_move(move):
            return 

        # Update the board and check the game state
        self._update_button(clicked_btn, self._game.current_player.label, self._game.current_player.color)
        self._game._current_moves[row][col] = move  
        winner, winner_combo = self._game.get_winner()
        self._cells_left -= 1

        if winner:
            self._handle_game_end(winner, winner_combo)
        else:
            self._game.toggle_player()
            self._update_display(f"{self._game.current_player.label}'s turn")
            self._handle_ai_move()
            self._cells_left -= 1

    def _update_button(self, button, label, color):
        """Update the button text and disable it."""
        button.config(text=label)
        button.config(fg=color)

    def _handle_game_end(self, winner, winner_combo):
        """Handle the end of the game, whether win or tie."""
        if winner == "TIE":
            self._update_display(msg="Tied game!", color="red")
        else:
            self._game._has_winner = True
            self._highlight_cells(winner_combo)
            msg = f'Player "{winner}" won!'
            color = "red" if winner == "X" else "green"
            self._update_display(msg, color)

    def _handle_ai_move(self):
        """Handle the AI move."""
        row, col = self._game.ai(self._cells_left)
        move = Move(row, col, "O")
        
        self._update_button(self._buttons[(row, col)], self._game.current_player.label, self._game.current_player.color)
        self._game._current_moves[row][col] = move  
        
        winner, winner_combo = self._game.get_winner()
        if winner:
            self._handle_game_end(winner, winner_combo)
        else:
            self._game.toggle_player()
            self._update_display(f"{self._game.current_player.label}'s turn")


    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self, winner_combo):
        for button, coordinates in self._cells.items():
            if coordinates in winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        """Reset the game's board to play again."""
        self._game.reset_game()
        self._update_display(msg="Ready?")
        if(self._game.current_player.label == "O"):
            self._game.toggle_player()
        self._cells_left = self._game.board_size**2
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")


def main():
    """Create the game's board and run its main loop."""
    size = 3
    game = TicTacToeGame(board_size=size)
    board = TicTacToeBoard(game,board_size=size)
    board.mainloop()


if __name__ == "__main__":
    main()