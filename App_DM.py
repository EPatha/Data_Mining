import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import chess.pgn
import pandas as pd

class ChessAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Opening Analyzer")

        # UI Elements
        self.white_pgn_label = tk.Label(root, text="White PGN File: None")
        self.white_pgn_label.pack(pady=5)

        self.white_pgn_button = tk.Button(root, text="Select White PGN", command=self.select_white_pgn)
        self.white_pgn_button.pack(pady=5)

        self.black_pgn_label = tk.Label(root, text="Black PGN File: None")
        self.black_pgn_label.pack(pady=5)

        self.black_pgn_button = tk.Button(root, text="Select Black PGN", command=self.select_black_pgn)
        self.black_pgn_button.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.analyze)
        self.analyze_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save to Excel", command=self.save_to_excel, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("Opening", "Games", "White Win Rate", "Black Win Rate"), show='headings')
        self.tree.heading("Opening", text="Opening")
        self.tree.heading("Games", text="Games")
        self.tree.heading("White Win Rate", text="White Win Rate (%)")
        self.tree.heading("Black Win Rate", text="Black Win Rate (%)")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.white_pgn_path = None
        self.black_pgn_path = None
        self.analysis_data = None

    def select_white_pgn(self):
        self.white_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.white_pgn_path:
            self.white_pgn_label.config(text=f"White PGN File: {self.white_pgn_path}")

    def select_black_pgn(self):
        self.black_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.black_pgn_path:
            self.black_pgn_label.config(text=f"Black PGN File: {self.black_pgn_path}")

    def analyze(self):
        if not self.white_pgn_path or not self.black_pgn_path:
            messagebox.showerror("Error", "Please select both White and Black PGN files.")
            return

        white_data = self.process_pgn(self.white_pgn_path)
        black_data = self.process_pgn(self.black_pgn_path)

        if not white_data or not black_data:
            messagebox.showerror("Error", "Unable to process one or both PGN files.")
            return

        self.analysis_data = self.compute_win_rates(white_data, black_data)
        self.display_results()
        self.save_button.config(state=tk.NORMAL)

    def process_pgn(self, pgn_path):
        data = []
        try:
            with open(pgn_path, "r") as file:
                while True:
                    game = chess.pgn.read_game(file)
                    if game is None:
                        break
                    moves = list(game.mainline_moves())
                    result = game.headers.get("Result", "*")
                    data.append((moves, result))
        except Exception as e:
            print(f"Error processing PGN file: {e}")
            return None
        return data

    def compute_win_rates(self, white_data, black_data):
        openings = {}

        for data, color in [(white_data, "white"), (black_data, "black")]:
            for moves, result in data:
                if len(moves) < 2:
                    continue
                opening = " ".join([str(moves[0]), str(moves[1])])
                if opening not in openings:
                    openings[opening] = {"games": 0, "white_wins": 0, "black_wins": 0}

                openings[opening]["games"] += 1
                if result == "1-0":
                    openings[opening]["white_wins"] += 1 if color == "white" else 0
                elif result == "0-1":
                    openings[opening]["black_wins"] += 1 if color == "black" else 0

        result_list = []
        for opening, stats in openings.items():
            games = stats["games"]
            white_win_rate = (stats["white_wins"] / games * 100) if games > 0 else 0
            black_win_rate = (stats["black_wins"] / games * 100) if games > 0 else 0

            if games >= 30:  # Filter for minimum games
                result_list.append((opening, games, round(white_win_rate, 2), round(black_win_rate, 2)))

        return result_list

    def display_results(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for entry in self.analysis_data:
            self.tree.insert("", tk.END, values=entry)

    def save_to_excel(self):
        if not self.analysis_data:
            messagebox.showerror("Error", "No data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        df = pd.DataFrame(self.analysis_data, columns=["Opening", "Games", "White Win Rate (%)", "Black Win Rate (%)"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Results saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessAnalysisApp(root)
    root.mainloop()
