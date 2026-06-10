"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
import math

class SearchTimeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Heuristic 1: تفاوت تعداد حرکات قانونی بازیکن با حریف، وزن دهی بیشتر به مرکز"""
    if game.is_loser(player):
        return float("-inf")
    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    # مرکز صفحه 7x7
    center = (3, 3)
    player_loc = game.get_player_location(player)
    # فاصله از مرکز
    center_dist = math.sqrt((player_loc[0]-center[0])**2 + (player_loc[1]-center[1])**2)
    return float(own_moves - opp_moves - 0.5*center_dist)


def custom_score_2(game, player):
    """Heuristic 2: نسبت تعداد حرکت‌ها و مسدود کردن مسیر حریف"""
    if game.is_loser(player):
        return float("-inf")
    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - 2*opp_moves)  # وزن‌دهی بیشتر به کاهش حرکات حریف


def custom_score_3(game, player):
    """Heuristic 3: ترکیبی از حرکات خود و حرکات حریف و نزدیکی به مرکز"""
    if game.is_loser(player):
        return float("-inf")
    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    center = (3, 3)
    loc = game.get_player_location(player)
    center_dist = math.sqrt((loc[0]-center[0])**2 + (loc[1]-center[1])**2)
    return float(2*own_moves - 3*opp_moves - center_dist)

# ---------------------------
# Base Player
# ---------------------------

class IsolationPlayer:
    """Base class for minimax and alphabeta agents."""
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

# ---------------------------
# Minimax Player
# ---------------------------

class MinimaxPlayer(IsolationPlayer):
    """Minimax agent with fixed depth."""

    def get_move(self, game, time_left):
        self.time_left = time_left
        best_move = (-1, -1)
        try:
            return self.minimax(game, self.search_depth)
        except SearchTimeout:
            return best_move

    def minimax(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        best_move = legal_moves[0]
        best_val = float("-inf")
        
        for move in legal_moves:
            val = self._min_value(game.forecast_move(move), depth - 1)
            if val > best_val:
                best_val = val
                best_move = move
        return best_move

    def _max_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        value = float("-inf")
        for mv in moves:
            value = max(value, self._min_value(game.forecast_move(mv), depth - 1))
        return value

    def _min_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        value = float("inf")
        for mv in moves:
            value = min(value, self._max_value(game.forecast_move(mv), depth - 1))
        return value

# ---------------------------
# AlphaBeta Player
# ---------------------------

class AlphaBetaPlayer(IsolationPlayer):
    """AlphaBeta player with iterative deepening."""

    def get_move(self, game, time_left):
        self.time_left = time_left
        best_move = (-1, -1)
        try:
            depth = 1
            while True:
                if self.time_left() < self.TIMER_THRESHOLD:
                    raise SearchTimeout()
                move = self.alphabeta(game, depth)
                if move is not None:
                    best_move = move
                depth += 1
        except SearchTimeout:
            return best_move
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)

        best_move = legal_moves[0]
        best_val = float("-inf")
        for move in legal_moves:
            val = self._min_value_ab(game.forecast_move(move), depth - 1, alpha, beta)
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, best_val)
            if alpha >= beta:
                break
        return best_move

    def _max_value_ab(self, game, depth, alpha, beta):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        value = float("-inf")
        for mv in moves:
            value = max(value, self._min_value_ab(game.forecast_move(mv), depth - 1, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def _min_value_ab(self, game, depth, alpha, beta):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        value = float("inf")
        for mv in moves:
            value = min(value, self._max_value_ab(game.forecast_move(mv), depth - 1, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

# ---------------------------
# Expectimax Player
# ---------------------------

class ExpectimaxPlayer(IsolationPlayer):
    """Expectimax agent assuming opponent plays randomly."""

    def get_move(self, game, time_left):
        self.time_left = time_left
        best_move = (-1, -1)
        try:
            return self.expectimax(game, self.search_depth)
        except SearchTimeout:
            return best_move

    def expectimax(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        best_move = legal_moves[0]
        best_val = float("-inf")
        for mv in legal_moves:
            val = self._expect_value(game.forecast_move(mv), depth - 1)
            if val > best_val:
                best_val = val
                best_move = mv
        return best_move

    def _max_value_exp(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        value = float("-inf")
        for mv in moves:
            value = max(value, self._expect_value(game.forecast_move(mv), depth - 1))
        return value

    def _expect_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        moves = game.get_legal_moves()
        if depth == 0 or not moves:
            return self.score(game, self)
        total = 0.0
        for mv in moves:
            total += self._max_value_exp(game.forecast_move(mv), depth - 1)
        return total / len(moves)

# class IsolationPlayer:
#     """Base class for minimax and alphabeta agents -- this class is never
#     constructed or tested directly.

