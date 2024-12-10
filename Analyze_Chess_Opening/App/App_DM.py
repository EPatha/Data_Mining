import chess.pgn
import pandas as pd
from tkinter import Tk, Label, Button, filedialog, messagebox, Toplevel, Text
from tkinter.ttk import Treeview


def process_pgn_file(pgn_file_path, color):
    """Process PGN file and return a DataFrame with color information."""
    games_data = []
    with open(pgn_file_path) as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_info = game.headers
            white_moves = []
            black_moves = []
            board = game.board()
            for move in game.mainline_moves():
                move_san = board.san(move)
                if board.turn == chess.WHITE:
                    white_moves.append(move_san)
                else:
                    black_moves.append(move_san)
                board.push(move)

            games_data.append({
                "White": game_info.get("White", "Unknown"),
                "Black": game_info.get("Black", "Unknown"),
                "Date": game_info.get("Date", "Unknown"),
                "Result": game_info.get("Result", "Unknown"),
                "White_Moves": " ".join(white_moves),
                "Black_Moves": " ".join(black_moves),
                "Color": color
            })
    return pd.DataFrame(games_data)


def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves."""
    df['White_First_Two_Moves'] = df['White_Moves'].apply(lambda x: ' '.join(x.split()[:2]))
    df['Black_First_Two_Moves'] = df['Black_Moves'].apply(lambda x: ' '.join(x.split()[:2]))
    
    df['White_Result'] = df['Result'].map({'1-0': 1, '0-1': 0, '1/2-1/2': 0.5})
    df['Black_Result'] = df['Result'].map({'1-0': 0, '0-1': 1, '1/2-1/2': 0.5})

    white_win_rate = df[df['Color'] == 'White'].groupby('White_First_Two_Moves').agg(
        total_games_white=('White_Result', 'count'),
        white_win_rate=('White_Result', 'mean')
    ).reset_index()

    black_win_rate = df[df['Color'] == 'Black'].groupby('Black_First_Two_Moves').agg(
        total_games_black=('Black_Result', 'count'),
        black_win_rate=('Black_Result', 'mean')
    ).reset_index()

    win_rate = pd.merge(white_win_rate, black_win_rate, left_on='White_First_Two_Moves', right_on='Black_First_Two_Moves', how='outer').fillna(0)
    win_rate['Total Games'] = win_rate['total_games_white'] + win_rate['total_games_black']

    # Tentukan nama kolom secara eksplisit
    win_rate.columns = ['Opening Move', 'Total Games White', 'Win Rate White', 
                        'Total Games Black', 'Win Rate Black', 'Total Games']

    most_used_openings = win_rate[win_rate['Total Games'] > 20].sort_values(by='Total Games', ascending=False)
    overall_win_rate = win_rate[win_rate['Total Games'] <= 20]

    return overall_win_rate, most_used_openings




class PGNAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess PGN Analyzer")
        self.root.geometry("800x600")

        self.white_pgn_file = None
        self.black_pgn_file = None
        self.overall_win_rate_df = None
        self.most_used_openings_df = None

        Label(root, text="Chess PGN Analyzer", font=("Arial", 16)).pack(pady=10)

        Button(root, text="Select White PGN File", command=self.select_white_pgn).pack(pady=5)
        Button(root, text="Select Black PGN File", command=self.select_black_pgn).pack(pady=5)
        Button(root, text="Analyze", command=self.analyze).pack(pady=10)
        Button(root, text="Save to Excel", command=self.save_to_excel).pack(pady=5)

        self.tree = Treeview(root, show='headings')
        self.tree.pack(fill='both', expand=True, pady=10)

        self.summary_text = Text(root, height=5)
        self.summary_text.pack(fill='x', pady=10)

    def select_white_pgn(self):
        self.white_pgn_file = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.white_pgn_file:
            messagebox.showinfo("File Selected", f"White PGN file selected: {self.white_pgn_file}")

    def select_black_pgn(self):
        self.black_pgn_file = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.black_pgn_file:
            messagebox.showinfo("File Selected", f"Black PGN file selected: {self.black_pgn_file}")

    def analyze(self):
        if not self.white_pgn_file or not self.black_pgn_file:
            messagebox.showerror("Error", "Please select both White and Black PGN files.")
            return

        df_white = process_pgn_file(self.white_pgn_file, 'White')
        df_black = process_pgn_file(self.black_pgn_file, 'Black')

        df_combined = pd.concat([df_white, df_black])
        self.overall_win_rate_df, self.most_used_openings_df = analyze_win_rate(df_combined)

        self.display_results()

    def display_results(self):
        """Display analysis results in treeview."""
        if 'Win Rate White' in self.most_used_openings_df.columns and 'Win Rate Black' in self.most_used_openings_df.columns:
            lowest_accuracy = min(self.most_used_openings_df['Win Rate White'].min(), self.most_used_openings_df['Win Rate Black'].min())
        else:
            lowest_accuracy = "N/A"
    
        # Lanjutkan dengan proses menampilkan hasil seperti biasa
        self.display_treeview(self.most_used_openings_df, "Most Used Openings", True)


    def display_treeview(self, df, title, add_summary=False):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=list(row))

        if add_summary:
            self.summary_text.delete(1.0, "end")
            lowest_accuracy = min(df['Win Rate White'].min(), df['Win Rate Black'].min())
            color = 'White' if df['Win Rate White'].min() < df['Win Rate Black'].min() else 'Black'
            summary = f"The color with the lowest accuracy is {color} with a rate of {lowest_accuracy:.2%}."
            self.summary_text.insert('end', summary)

    def show_summary(self):
        if self.overall_win_rate_df is None or self.most_used_openings_df is None:
            return

        lowest_accuracy = min(self.most_used_openings_df['Win Rate White'].min(), self.most_used_openings_df['Win Rate Black'].min())
        color = 'White' if self.most_used_openings_df['Win Rate White'].min() < self.most_used_openings_df['Win Rate Black'].min() else 'Black'
        summary = f"The color with the lowest accuracy is {color} with a rate of {lowest_accuracy:.2%}."
        self.summary_text.delete(1.0, "end")
        self.summary_text.insert('end', summary)

    def save_to_excel(self):
        if self.overall_win_rate_df is None or self.most_used_openings_df is None:
            messagebox.showerror("Error", "No data to save. Please run the analysis first.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            with pd.ExcelWriter(save_path) as writer:
                self.most_used_openings_df.to_excel(writer, sheet_name="Most Used Openings", index=False)
                self.overall_win_rate_df.to_excel(writer, sheet_name="Overall Win Rate", index=False)
            messagebox.showinfo("Success", f"Data saved to {save_path}")


if __name__ == "__main__":
    root = Tk()
    app = PGNAnalyzerApp(root)
    root.mainloop()
