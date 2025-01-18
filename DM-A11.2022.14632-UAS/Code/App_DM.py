import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import chess.pgn
import pandas as pd
import os
import webbrowser

class ChessAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Analyzer")

        self.dataset_dir = "datasets"
        os.makedirs(self.dataset_dir, exist_ok=True)

        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the title with a dark background
        title_frame = tk.Frame(self.root, bg="darkblue")
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(title_frame, text="Chess Analyzer for Search your Weakness Opening", font=("Times New Rowman", 20, "bold"), fg="white", bg="darkblue")
        title_label.pack(pady=10)

        # Create a frame for the buttons
        button_frame = tk.Frame(self.root, bg="lightgray")
        button_frame.pack(fill=tk.X, pady=10)

        tutorial_button = tk.Button(button_frame, text="Tutorial", command=self.show_tutorial, width=20, bg="lightgreen")
        tutorial_button.pack(side=tk.LEFT, pady=5, padx=10)
        dataset_button = tk.Button(button_frame, text="Dataset (Google Drive)", command=self.open_dataset_link, width=20)
        dataset_button.pack(side=tk.LEFT, pady=5, padx=10)
        analyze_button = tk.Button(button_frame, text="Analyze", command=self.analyze, width=20)
        analyze_button.pack(side=tk.LEFT, pady=5, padx=10)

        # Create a frame for the split view
        split_frame = tk.Frame(self.root)
        split_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for white analysis
        left_frame = tk.Frame(split_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.white_pgn_label = tk.Label(left_frame, text="Select White PGN file", bg="white", fg="black")
        self.white_pgn_label.pack(pady=5)
        tk.Button(left_frame, text="Select White PGN", command=self.select_white_pgn, width=20).pack(pady=5)

        self.tree_white = ttk.Treeview(left_frame, columns=("Opening", "Games", "Win Rate (%)"), show="headings")
        self.tree_white.heading("Opening", text="Opening")
        self.tree_white.heading("Games", text="Games")
        self.tree_white.heading("Win Rate (%)", text="Win Rate (%)")
        self.tree_white.pack(fill=tk.BOTH, expand=True, pady=10)

        # Middle frame as a separator
        middle_frame = tk.Frame(split_frame, bg="lightgray", width=10)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right frame for black analysis
        right_frame = tk.Frame(split_frame, bg="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.black_pgn_label = tk.Label(right_frame, text="Select Black PGN file", bg="black", fg="white")
        self.black_pgn_label.pack(pady=5)
        tk.Button(right_frame, text="Select Black PGN", command=self.select_black_pgn, width=20).pack(pady=5)

        self.tree_black = ttk.Treeview(right_frame, columns=("Opening", "Games", "Win Rate (%)"), show="headings", style="Black.Treeview")
        self.tree_black.heading("Opening", text="Opening")
        self.tree_black.heading("Games", text="Games")
        self.tree_black.heading("Win Rate (%)", text="Win Rate (%)")
        self.tree_black.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add Close button
        close_button = tk.Button(self.root, text="Close", command=self.root.quit, bg="red", fg="white")
        close_button.place(relx=1.0, rely=0.0, anchor="ne")

        # Style for black treeview
        style = ttk.Style()
        style.configure("Black.Treeview", background="black", foreground="lightgray", fieldbackground="black")
        style.configure("Black.Treeview.Heading", background="black", foreground="lightgray")
        style.map("Black.Treeview", foreground=[('selected', 'lightgray')], background=[('selected', 'black')])

    def show_datasets(self):
        webbrowser.open("https://drive.google.com/drive/folders/1_FWcpYO7noxe5gpb_DLPTKnc2PVimuzu?usp=sharing")

    def select_white_pgn(self):
        self.white_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        self.white_pgn_label.config(text=self.white_pgn_path)

    def select_black_pgn(self):
        self.black_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        self.black_pgn_label.config(text=self.black_pgn_path)

    def select_dataset(self):
        dataset_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if dataset_path:
            messagebox.showinfo("Dataset Selected", f"Dataset file selected: {dataset_path}")

    def analyze(self):
        if not hasattr(self, 'white_pgn_path') or not hasattr(self, 'black_pgn_path'):
            messagebox.showerror("Error", "Please select both White and Black PGN files.")
            return

        white_games = self.load_pgn(self.white_pgn_path)
        black_games = self.load_pgn(self.black_pgn_path)

        self.white_analysis = self.compute_win_rates(white_games, "white")
        self.black_analysis = self.compute_win_rates(black_games, "black")

        self.display_results()

    def load_pgn(self, pgn_path):
        games = []
        with open(pgn_path) as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                moves = [move.uci() for move in game.mainline_moves()]
                result = game.headers["Result"]
                games.append({"Moves": moves, "Result": result})
        return games

    def compute_win_rates(self, data, color):
        openings = {}
        for game in data:
            if len(game["Moves"]) < 2:
                continue
            opening = " ".join([game["Moves"][0][2:], game["Moves"][1][2:]])
            if opening not in openings:
                openings[opening] = {"games": 0, "wins": 0}
            openings[opening]["games"] += 1
            if (color == "white" and game["Result"] == "1-0") or (color == "black" and game["Result"] == "0-1"):
                openings[opening]["wins"] += 1

        analysis = []
        for opening, stats in openings.items():
            if stats["games"] >= 30:  # Filter to include only openings with 30 or more games
                win_rate = (stats["wins"] / stats["games"]) * 100
                analysis.append({"Opening": opening, "Games": stats["games"], "Win Rate (%)": win_rate})

        return pd.DataFrame(analysis)

    def display_results(self):
        for row in self.tree_white.get_children():
            self.tree_white.delete(row)

        for row in self.tree_black.get_children():
            self.tree_black.delete(row)

        for _, row in self.white_analysis.iterrows():
            self.tree_white.insert("", tk.END, values=(row["Opening"], row["Games"], row["Win Rate (%)"]))

        for _, row in self.black_analysis.iterrows():
            self.tree_black.insert("", tk.END, values=(row["Opening"], row["Games"], row["Win Rate (%)"]))

        # Display evaluation
        white_least_winrate = self.white_analysis.loc[self.white_analysis["Win Rate (%)"].idxmin()]
        black_least_winrate = self.black_analysis.loc[self.black_analysis["Win Rate (%)"].idxmin()]

        evaluation_text = (
            f"Hasil Evaluasi:\n"
            f"Pembukaan Putih yang perlu dipelajari = {white_least_winrate['Opening']} "
            f"(Win Rate: {white_least_winrate['Win Rate (%)']:.2f}%)\n"
            f"Pembukaan Hitam yang perlu dipelajari = {black_least_winrate['Opening']} "
            f"(Win Rate: {black_least_winrate['Win Rate (%)']:.2f}%)"
        )
        messagebox.showinfo("Hasil Evaluasi", evaluation_text)

    def show_tutorial(self):
        tutorial_text = (
            "Cara Menggunakan Chess Analyzer:\n"
            "1. Dapatkan file PGN dari permainan catur. \n"
            "   (Klik tombol 'Dataset' untuk membuka link Google Drive yang berisi dataset PGN yang tersedia untuk diunduh.)\n"
            "   Atau\n"
            "   (Anda bisa mendapatkan file PGN pribadi atau orang lain dari situs seperti lichess.com atau chess.com.\n"
            "   Pergi ke situs openingtree.com dan masukkan nickname Anda untuk menganalisis permainan Anda.\n"
            "   Setelah analisis selesai, unduh file PGN dari situs tersebut).\n"
            "2. Klik 'Select White PGN' untuk memilih file PGN permainan Anda sebagai putih.\n"
            "3. Klik 'Select Black PGN' untuk memilih file PGN permainan Anda sebagai hitam.\n"
            "4. Setelah kedua file PGN dipilih, klik tombol 'Analyze'.\n"
            "5. Aplikasi akan menganalisis permainan Anda dan menampilkan hasilnya di tabel.\n"
            "6. Hasil evaluasi akan menunjukkan pembukaan yang perlu Anda pelajari lebih lanjut berdasarkan win rate.\n"
        )
        messagebox.showinfo("Tutorial", tutorial_text)

    def open_dataset_link(self):
        webbrowser.open("https://drive.google.com/drive/folders/1_FWcpYO7noxe5gpb_DLPTKnc2PVimuzu?usp=sharing")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessAnalyzerApp(root)
    root.mainloop()