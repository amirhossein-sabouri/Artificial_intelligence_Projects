# import json
# import os
# import webbrowser
# from isolation import Board
# from sample_players import RandomPlayer, GreedyPlayer
# from game_agent import AlphaBetaPlayer, MinimaxPlayer, ExpectimaxPlayer, custom_score, custom_score_2, custom_score_3


# # You can also import your custom AI player:
# # from my_custom_player import AlphaBetaPlayer

# # --- 1. Setup players ---
# # player1 = RandomPlayer()
# player1 = AlphaBetaPlayer(search_depth=3, score_fn=custom_score, timeout=15.)
# player2 = MinimaxPlayer(search_depth=2, score_fn=custom_score_2, timeout=15.)

# # or for your custom agent:player1 = AlphaBetaPlayer(search_depth=3, score_fn=custom_score, timeout=15.)
# player2 = MinimaxPlayer(search_depth=2, score_fn=custom_score_2, timeout=15.)


# # player2 = RandomPlayer()

# # --- 2. Play the game and get move history ---
# game = Board(player1, player2)
# winner, history, outcome = game.play()
# print(f"🏆 Game finished! Winner: {winner}")

# # --- 3. Save history to JSON ---
# output_dir = "isoviz"
# output_path = os.path.join(output_dir, "match.json")
# os.makedirs(output_dir, exist_ok=True)

# with open(output_path, "w") as f:
#     json.dump(history, f)
# print(f"✅ Match saved to {output_path}")

# # --- 4. Open visualization in browser ---
# html_path = os.path.abspath(os.path.join(output_dir, "display.html"))
# webbrowser.open(f"file://{html_path}")
# print("🌐 Opening visualization in your default browser...")

# from isolation import Board
# from game_agent import AlphaBetaPlayer

# p1 = AlphaBetaPlayer(timeout=200)
# p2 = AlphaBetaPlayer(timeout=200)

# b = Board(p1, p2)
# print(b.get_legal_moves())

# move = p1.get_move(b, lambda: 1000)
# print("Move:", move)

from isolation import Board
from game_agent import AlphaBetaPlayer

p1 = AlphaBetaPlayer(search_depth=3, timeout=200.)
p2 = AlphaBetaPlayer(search_depth=3, timeout=200.)

b = Board(p1, p2)

print("Legal:", b.get_legal_moves())

move = p1.get_move(b, lambda: 1000)
print("p1 move:", move)


