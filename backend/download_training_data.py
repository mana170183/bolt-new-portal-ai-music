#!/usr/bin/env python3
"""
Training Data Downloader for AI Music Generation
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_training_data():
    """Create sample training data structure"""
    
    training_dir = Path("training_data")
    training_dir.mkdir(exist_ok=True)
    
    # Create sample genres
    genres = ["classical", "jazz", "rock", "blues", "electronic", "ambient"]
    
    for genre in genres:
        genre_dir = training_dir / genre
        genre_dir.mkdir(exist_ok=True)
        
        # Create a sample info file
        info_file = genre_dir / "info.txt"
        with open(info_file, 'w') as f:
            f.write(f"Sample {genre} training data directory\n")
            f.write(f"Add MIDI files here for {genre} training\n")
    
    logger.info(f"Created training data structure in {training_dir}")
    
    # Create manifest
    manifest = {
        "created": str(training_dir),
        "genres": genres,
        "description": "Sample training data structure for AI music generation"
    }
    
    import json
    with open(training_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info("Training data structure ready")

if __name__ == "__main__":
    create_sample_training_data()
