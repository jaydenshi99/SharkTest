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
    
    def __init__(self, engine1_project_dir: str, engine2_project_dir: str, time_per_move: float = 0.1):
        """
        Initialize the benchmark with two engine project directories and time per move.
        
        Args:
            engine1_project_dir: Path to the first chess engine project directory
            engine2_project_dir: Path to the second chess engine project directory
            time_per_move: Time per move in seconds
        """
        self.engine1_project_dir = Path(engine1_project_dir)
        self.engine2_project_dir = Path(engine2_project_dir)
        self.time_per_move = time_per_move
        
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
        
        # Results tracking
        self.results = {
            'engine1_wins': 0,
            'engine2_wins': 0,
            'draws': 0,
            'engine1_crashes': 0,
            'engine2_crashes': 0,
            'total_games': 0
        }
        
        logger.info(f"Initialized benchmark: {self.engine1_project_dir.name} vs {self.engine2_project_dir.name}")
        logger.info(f"Time per move: {self.time_per_move}s")
    
    def play_game(self, game_number: int, engine1_is_white: bool = True) -> Optional[chess.pgn.Game]:
        """
        Play a single game between the two engines.
        
        Args:
            game_number: The game number for logging purposes
            engine1_is_white: Whether engine1 plays as white
            
        Returns:
            A chess.pgn.Game object if successful, None if failed
        """
        logger.info(f"Starting game {game_number} - {'Engine1' if engine1_is_white else 'Engine2'} plays White")
        
        # Create a new game
        board = chess.Board()
        game = chess.pgn.Game()
        game.headers["Event"] = f"Engine Benchmark Game {game_number}"
        game.headers["Site"] = "Computer"
        game.headers["Date"] = time.strftime("%Y.%m.%d")
        game.headers["Round"] = str(game_number)
        game.headers["White"] = self.engine1_project_dir.name if engine1_is_white else self.engine2_project_dir.name
        game.headers["Black"] = self.engine2_project_dir.name if engine1_is_white else self.engine1_project_dir.name
        game.headers["TimeControl"] = f"{self.time_per_move}s per move"
        
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
                    winner = "White" if board.turn == chess.BLACK else "Black"
                    if (winner == "White" and engine1_is_white) or (winner == "Black" and not engine1_is_white):
                        self.results['engine1_wins'] += 1
                        game.headers["Result"] = "1-0"
                    else:
                        self.results['engine2_wins'] += 1
                        game.headers["Result"] = "0-1"
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
    
    def run_benchmark(self, num_games: int) -> str:
        """
        Run the complete benchmark between the two engines.
        
        Args:
            num_games: Number of games to play
            
        Returns:
            Path to the generated PGN file
        """
        logger.info(f"Starting benchmark: {num_games} games")
        
        # Create timestamped PGN filename
        timestamp = int(time.time())
        pgn_filename = f"match_{timestamp}.pgn"
        pgn_path = Path(pgn_filename)
        
        games_played = []
        
        try:
            for game_num in range(1, num_games + 1):
                # Alternate which engine plays white
                engine1_is_white = (game_num % 2 == 1)
                
                game = self.play_game(game_num, engine1_is_white)
                if game:
                    games_played.append(game)
                
                # Print progress
                if game_num % 10 == 0 or game_num == num_games:
                    logger.info(f"Progress: {game_num}/{num_games} games completed")
            
            # Save all games to PGN file
            with open(pgn_path, 'w') as pgn_file:
                for game in games_played:
                    print(game, file=pgn_file, end='\n\n')
            
            logger.info(f"Benchmark completed! Results saved to: {pgn_filename}")
            return str(pgn_path)
            
        except KeyboardInterrupt:
            logger.info("Benchmark interrupted by user")
            # Save partial results
            if games_played:
                with open(pgn_path, 'w') as pgn_file:
                    for game in games_played:
                        print(game, file=pgn_file, end='\n\n')
                logger.info(f"Partial results saved to: {pgn_filename}")
            return str(pgn_path)
    
    def print_summary(self):
        """Print a summary of the benchmark results."""
        print("\n" + "="*60)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*60)
        print(f"Total Games: {self.results['total_games']}")
        print(f"{self.engine1_project_dir.name} Wins: {self.results['engine1_wins']}")
        print(f"{self.engine2_project_dir.name} Wins: {self.results['engine2_wins']}")
        print(f"Draws: {self.results['draws']}")
        print(f"{self.engine1_project_dir.name} Crashes: {self.results['engine1_crashes']}")
        print(f"{self.engine2_project_dir.name} Crashes: {self.results['engine2_crashes']}")
        
        if self.results['total_games'] > 0:
            engine1_win_rate = (self.results['engine1_wins'] / self.results['total_games']) * 100
            engine2_win_rate = (self.results['engine2_wins'] / self.results['total_games']) * 100
            draw_rate = (self.results['draws'] / self.results['total_games']) * 100
            
            print(f"\nWin Rates:")
            print(f"{self.engine1_project_dir.name}: {engine1_win_rate:.1f}%")
            print(f"{self.engine2_project_dir.name}: {engine2_win_rate:.1f}%")
            print(f"Draws: {draw_rate:.1f}%")
        
        print("="*60)


def main():
    """Main function to run the chess engine benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark two UCI chess engines")
    parser.add_argument("engine1_project_dir", help="Path to first chess engine project directory")
    parser.add_argument("engine2_project_dir", help="Path to second chess engine project directory")
    parser.add_argument("-n", "--games", type=int, default=10, help="Number of games to play (default: 10)")
    parser.add_argument("-t", "--time", type=float, default=0.1, help="Time per move in seconds (default: 0.1)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create benchmark instance
        benchmark = ChessEngineBenchmark(args.engine1_project_dir, args.engine2_project_dir, args.time)
        
        # Run the benchmark
        pgn_file = benchmark.run_benchmark(args.games)
        
        # Print results
        benchmark.print_summary()
        
        print(f"\nGames saved to: {pgn_file}")
        print("You can open this file in chess software like Lichess, ChessBase, or any PGN viewer.")
        
    except FileNotFoundError as e:
        logger.error(f"Engine project directory or executable not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
