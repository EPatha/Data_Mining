import chess.pgn
import pandas as pd
from tkinter import Tk, Label, Button, filedialog, messagebox, Toplevel
from tkinter.ttk import Treeview

# Functions to process PGN files
def process_pgn_file(pgn_file_path, color):
    """Process PGN file and return a DataFrame with color information."""
    games_data = []
    with open(pgn_file_path) as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_info = game.headers
            game_moves = []
            board = game.board()
            for move in game.mainline_moves():
                game_moves.append(board.san(move))
                board.push(move)
            games_data.append({
                "White": game_info.get("White", "Unknown"),
                "Black": game_info.get("Black", "Unknown"),
                "Date": game_info.get("Date", "Unknown"),
                "Result": game_info.get("Result", "Unknown"),
                "Moves": " ".join(game_moves),
                "Color": color
            })
    return pd.DataFrame(games_data)

def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves."""
    df['First_Two_Moves'] = df['Moves'].apply(lambda x: ' '.join(x.split()[:2]))
    df['White_Result'] = df['Result'].map({'1-0': 1, '0-1': 0, '1/2-1/2': 0.5})
    df['Black_Result'] = df['Result'].map({'1-0': 0, '0-1': 1, '1/2-1/2': 0.5})

    white_win_rate = df[df['Color'] == 'White'].groupby('First_Two_Moves').agg(
        total_games_white=('White_Result', 'count'),
        white_win_rate=('White_Result', 'mean')
    ).reset_index()

    black_win_rate = df[df['Color'] == 'Black'].groupby('First_Two_Moves').agg(
        total_games_black=('Black_Result', 'count'),
        black_win_rate=('Black_Result', 'mean')
    ).reset_index()

    win_rate = pd.merge(white_win_rate, black_win_rate, on='First_Two_Moves', how='outer').fillna(0)
    win_rate.columns = ['Opening Move', 'Total Games White', 'Win Rate White', 'Total Games Black', 'Win Rate Black']
    return win_rate

# GUI Application class
class PGNAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess PGN Analyzer")
        self.root.geometry("600x400")

        # File paths
        self.white_pgn_file = None
        self.black_pgn_file = None
        self.win_rate_df = None

        # GUI Elements
        Label(root, text="Chess PGN Analyzer", font=("Arial", 16)).pack(pady=10)

        Button(root, text="Select White PGN File", command=self.select_white_pgn).pack(pady=5)
        Button(root, text="Select Black PGN File", command=self.select_black_pgn).pack(pady=5)
        Button(root, text="Analyze", command=self.analyze).pack(pady=10)
        Button(root, text="Save to Excel", command=self.save_to_excel).pack(pady=5)

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

        # Process PGN files
        df_white = process_pgn_file(self.white_pgn_file, 'White')
        df_black = process_pgn_file(self.black_pgn_file, 'Black')

        # Combine and analyze
        df_combined = pd.concat([df_white, df_black])
        self.win_rate_df = analyze_win_rate(df_combined)

        # Display result in new window
        self.display_results()

    def display_results(self):
        if self.win_rate_df is None:
            return

        # Create a new window
        result_window = Toplevel(self.root)
        result_window.title("Win Rate Analysis")
        result_window.geometry("800x400")

        tree = Treeview(result_window, columns=self.win_rate_df.columns, show='headings')
        tree.pack(fill='both', expand=True)

        # Set column headings
        for col in self.win_rate_df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Add rows
        for _, row in self.win_rate_df.iterrows():
            tree.insert('', 'end', values=list(row))

    def save_to_excel(self):
        if self.win_rate_df is None:
            messagebox.showerror("Error", "No data to save. Please run the analysis first.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            self.win_rate_df.to_excel(save_path, index=False)
            messagebox.showinfo("Success", f"Data saved to {save_path}")

# Main application execution
if __name__ == "__main__":
    root = Tk()
    app = PGNAnalyzerApp(root)
    root.mainloop()
