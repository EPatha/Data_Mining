import streamlit as st
import chess.pgn
import pandas as pd
import os
import io

def load_pgn(uploaded_file):
    games = []
    pgn_content = uploaded_file.read().decode("utf-8")
    pgn_file = io.StringIO(pgn_content)
    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        moves = [move.uci() for move in game.mainline_moves()]
        result = game.headers["Result"]
        games.append({"Moves": moves, "Result": result})
    return games

def compute_win_rates(data, color):
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

def main():
    st.title("Chess Analyzer for Search your Weakness Opening")

    st.markdown(
        """
        Dataset berada di link ini, download dulu di link Google Drive tersebut:
        [Google Drive Dataset](https://drive.google.com/drive/folders/1_FWcpYO7noxe5gpb_DLPTKnc2PVimuzu?usp=sharing)
        """
    )

    st.sidebar.title("Options")
    tutorial_button = st.sidebar.button("Tutorial")
    if tutorial_button:
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
        st.info(tutorial_text)

    white_pgn_file = st.sidebar.file_uploader("Select White PGN file", type=["pgn"])
    black_pgn_file = st.sidebar.file_uploader("Select Black PGN file", type=["pgn"])

    if st.sidebar.button("Analyze"):
        if white_pgn_file is None or black_pgn_file is None:
            st.error("Please select both White and Black PGN files.")
            return

        white_games = load_pgn(white_pgn_file)
        black_games = load_pgn(black_pgn_file)

        white_analysis = compute_win_rates(white_games, "white")
        black_analysis = compute_win_rates(black_games, "black")

        st.subheader("White Analysis")
        st.dataframe(white_analysis)

        st.subheader("Black Analysis")
        st.dataframe(black_analysis)

        white_least_winrate = white_analysis.loc[white_analysis["Win Rate (%)"].idxmin()]
        black_least_winrate = black_analysis.loc[black_analysis["Win Rate (%)"].idxmin()]

        st.subheader("Hasil Evaluasi")
        st.write(f"Pembukaan Putih yang perlu dipelajari = {white_least_winrate['Opening']} (Win Rate: {white_least_winrate['Win Rate (%)']:.2f}%)")
        st.write(f"Pembukaan Hitam yang perlu dipelajari = {black_least_winrate['Opening']} (Win Rate: {black_least_winrate['Win Rate (%)']:.2f}%)")

if __name__ == "__main__":
    main()