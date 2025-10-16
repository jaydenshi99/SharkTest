# Chess Engine Benchmark Script

A Python script to benchmark two UCI-compatible chess engines playing against each other. This tool uses the `python-chess` library to manage UCI engine communication and game logic.

## Features

- **UCI Engine Support**: Works with any UCI-compatible chess engine
- **Flexible Configuration**: Specify engine paths, number of games, and time per move
- **Balanced Testing**: Alternates engine sides (White/Black) each game
- **PGN Output**: Saves all games in timestamped PGN files compatible with chess software
- **Comprehensive Results**: Detailed statistics including wins, losses, draws, and crash counts
- **Error Handling**: Robust handling of engine crashes and invalid moves
- **Clean Code**: Modular, well-commented, and easy to understand

## Installation

1. Install Python 3.7 or higher
2. Install the required dependency:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install python-chess
```

## Usage

### Basic Usage

```bash
python chess_engine_benchmark.py <engine1_project_dir> <engine2_project_dir> [options]
```

### Command Line Arguments

- `engine1_project_dir`: Path to first chess engine project directory
- `engine2_project_dir`: Path to second chess engine project directory
- `-n, --games`: Number of games to play (default: 10)
- `-t, --time`: Time per move in seconds (default: 0.1)
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message

### Examples

#### Self-play (same engine against itself)
```bash
python chess_engine_benchmark.py /path/to/myengine_project /path/to/myengine_project -n 10 -t 0.1
```

#### Two different engines
```bash
python chess_engine_benchmark.py /path/to/myengine1_project /path/to/myengine2_project -n 20 -t 1.0
```

#### Quick benchmark
```bash
python chess_engine_benchmark.py /path/to/engine1_project /path/to/engine2_project -n 5 -t 0.05
```

#### Long time control
```bash
python chess_engine_benchmark.py /path/to/engine1_project /path/to/engine2_project -n 50 -t 5.0
```

#### Verbose output
```bash
python chess_engine_benchmark.py /path/to/engine1_project /path/to/engine2_project -n 10 -t 0.1 -v
```

## Example Usage Script

Run the interactive example script to get started:

```bash
python example_usage.py
```

This script provides:
- Example commands with different configurations
- Interactive setup for running benchmarks
- Detection of common engine installations

## Output

### Console Output
The script provides real-time progress updates and a comprehensive results summary:

```
BENCHMARK RESULTS SUMMARY
============================================================
Total Games: 10
stockfish Wins: 4
komodo Wins: 3
Draws: 3
stockfish Crashes: 0
komodo Crashes: 0

Win Rates:
stockfish: 40.0%
komodo: 30.0%
Draws: 30.0%
============================================================
```

### PGN File
Games are saved in a timestamped PGN file (e.g., `match_1697581234.pgn`) that can be opened in:
- Lichess Analysis Board
- ChessBase
- Any PGN-compatible chess software

## Engine Requirements

Your chess engines must:
- Be UCI-compatible
- Be built and located in a project directory with the structure: `project_dir/build/bin/main`
- Support basic UCI commands: `uci`, `isready`, `position`, `go movetime X`, `quit`

### Minimal UCI Implementation

The script works with minimal UCI implementations. You only need to support these commands:
- `uci` - Initial handshake
- `isready` - Check if engine is ready  
- `position [fen <fen> | startpos] moves <move1> ... <movei>` - Set board position
- `go movetime <x>` - Calculate best move with time limit in milliseconds
- `quit` - Exit the engine

Optional commands (script will work without them):
- `setoption name <option> value <value>` - Engine configuration

### Project Directory Structure

Your engine project should have this structure:
```
your_engine_project/
├── build/
│   └── bin/
│       └── main          # Your compiled engine executable
├── src/                  # Source code
├── CMakeLists.txt        # Build configuration
└── ...                   # Other project files
```

The script will run `./build/bin/main --uci` from your project directory.

### Common UCI Engines
- **Stockfish**: Open-source, very strong
- **Komodo**: Commercial engine
- **Leela Chess Zero (Lc0)**: Neural network engine
- **Houdini**: Commercial engine
- **Rybka**: Commercial engine

## Error Handling

The script includes comprehensive error handling for:
- **Engine crashes**: Tracks and reports engine crashes
- **Invalid moves**: Validates moves before playing them
- **File not found**: Checks engine paths before starting
- **Interrupted games**: Saves partial results if interrupted
- **UCI protocol errors**: Handles communication failures

## Technical Details

### Game Flow
1. Initialize both engines with UCI protocol
2. Configure engines (single thread, time limits)
3. Play moves alternating between engines
4. Track game state and validate moves
5. Determine game result (win/loss/draw)
6. Save game to PGN format

### Time Control
- Uses `chess.engine.Limit(time=X)` for time control
- Each engine gets exactly X seconds per move
- No increment or other time controls currently supported

### Side Alternation
- Engine 1 plays White in odd-numbered games
- Engine 2 plays White in even-numbered games
- Ensures balanced testing conditions

## Troubleshooting

### Common Issues

1. **"Engine project directory or executable not found"**
   - Verify the project directory path is correct
   - Ensure `build/bin/main` exists in your project directory
   - Make sure your engine is compiled and built
   - Check file permissions

2. **"Engine crashed"**
   - Engine may not be UCI-compatible
   - Engine may have insufficient resources
   - Try reducing time per move

3. **"Invalid move"**
   - Engine may be returning illegal moves
   - Check engine UCI implementation
   - Enable verbose logging for debugging

### Debug Mode
Use the `-v` flag for verbose logging to see:
- Individual moves as they're played
- Engine communication details
- Detailed error messages

## Contributing

This script is designed to be simple and readable. Feel free to:
- Add new features
- Improve error handling
- Optimize performance
- Add support for different time controls

## License

This script is provided as-is for educational and testing purposes. Please respect the licenses of any chess engines you use with this tool.
