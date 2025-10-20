#!/usr/bin/env python3
"""
Chess Engine Benchmark Script

A Python script to benchmark two UCI-compatible chess engines playing against each other.
Uses the python-chess library for UCI engine communication and game management.

Author: AI Assistant
Date: 2024
"""

import chess
import chess.engine
import chess.pgn
import subprocess
import time
import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChessEngineBenchmark:
    """
    A class to handle chess engine benchmarking between two UCI engines.
    """
    
    def __init__(self, engine1_project_dir: str, engine2_project_dir: str, time_per_move: float = 0.1, fen_file: str = "fens/fen_positions.txt"):
        """
        Initialize the benchmark with two engine project directories and time per move.
        
        Args:
            engine1_project_dir: Path to the first chess engine project directory
            engine2_project_dir: Path to the second chess engine project directory
            time_per_move: Time per move in seconds
            fen_file: Path to the FEN positions file
        """
        self.engine1_project_dir = Path(engine1_project_dir)
        self.engine2_project_dir = Path(engine2_project_dir)
        self.time_per_move = time_per_move
        self.fen_file = Path(fen_file)
        
        # Validate project directories
        if not self.engine1_project_dir.exists():
            raise FileNotFoundError(f"Engine 1 project directory not found: {engine1_project_dir}")
        if not self.engine2_project_dir.exists():
            raise FileNotFoundError(f"Engine 2 project directory not found: {engine2_project_dir}")
        
        # Check if build/bin/main exists in each project directory
        engine1_executable = self.engine1_project_dir / "build" / "bin" / "main"
        engine2_executable = self.engine2_project_dir / "build" / "bin" / "main"
        
        if not engine1_executable.exists():
            raise FileNotFoundError(f"Engine 1 executable not found: {engine1_executable}")
        if not engine2_executable.exists():
            raise FileNotFoundError(f"Engine 2 executable not found: {engine2_executable}")
        
        # Load FEN positions
        self.fen_positions = self.load_fen_positions()
        
        # Set engine names (append A/B if same name)
        self.engine1_name = self.engine1_project_dir.name
        self.engine2_name = self.engine2_project_dir.name
        
        if self.engine1_name == self.engine2_name:
            self.engine1_name = f"{self.engine1_name}A"
            self.engine2_name = f"{self.engine2_name}B"
            logger.info(f"Same engine name detected, using: {self.engine1_name} vs {self.engine2_name}")
        
        # Results tracking
        self.results = {
            'engine1_wins': 0,
            'engine2_wins': 0,
            'draws': 0,
            'engine1_crashes': 0,
            'engine2_crashes': 0,
            'total_games': 0,
            'total_matches': 0
        }

        self.pgn_location = ""
        
        logger.info(f"Initialized benchmark: {self.engine1_name} vs {self.engine2_name}")
        logger.info(f"Time per move: {self.time_per_move}s")
        logger.info(f"Loaded {len(self.fen_positions)} FEN positions from {fen_file}")
    
    def load_fen_positions(self) -> list:
        """Load FEN positions from the specified file."""
        try:
            with open(self.fen_file, 'r') as f:
                positions = [line.strip() for line in f if line.strip()]
            logger.info(f"Successfully loaded {len(positions)} FEN positions")
            return positions
        except FileNotFoundError:
            raise FileNotFoundError(f"FEN positions file not found: {self.fen_file}")
        except Exception as e:
            raise Exception(f"Error loading FEN positions: {e}")
    
    def play_game(self, game_number: int, fen_position: str, engine1_is_white: bool = True) -> Optional[chess.pgn.Game]:
        """
        Play a single game between the two engines from a specific FEN position.
        
        Args:
            game_number: The game number for logging purposes
            fen_position: The FEN position to start from
            engine1_is_white: Whether engine1 plays as white
            
        Returns:
            A chess.pgn.Game object if successful, None if failed
        """
        logger.info(f"Starting game {game_number} - {'Engine1' if engine1_is_white else 'Engine2'} plays White")
        
        # Create a game from the FEN position
        try:
            board = chess.Board(fen_position)
        except ValueError as e:
            logger.error(f"Invalid FEN position in game {game_number}: {fen_position}")
            return None
        
        game = chess.pgn.Game()
        game.headers["Event"] = f"Engine Benchmark Game {game_number}"
        game.headers["Site"] = "Computer"
        game.headers["Date"] = time.strftime("%Y.%m.%d")
        game.headers["Round"] = str(game_number)
        game.headers["White"] = self.engine1_name if engine1_is_white else self.engine2_name
        game.headers["Black"] = self.engine2_name if engine1_is_white else self.engine1_name
        game.headers["TimeControl"] = f"{self.time_per_move}s per move"
        game.headers["FEN"] = fen_position
        
        node = game
        
        try:
            # Start both engines from their project directories
            engine1_cmd = [str(self.engine1_project_dir / "build" / "bin" / "main"), "--uci"]
            engine2_cmd = [str(self.engine2_project_dir / "build" / "bin" / "main"), "--uci"]
            
            with chess.engine.SimpleEngine.popen_uci(engine1_cmd, cwd=str(self.engine1_project_dir)) as engine1, \
                 chess.engine.SimpleEngine.popen_uci(engine2_cmd, cwd=str(self.engine2_project_dir)) as engine2:
                
                # Configure engines (optional - skip if not supported)
                try:
                    engine1.configure({"Threads": 1})
                    engine2.configure({"Threads": 1})
                except chess.engine.EngineError:
                    # Engine doesn't support configuration, continue anyway
                    logger.debug("Engine doesn't support configuration, continuing...")
                
                move_count = 0
                max_moves = 200  # Prevent infinite games
                
                while not board.is_game_over() and move_count < max_moves:
                    # Determine which engine to use
                    current_engine = engine1 if (board.turn == chess.WHITE and engine1_is_white) or \
                                           (board.turn == chess.BLACK and not engine1_is_white) else engine2
                    
                    try:
                        # Get the best move
                        result = current_engine.play(board, chess.engine.Limit(time=self.time_per_move))
                        move = result.move
                        
                        # Validate the move
                        if move not in board.legal_moves:
                            logger.error(f"Invalid move {move} in game {game_number}")
                            break
                        
                        # Make the move
                        board.push(move)
                        node = node.add_variation(move)
                        move_count += 1
                        
                        logger.debug(f"Move {move_count}: {move}")
                        
                    except chess.engine.EngineTerminatedError:
                        logger.error(f"Engine crashed in game {game_number}")
                        if current_engine == engine1:
                            self.results['engine1_crashes'] += 1
                        else:
                            self.results['engine2_crashes'] += 1
                        return None
                        
                    except Exception as e:
                        logger.error(f"Error in game {game_number}: {e}")
                        return None
                
                # Determine game result
                if board.is_checkmate():
                    winner = "Black" if board.turn == chess.WHITE else "White"
                    if (winner == "White" and engine1_is_white) or (winner == "Black" and not engine1_is_white):
                        self.results['engine1_wins'] += 1
                        game.headers["Result"] = "1-0" if engine1_is_white else "0-1"
                    else:
                        self.results['engine2_wins'] += 1
                        game.headers["Result"] = "0-1" if engine1_is_white else "1-0"
                elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
                    self.results['draws'] += 1
                    game.headers["Result"] = "1/2-1/2"
                else:
                    # Game ended due to move limit
                    self.results['draws'] += 1
                    game.headers["Result"] = "1/2-1/2"
                
                self.results['total_games'] += 1
                logger.info(f"Game {game_number} completed: {game.headers['Result']}")
                return game
                
        except Exception as e:
            logger.error(f"Failed to start engines for game {game_number}: {e}")
            return None
    
    def run_benchmark(self, num_matches: int) -> str:
        """
        Run the complete benchmark between the two engines using FEN positions.
        
        Args:
            num_matches: Number of matches to play (each match = 2 games)
            
        Returns:
            Path to the generated PGN file
        """
        logger.info(f"Starting benchmark: {num_matches} matches ({num_matches * 2} games)")
        
        # Check if we have enough FEN positions
        if num_matches > len(self.fen_positions):
            logger.warning(f"Requested {num_matches} matches but only {len(self.fen_positions)} FEN positions available")
            num_matches = len(self.fen_positions)
        
        # Create tests directory if it doesn't exist
        tests_dir = Path("tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Create timestamped PGN filename in tests directory
        timestamp = int(time.time())
        pgn_filename = f"fen_match_{timestamp}.pgn"
        self.pgn_location = pgn_filename
        pgn_path = tests_dir / pgn_filename
        
        games_played = []
        
        try:
            game_counter = 1
            
            for match_num in range(1, num_matches + 1):
                fen_position = self.fen_positions[match_num - 1]  # Use ith FEN for ith match
                
                logger.info(f"Starting match {match_num} with FEN: {fen_position[:50]}...")
                
                # Game 1: Engine 1 plays White
                game1 = self.play_game(game_counter, fen_position, engine1_is_white=True)
                if game1:
                    games_played.append(game1)
                    game_counter += 1
                
                # Game 2: Engine 2 plays White (same FEN position)
                game2 = self.play_game(game_counter, fen_position, engine1_is_white=False)
                if game2:
                    games_played.append(game2)
                    game_counter += 1
                
                self.results['total_matches'] += 1
                
                # Debug: Print win statistics after each match
                logger.debug(f"Match {match_num} completed - Current Statistics:")
                logger.debug(f"  {self.engine1_name} Wins: {self.results['engine1_wins']}")
                logger.debug(f"  {self.engine2_name} Wins: {self.results['engine2_wins']}")
                logger.debug(f"  Draws: {self.results['draws']}")
                logger.debug(f"  Total Games: {self.results['total_games']}")
                
                if self.results['total_games'] > 0:
                    engine1_win_rate = (self.results['engine1_wins'] / self.results['total_games']) * 100
                    engine2_win_rate = (self.results['engine2_wins'] / self.results['total_games']) * 100
                    draw_rate = (self.results['draws'] / self.results['total_games']) * 100
                    logger.debug(f"  Win Rates: {self.engine1_name} {engine1_win_rate:.1f}%, {self.engine2_name} {engine2_win_rate:.1f}%, Draws {draw_rate:.1f}%")
                
                # Print progress
                if match_num % 5 == 0 or match_num == num_matches:
                    logger.info(f"Progress: {match_num}/{num_matches} matches completed")
            
            # Save all games to PGN file
            with open(pgn_path, 'w') as pgn_file:
                for game in games_played:
                    print(game, file=pgn_file, end='\n\n')
            
            logger.info(f"Benchmark completed! Results saved to: tests/{pgn_filename}")
            return str(pgn_path)
            
        except KeyboardInterrupt:
            logger.info("Benchmark interrupted by user")
            # Save partial results
            if games_played:
                with open(pgn_path, 'w') as pgn_file:
                    for game in games_played:
                        print(game, file=pgn_file, end='\n\n')
                logger.info(f"Partial results saved to: tests/{pgn_filename}")
            return str(pgn_path)
    
    def print_summary(self):
        """Print a summary of the benchmark results."""
        print("\n" + "="*60)
        print("FEN POSITION BENCHMARK RESULTS SUMMARY")
        print("="*60)
        print(f"PGN: {self.pgn_location}")
        print(f"Time Control: {self.time_per_move} sec/move")
        print(f"Total Games: {self.results['total_games']}")
        print(f"Total Matches: {self.results['total_matches']}")
        print(f"Total Games: {self.results['total_games']}")
        print(f"{self.engine1_name} Wins: {self.results['engine1_wins']}")
        print(f"{self.engine2_name} Wins: {self.results['engine2_wins']}")
        print(f"Draws: {self.results['draws']}")
        print(f"{self.engine1_name} Crashes: {self.results['engine1_crashes']}")
        print(f"{self.engine2_name} Crashes: {self.results['engine2_crashes']}")
        
        if self.results['total_games'] > 0:
            # Calculate points (1 for win, 0.5 for draw, 0 for loss)
            engine1_points = self.results['engine1_wins'] + (self.results['draws'] * 0.5)
            engine2_points = self.results['engine2_wins'] + (self.results['draws'] * 0.5)
            total_points = engine1_points + engine2_points
            
            # Calculate win rates
            engine1_win_rate = (self.results['engine1_wins'] / self.results['total_games']) * 100
            engine2_win_rate = (self.results['engine2_wins'] / self.results['total_games']) * 100
            draw_rate = (self.results['draws'] / self.results['total_games']) * 100
            
            # Calculate score (points / total possible points)
            engine1_score = engine1_points / self.results['total_games'] if self.results['total_games'] > 0 else 0.5
            engine2_score = engine2_points / self.results['total_games'] if self.results['total_games'] > 0 else 0.5
            
            print(f"\nPoints Breakdown:")
            print(f"{self.engine1_name}: {engine1_points:.1f} points ({engine1_score:.3f} score)")
            print(f"{self.engine2_name}: {engine2_points:.1f} points ({engine2_score:.3f} score)")
            
            print(f"\nWin Rates:")
            print(f"{self.engine1_name}: {engine1_win_rate:.1f}%")
            print(f"{self.engine2_name}: {engine2_win_rate:.1f}%")
            print(f"Draws: {draw_rate:.1f}%")
            
            # Calculate Elo difference
            if engine1_score != 0.5 and engine1_score > 0 and engine1_score < 1:
                import math
                elo_diff = 400 * math.log10(engine1_score / (1 - engine1_score))
                print(f"\nElo Difference:")
                if elo_diff > 0:
                    print(f"{self.engine1_name} is {abs(elo_diff):.0f} Elo points stronger than {self.engine2_name}")
                else:
                    print(f"{self.engine2_name} is {abs(elo_diff):.0f} Elo points stronger than {self.engine1_name}")
            else:
                print(f"\nElo Difference: Too close to call (scores too close to 50%)")
        
        print("="*60)


def main():
    """Main function to run the chess engine benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark two UCI chess engines using FEN positions")
    parser.add_argument("engine1_project_dir", help="Path to first chess engine project directory")
    parser.add_argument("engine2_project_dir", help="Path to second chess engine project directory")
    parser.add_argument("-m", "--matches", type=int, default=5, help="Number of matches to play (default: 5)")
    parser.add_argument("-t", "--time", type=float, default=0.1, help="Time per move in seconds (default: 0.1)")
    parser.add_argument("-f", "--fen-file", default="fens/fen_positions.txt", help="FEN positions file (default: fens/fen_positions.txt)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create benchmark instance
        benchmark = ChessEngineBenchmark(args.engine1_project_dir, args.engine2_project_dir, args.time, args.fen_file)
        
        # Run the benchmark
        pgn_file = benchmark.run_benchmark(args.matches)
        
        # Print results
        benchmark.print_summary()
        
        print(f"\nGames saved to: {pgn_file}")
        print("You can open this file in chess software like Lichess, ChessBase, or any PGN viewer.")
        print(f"All test files are saved in the 'tests' directory.")
        print(f"Each match consists of 2 games: Engine1 as White, Engine2 as White (same FEN position)")
        
    except FileNotFoundError as e:
        logger.error(f"Engine project directory, executable, or FEN file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
