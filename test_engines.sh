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
MATCHES=5
TIME=0.1
FEN_FILE="fens/fen_positions.txt"

echo "Testing engines with these settings:"
echo "Engine 1: $ENGINE1"
echo "Engine 2: $ENGINE2"
echo "Matches: $MATCHES"
echo "Time per move: ${TIME}s"
echo "FEN file: $FEN_FILE"
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
    
    read -p "Enter number of matches [$MATCHES]: " input_matches
    if [ ! -z "$input_matches" ]; then
        MATCHES="$input_matches"
    fi
    
    read -p "Enter time per move in seconds [$TIME]: " input_time
    if [ ! -z "$input_time" ]; then
        TIME="$input_time"
    fi
    
    read -p "Enter FEN file path [$FEN_FILE]: " input_fen_file
    if [ ! -z "$input_fen_file" ]; then
        FEN_FILE="$input_fen_file"
    fi
    
    echo ""
    echo "Updated settings:"
    echo "Engine 1: $ENGINE1"
    echo "Engine 2: $ENGINE2"
    echo "Matches: $MATCHES (each match = 2 games)"
    echo "Time per move: ${TIME}s"
    echo "FEN file: $FEN_FILE"
    echo ""
fi

# Run the benchmark
echo "Starting benchmark..."
echo ""

python chess_engine_benchmark.py "$ENGINE1" "$ENGINE2" -m "$MATCHES" -t "$TIME" -f "$FEN_FILE"

echo ""
echo "Benchmark completed!"
echo "Check the generated PGN file for the game results."
