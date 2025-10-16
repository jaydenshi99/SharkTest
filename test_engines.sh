#!/bin/bash
# Simple script to test chess engines
# Usage: ./test_engines.sh

echo "=== Chess Engine Test Script ==="
echo ""

# Navigate to the benchmark directory
cd /Users/jaydenshi/Documents/Code/Projects/SharkTest

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment activated!"
echo ""

# Set default values
ENGINE1="/Users/jaydenshi/Documents/Code/Projects/SticksharkVersions/1.0"
ENGINE2="/Users/jaydenshi/Documents/Code/Projects/SticksharkVersions/1.0"
GAMES=5
TIME=0.1

echo "Testing engines with these settings:"
echo "Engine 1: $ENGINE1"
echo "Engine 2: $ENGINE2"
echo "Games: $GAMES"
echo "Time per move: ${TIME}s"
echo ""

# Ask user if they want to change settings
read -p "Do you want to change any settings? (y/N): " change_settings

if [[ $change_settings =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter Engine 1 project directory [$ENGINE1]: " input_engine1
    if [ ! -z "$input_engine1" ]; then
        ENGINE1="$input_engine1"
    fi
    
    read -p "Enter Engine 2 project directory [$ENGINE2]: " input_engine2
    if [ ! -z "$input_engine2" ]; then
        ENGINE2="$input_engine2"
    fi
    
    read -p "Enter number of games [$GAMES]: " input_games
    if [ ! -z "$input_games" ]; then
        GAMES="$input_games"
    fi
    
    read -p "Enter time per move in seconds [$TIME]: " input_time
    if [ ! -z "$input_time" ]; then
        TIME="$input_time"
    fi
    
    echo ""
    echo "Updated settings:"
    echo "Engine 1: $ENGINE1"
    echo "Engine 2: $ENGINE2"
    echo "Games: $GAMES"
    echo "Time per move: ${TIME}s"
    echo ""
fi

# Run the benchmark
echo "Starting benchmark..."
echo ""

python chess_engine_benchmark.py "$ENGINE1" "$ENGINE2" -n "$GAMES" -t "$TIME"

echo ""
echo "Benchmark completed!"
echo "Check the generated PGN file for the game results."
