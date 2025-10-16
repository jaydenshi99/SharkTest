#!/usr/bin/env python3
"""
FEN Position Extractor

Extracts all FEN positions from Book.txt and saves them to a new file.
"""

import re
from pathlib import Path

def extract_fen_positions(input_file, output_file):
    """
    Extract all FEN positions from the input file and save to output file.
    
    Args:
        input_file: Path to the input Book.txt file
        output_file: Path to the output file for FEN positions
    """
    
    fen_positions = []
    
    print(f"Reading from: {input_file}")
    
    try:
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Look for lines that start with "pos " followed by a FEN
                if line.startswith('pos '):
                    # Extract the FEN part (everything after "pos ")
                    fen = line[4:].strip()
                    
                    # Basic validation - FEN should have at least 4 parts (board, turn, castling, en passant)
                    fen_parts = fen.split()
                    if len(fen_parts) >= 4:
                        # If FEN is incomplete, pad it with default values
                        if len(fen_parts) == 4:
                            # Add missing halfmove clock and fullmove number
                            fen = fen + " 0 1"
                        elif len(fen_parts) == 5:
                            # Add missing fullmove number
                            fen = fen + " 1"
                        
                        fen_positions.append(fen)
                    else:
                        print(f"Warning: Invalid FEN format at line {line_num}: {fen}")
                
                # Progress indicator for large files
                if line_num % 10000 == 0:
                    print(f"Processed {line_num} lines, found {len(fen_positions)} FEN positions...")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    print(f"\nFound {len(fen_positions)} FEN positions")
    
    # Save to output file
    try:
        with open(output_file, 'w') as f:
            for fen in fen_positions:
                f.write(fen + '\n')
        
        print(f"Successfully saved FEN positions to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False

def main():
    """Main function to run the FEN extraction."""
    
    input_file = "Book.txt"
    output_file = "fen_positions.txt"
    
    print("=== FEN Position Extractor ===")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        print("Make sure Book.txt is in the current directory.")
        return
    
    # Extract FEN positions
    success = extract_fen_positions(input_file, output_file)
    
    if success:
        print(f"\n✅ Extraction completed successfully!")
        print(f"📁 FEN positions saved to: {output_file}")
        
        # Show file size info
        input_size = Path(input_file).stat().st_size
        output_size = Path(output_file).stat().st_size
        print(f"📊 Input file size: {input_size:,} bytes")
        print(f"📊 Output file size: {output_size:,} bytes")
        
        # Show first few FEN positions as preview
        print(f"\n📋 Preview of extracted FEN positions:")
        try:
            with open(output_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 5:  # Show first 5
                        break
                    print(f"  {i+1}. {line.strip()}")
            if len(fen_positions) > 5:
                print(f"  ... and {len(fen_positions) - 5} more")
        except:
            pass
    else:
        print("❌ Extraction failed!")

if __name__ == "__main__":
    main()
