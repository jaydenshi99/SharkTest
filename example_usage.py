#!/usr/bin/env python3
"""
Example Usage Script for Chess Engine Benchmark

This script demonstrates how to use the chess_engine_benchmark.py script
with different configurations and scenarios.
"""

import subprocess
import sys
from pathlib import Path

def run_benchmark_example():
    """
    Example function showing how to run the chess engine benchmark.
    """
    
    print("Chess Engine Benchmark - Example Usage")
    print("=" * 50)
    
    # Example 1: Self-play (same engine playing against itself)
    print("\nExample 1: Self-play benchmark")
    print("Command: python chess_engine_benchmark.py /path/to/myengine /path/to/myengine -n 10 -t 0.1")
    print("This would run 10 games with your engine playing against itself, 0.1 seconds per move")
    
    # Example 2: Two different engines
    print("\nExample 2: Two different engines")
    print("Command: python chess_engine_benchmark.py /path/to/myengine1 /path/to/myengine2 -n 20 -t 1.0")
    print("This would run 20 games between two different engines, 1 second per move")
    
    # Example 3: Quick benchmark
    print("\nExample 3: Quick benchmark")
    print("Command: python chess_engine_benchmark.py /path/to/engine1 /path/to/engine2 -n 5 -t 0.05")
    print("This would run 5 games with very fast time control (0.05 seconds per move)")
    
    # Example 4: Long time control
    print("\nExample 4: Long time control")
    print("Command: python chess_engine_benchmark.py /path/to/engine1 /path/to/engine2 -n 50 -t 5.0")
    print("This would run 50 games with 5 seconds per move (higher quality games)")
    
    # Example 5: Verbose output
    print("\nExample 5: Verbose output")
    print("Command: python chess_engine_benchmark.py /path/to/engine1 /path/to/engine2 -n 10 -t 0.1 -v")
    print("This would run 10 games with verbose logging enabled")
    
    print("\n" + "=" * 50)
    print("IMPORTANT: ENGINE PROJECT DIRECTORY STRUCTURE")
    print("=" * 50)
    print("Your engine project should have this structure:")
    print("your_engine_project/")
    print("├── build/")
    print("│   └── bin/")
    print("│       └── main")
    print("├── src/")
    print("└── ...")
    print("\nThe script will run: ./build/bin/main --uci from your project directory")
    
    print("\n" + "=" * 50)
    print("EXAMPLE PROJECT PATHS:")
    print("=" * 50)
    print("If your engines are in:")
    print("- /home/user/mychessengine/")
    print("- /home/user/myotheroengine/")
    print("\nThen run:")
    print("python chess_engine_benchmark.py /home/user/mychessengine /home/user/myotheroengine -n 10 -t 0.1")
    
    print("\nFor self-play (same engine vs itself):")
    print("python chess_engine_benchmark.py /home/user/mychessengine /home/user/mychessengine -n 10 -t 0.1")

def interactive_benchmark():
    """
    Interactive function to help users run benchmarks.
    """
    print("\nInteractive Chess Engine Benchmark Setup")
    print("=" * 40)
    
    try:
        engine1_project_dir = input("Enter path to first engine project directory: ").strip()
        engine2_project_dir = input("Enter path to second engine project directory: ").strip()
        
        if not engine1_project_dir or not engine2_project_dir:
            print("Error: Both engine project directory paths are required")
            return
        
        num_games = input("Number of games (default: 10): ").strip()
        num_games = int(num_games) if num_games else 10
        
        time_per_move = input("Time per move in seconds (default: 0.1): ").strip()
        time_per_move = float(time_per_move) if time_per_move else 0.1
        
        verbose = input("Verbose output? (y/N): ").strip().lower() == 'y'
        
        # Build command
        cmd = [
            sys.executable, "chess_engine_benchmark.py",
            engine1_project_dir, engine2_project_dir,
            "-n", str(num_games),
            "-t", str(time_per_move)
        ]
        
        if verbose:
            cmd.append("-v")
        
        print(f"\nRunning command: {' '.join(cmd)}")
        print("=" * 40)
        
        # Run the benchmark
        result = subprocess.run(cmd, check=True)
        print("\nBenchmark completed successfully!")
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error running benchmark: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("Chess Engine Benchmark - Example Usage Script")
    print("This script shows how to use the chess_engine_benchmark.py script")
    print()
    
    choice = input("Choose an option:\n1. Show examples\n2. Run interactive benchmark\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_benchmark_example()
    elif choice == "2":
        interactive_benchmark()
    else:
        print("Invalid choice. Showing examples...")
        run_benchmark_example()