#     ********************  DO NOT MODIFY THIS CLASS  ********************

#     Parameters
#     ----------
#     search_depth : int (optional)
#         A strictly positive integer (i.e., 1, 2, 3,...) for the number of
#         layers in the game tree to explore for fixed-depth search. (i.e., a
#         depth of one (1) would only explore the immediate sucessors of the
#         current state.)

#     score_fn : callable (optional)
#         A function to use for heuristic evaluation of game states.

#     timeout : float (optional)
#         Time remaining (in milliseconds) when search is aborted. Should be a
#         positive value large enough to allow the function to return before the
#         timer expires.
#     """
#     def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
#         self.search_depth = search_depth
#         self.score = score_fn
#         self.time_left = None
#         self.TIMER_THRESHOLD = timeout


# class MinimaxPlayer(IsolationPlayer):
#     """Game-playing agent that chooses a move using depth-limited minimax
#     search. You must finish and test this player to make sure it properly uses
#     minimax to return a good move before the search time limit expires.
#     """

#     def get_move(self, game, time_left):
#         """Search for the best move from the available legal moves and return a
#         result before the time limit expires.

#         **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

#         For fixed-depth search, this function simply wraps the call to the
#         minimax method, but this method provides a common interface for all
#         Isolation agents, and you will replace it in the AlphaBetaPlayer with
#         iterative deepening search.

#         Parameters
#         ----------
#         game : `isolation.Board`
#             An instance of `isolation.Board` encoding the current state of the
#             game (e.g., player locations and blocked cells).

#         time_left : callable
#             A function that returns the number of milliseconds left in the
#             current turn. Returning with any less than 0 ms remaining forfeits
#             the game.

#         Returns
#         -------
#         (int, int)
#             Board coordinates corresponding to a legal move; may return
#             (-1, -1) if there are no available legal moves.
#         """
#         self.time_left = time_left

#         # Initialize the best move so that this function returns something
#         # in case the search fails due to timeout
#         best_move = (-1, -1)

#         try:
#             # The try/except block will automatically catch the exception
#             # raised when the timer is about to expire.
#             return self.minimax(game, self.search_depth)

#         except SearchTimeout:
#             pass  # Handle any actions required after timeout as needed

#         # Return the best move from the last completed search iteration
#         return best_move

#     def minimax(self, game, depth):
#         """Implement depth-limited minimax search algorithm as described in
#         the lectures.

#         This should be a modified version of MINIMAX-DECISION in the AIMA text.
#         https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

#         **********************************************************************
#             You MAY add additional methods to this class, or define helper
#                  functions to implement the required functionality.
#         **********************************************************************

#         Parameters
#         ----------
#         game : isolation.Board
#             An instance of the Isolation game `Board` class representing the
#             current game state

#         depth : int
#             Depth is an integer representing the maximum number of plies to
#             search in the game tree before aborting

#         Returns
#         -------
#         (int, int)
#             The board coordinates of the best move found in the current search;
#             (-1, -1) if there are no legal moves

#         Notes
#         -----
#             You MUST use the `self.score()` method for board evaluation
#             to pass the project tests; you cannot call any other evaluation
#             function directly.
#         """
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         # TODO: finish this function!
#         raise NotImplementedError
# # ---------------------------
# # AlphaBetaPlayer
# # ---------------------------

