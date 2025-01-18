import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import chess.pgn
import pandas as pd
from tkinter import font
import os

class ChessAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Opening Analyzer")
        self.root.geometry("800x1500")

        # Font settings
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        section_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Close button
        self.close_button = tk.Button(root, text="X", command=self.root.quit, bg="red", fg="white", font=section_font)
        self.close_button.place(relx=1.0, rely=0.0, anchor="ne")

        # Section for White PGN
        self.white_frame = ttk.LabelFrame(root, text="White PGN", padding=10)
        self.white_frame.pack(fill=tk.X, padx=10, pady=5)

        self.white_pgn_label = tk.Label(self.white_frame, text="File: None", font=section_font)
        self.white_pgn_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.white_pgn_button = tk.Button(self.white_frame, text="Select PGN", command=self.select_white_pgn, width=10)
        self.white_pgn_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Section for Black PGN
        self.black_frame = ttk.LabelFrame(root, text="Black PGN", padding=10)
        self.black_frame.pack(fill=tk.X, padx=10, pady=5)

        self.black_pgn_label = tk.Label(self.black_frame, text="File: None", font=section_font)
        self.black_pgn_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.black_pgn_button = tk.Button(self.black_frame, text="Select PGN", command=self.select_black_pgn, width=10)
        self.black_pgn_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Action buttons
        self.action_frame = ttk.Frame(root, padding=10)
        self.action_frame.pack(fill=tk.X, padx=10, pady=5)

        self.analyze_button = tk.Button(self.action_frame, text="Analyze", command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.filter_button = tk.Button(self.action_frame, text="Most Used Opening", command=self.filter_most_used_openings)
        self.filter_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.action_frame, text="Save to Excel", command=self.save_to_excel, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Results TreeView
        self.result_frame = ttk.LabelFrame(root, text="Results", padding=10)
        self.result_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        self.tree = ttk.Treeview(self.result_frame, columns=("Opening", "Games", "Win Rate (%)"), show='headings', height=15)
        self.tree.heading("Opening", text="Opening")
        self.tree.heading("Games", text="Games")
        self.tree.heading("Win Rate (%)", text="Win Rate (%)")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Variables to store file paths and analysis
        self.white_pgn_path = None
        self.black_pgn_path = None
        self.white_analysis = None
        self.black_analysis = None

    def select_white_pgn(self):
        self.white_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.white_pgn_path:
            self.white_pgn_label.config(text=f"File: {self.white_pgn_path}")

    def select_black_pgn(self):
        self.black_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.black_pgn_path:
            self.black_pgn_label.config(text=f"File: {self.black_pgn_path}")

    def analyze(self):
        if not self.white_pgn_path or not self.black_pgn_path:
            messagebox.showerror("Error", "Please select both White and Black PGN files.")
            return

        white_data = self.process_pgn(self.white_pgn_path)
        black_data = self.process_pgn(self.black_pgn_path)

        if not white_data or not black_data:
            messagebox.showerror("Error", "Unable to process one or both PGN files.")
            return

        self.white_analysis = self.compute_win_rates(white_data, "white")
        self.black_analysis = self.compute_win_rates(black_data, "black")
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

    def compute_win_rates(self, data, color):
        openings = {}

        for moves, result in data:
            if len(moves) < 2:
                continue
            opening = " ".join([str(moves[0]), str(moves[1])])
            if opening not in openings:
                openings[opening] = {"games": 0, "wins": 0}

            openings[opening]["games"] += 1
            if (result == "1-0" and color == "white") or (result == "0-1" and color == "black"):
                openings[opening]["wins"] += 1

        result_list = []
        for opening, stats in openings.items():
            games = stats["games"]
            win_rate = (stats["wins"] / games * 100) if games > 0 else 0
            result_list.append((opening, games, round(win_rate, 2)))

        return result_list

    def display_results(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add header for White results
        self.tree.insert("", tk.END, values=("White:", "", ""), tags=("header",))
        for entry in self.white_analysis:
            self.tree.insert("", tk.END, values=entry, tags=("white",))

        # Add a separator row
        self.tree.insert("", tk.END, values=("", "", ""), tags=("separator",))

        # Add header for Black results
        self.tree.insert("", tk.END, values=("Black:", "", ""), tags=("header",))
        for entry in self.black_analysis:
            self.tree.insert("", tk.END, values=entry, tags=("black",))

        # Apply styles
        self.tree.tag_configure("header", font=("Helvetica", 12, "bold"), background="#f0f0f0")
        self.tree.tag_configure("white", background="#e6f7ff")
        self.tree.tag_configure("black", background="#fff3e6")
        self.tree.tag_configure("separator", background="#ffffff")

    def filter_most_used_openings(self):
        if not self.white_analysis or not self.black_analysis:
            messagebox.showerror("Error", "No data to filter. Please analyze first.")
            return

        self.white_analysis = [entry for entry in self.white_analysis if entry[1] >= 30]
        self.black_analysis = [entry for entry in self.black_analysis if entry[1] >= 30]

        self.display_results()

    def save_to_excel(self):
        if not self.white_analysis or not self.black_analysis:
            messagebox.showerror("Error", "No data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        white_df = pd.DataFrame(self.white_analysis, columns=["Opening", "Games", "Win Rate (%)"])
        black_df = pd.DataFrame(self.black_analysis, columns=["Opening", "Games", "Win Rate (%)"])

        with pd.ExcelWriter(file_path) as writer:
            white_df.to_excel(writer, sheet_name="White", index=False)
            black_df.to_excel(writer, sheet_name="Black", index=False)

        messagebox.showinfo("Success", f"Results saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessAnalysisApp(root)
    root.mainloop()