# class AlphaBetaPlayer(IsolationPlayer):
#     """Iterative deepening minimax player with alpha-beta pruning."""

#     def get_move(self, game, time_left):
#         """Iterative deepening: increase depth until timeout, return best found."""
#         self.time_left = time_left
#         best_move = (-1, -1)

#         try:
#             depth = 1
#             while True:
#                 if self.time_left() < self.TIMER_THRESHOLD:
#                     raise SearchTimeout()
#                 move = self.alphabeta(game, depth)
#                 # if alphabeta returns a valid move, update best_move
#                 if move is not None:
#                     best_move = move
#                 depth += 1
#         except SearchTimeout:
#             # return last best move found
#             return best_move
#         except Exception:
#             # in case of unexpected error, return best_move
#             return best_move

#     def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
#         """Return best move from current game state using alpha-beta pruning."""

#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         legal_moves = game.get_legal_moves()
#         if not legal_moves:
#             return (-1, -1)

#         best_move = (-1, -1)
#         best_val = float("-inf")

#         for move in legal_moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             forecast = game.forecast_move(move)
#             val = self._min_value_ab(forecast, depth - 1, alpha, beta)
#             if val > best_val:
#                 best_val = val
#                 best_move = move
#             alpha = max(alpha, best_val)
#             if alpha >= beta:
#                 break  # beta cutoff

#         return best_move

#     def _max_value_ab(self, game, depth, alpha, beta):
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         moves = game.get_legal_moves()
#         if depth == 0 or not moves:
#             return self.score(game, self)

#         value = float("-inf")
#         for mv in moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             value = max(value, self._min_value_ab(game.forecast_move(mv), depth - 1, alpha, beta))
#             if value >= beta:
#                 return value
#             alpha = max(alpha, value)
#         return value

#     def _min_value_ab(self, game, depth, alpha, beta):
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         moves = game.get_legal_moves()
#         if depth == 0 or not moves:
#             return self.score(game, self)

#         value = float("inf")
#         for mv in moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             value = min(value, self._max_value_ab(game.forecast_move(mv), depth - 1, alpha, beta))
#             if value <= alpha:
#                 return value
#             beta = min(beta, value)
#         return value


# # ---------------------------
# # ExpectimaxPlayer
# # ---------------------------

# class ExpectimaxPlayer(IsolationPlayer):
#     """Depth-limited expectimax player. Assumes opponent acts randomly."""

#     def get_move(self, game, time_left):
#         """Return the best move found by depth-limited expectimax search."""
#         self.time_left = time_left
#         best_move = (-1, -1)

#         try:
#             # fixed-depth search using self.search_depth
#             return self.expectimax(game, self.search_depth)
#         except SearchTimeout:
#             return best_move

#     def expectimax(self, game, depth):
#         """Return best move for current player using expectimax."""
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         legal_moves = game.get_legal_moves()
#         if not legal_moves:
#             return (-1, -1)

#         best_move = legal_moves[0]
#         best_val = float("-inf")

#         for mv in legal_moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             val = self._expect_value(game.forecast_move(mv), depth - 1)
#             if val > best_val:
#                 best_val = val
#                 best_move = mv

#         return best_move

#     def _max_value_exp(self, game, depth):
#         """Max node (agent's turn)."""
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         moves = game.get_legal_moves()
#         if depth == 0 or not moves:
#             return self.score(game, self)

#         value = float("-inf")
#         for mv in moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             value = max(value, self._expect_value(game.forecast_move(mv), depth - 1))
#         return value

#     def _expect_value(self, game, depth):
#         """Chance/opponent node: return expected value assuming uniform random play."""
#         if self.time_left() < self.TIMER_THRESHOLD:
#             raise SearchTimeout()

#         moves = game.get_legal_moves()
#         if depth == 0 or not moves:
#             return self.score(game, self)

#         total = 0.0
#         for mv in moves:
#             if self.time_left() < self.TIMER_THRESHOLD:
#                 raise SearchTimeout()
#             total += self._max_value_exp(game.forecast_move(mv), depth - 1)
#         return total / len(moves)


