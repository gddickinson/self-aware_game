"""
Create placeholder assets for development
This script generates simple placeholder graphics for development
Run this once to create the basic assets folder structure
"""

import os
import pygame
import sys

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_placeholder_sprite_sheet():
    """Create a simple placeholder sprite sheet for the character."""
    # Create assets directory structure
    create_directory("assets")
    create_directory("assets/fonts")
    create_directory("assets/sounds")
    create_directory("assets/ui")

    # Initialize pygame
    pygame.init()

    # Character sprite sheet (4x4 grid of sprites)
    sprite_size = 32
    sprite_sheet_size = (sprite_size * 4, sprite_size * 4)
    sprite_sheet = pygame.Surface(sprite_sheet_size, pygame.SRCALPHA)

    # Colors for different directions
    direction_colors = [
        (255, 100, 100),  # Right (Red)
        (100, 255, 100),  # Down (Green)
        (100, 100, 255),  # Left (Blue)
        (255, 255, 100)   # Up (Yellow)
    ]

    # Draw character sprites (simple colored rectangles with different shades)
    for direction in range(4):
        for frame in range(4):
            # Base color for this direction
            color = direction_colors[direction]

            # Modify shade based on frame
            shade = 0.7 + (frame * 0.1)  # 0.7, 0.8, 0.9, 1.0
            frame_color = (
                min(255, int(color[0] * shade)),
                min(255, int(color[1] * shade)),
                min(255, int(color[2] * shade))
            )

            # Position in the sprite sheet
            x = frame * sprite_size
            y = direction * sprite_size

            # Draw character body (rectangle)
            body_rect = pygame.Rect(x + 8, y + 8, 16, 24)
            pygame.draw.rect(sprite_sheet, frame_color, body_rect, border_radius=4)

            # Draw character head (circle)
            head_pos = (x + 16, y + 8)
            pygame.draw.circle(sprite_sheet, frame_color, head_pos, 6)

            # Draw features (eyes, etc.) - just simple pixels
            # Eyes
            eye_color = (30, 30, 30)
            if direction == 0:  # Right
                pygame.draw.rect(sprite_sheet, eye_color, (x + 18, y + 6, 2, 2))
            elif direction == 1:  # Down
                pygame.draw.rect(sprite_sheet, eye_color, (x + 14, y + 8, 2, 2))
                pygame.draw.rect(sprite_sheet, eye_color, (x + 18, y + 8, 2, 2))
            elif direction == 2:  # Left
                pygame.draw.rect(sprite_sheet, eye_color, (x + 12, y + 6, 2, 2))
            elif direction == 3:  # Up
                pygame.draw.rect(sprite_sheet, eye_color, (x + 14, y + 6, 2, 2))
                pygame.draw.rect(sprite_sheet, eye_color, (x + 18, y + 6, 2, 2))

    # Save sprite sheet
    pygame.image.save(sprite_sheet, "assets/character_sprites.png")
    print("Created placeholder character sprite sheet")

    # Create a simple UI button sprite
    button_sheet = pygame.Surface((192, 64), pygame.SRCALPHA)

    # Normal button
    button_rect = pygame.Rect(0, 0, 64, 32)
    pygame.draw.rect(button_sheet, (100, 100, 100), button_rect, border_radius=5)
    pygame.draw.rect(button_sheet, (150, 150, 150), button_rect, width=2, border_radius=5)

    # Hover button
    button_rect = pygame.Rect(64, 0, 64, 32)
    pygame.draw.rect(button_sheet, (120, 120, 150), button_rect, border_radius=5)
    pygame.draw.rect(button_sheet, (170, 170, 200), button_rect, width=2, border_radius=5)

    # Pressed button
    button_rect = pygame.Rect(128, 0, 64, 32)
    pygame.draw.rect(button_sheet, (80, 80, 120), button_rect, border_radius=5)
    pygame.draw.rect(button_sheet, (120, 120, 170), button_rect, width=2, border_radius=5)

    # Save button sprite
    pygame.image.save(button_sheet, "assets/ui/buttons.png")
    print("Created placeholder UI button sprites")

    # Create a simple dialogue box
    dialogue_box = pygame.Surface((400, 100), pygame.SRCALPHA)
    pygame.draw.rect(dialogue_box, (40, 40, 60, 200), (0, 0, 400, 100), border_radius=10)
    pygame.draw.rect(dialogue_box, (100, 100, 140, 255), (0, 0, 400, 100), width=2, border_radius=10)
    pygame.image.save(dialogue_box, "assets/ui/dialogue_box.png")
    print("Created placeholder dialogue box")

    # Create a simple thought bubble
    thought_bubble = pygame.Surface((200, 100), pygame.SRCALPHA)
    pygame.draw.rect(thought_bubble, (240, 240, 255, 200), (0, 0, 200, 100), border_radius=20)
    pygame.draw.rect(thought_bubble, (180, 180, 220, 255), (0, 0, 200, 100), width=2, border_radius=20)
    # Add small circles for the tail of the thought bubble
    pygame.draw.circle(thought_bubble, (240, 240, 255, 200), (40, 105), 10)
    pygame.draw.circle(thought_bubble, (240, 240, 255, 200), (20, 115), 6)
    pygame.draw.circle(thought_bubble, (240, 240, 255, 200), (10, 123), 3)
    pygame.image.save(thought_bubble, "assets/ui/thought_bubble.png")
    print("Created placeholder thought bubble")

    # Create placeholder sound files (0.5 second beeps)
    try:
        import numpy as np
        import wave
        import struct

        # Function to create a simple sound file
        def create_beep(filename, frequency=440, duration=0.5, volume=0.5):
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave_data = np.sin(frequency * t * 2 * np.pi)
            wave_data = (wave_data * 32767 * volume).astype(np.int16)

            # Write the wave data to a file
            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes = 16 bits
                wav_file.setframerate(sample_rate)
                for sample in wave_data:
                    wav_file.writeframes(struct.pack('<h', sample))

        # Create different beep sounds
        create_beep("assets/sounds/dialogue.wav", frequency=440)  # A4
        create_beep("assets/sounds/footsteps.wav", frequency=220, duration=0.1)  # A3
        create_beep("assets/sounds/snake_eat.wav", frequency=880)  # A5
        create_beep("assets/sounds/thinking.wav", frequency=660)  # E5

        print("Created placeholder sound files")
    except ImportError:
        print("NumPy not available - skipping sound file creation")
        print("To create sound files, install NumPy: pip install numpy")
        # Create empty files as placeholders
        open("assets/sounds/dialogue.wav", 'w').close()
        open("assets/sounds/footsteps.wav", 'w').close()
        open("assets/sounds/snake_eat.wav", 'w').close()
        open("assets/sounds/thinking.wav", 'w').close()

    print("\nAsset creation complete!")
    print("You can replace these placeholder assets with your own custom graphics and sounds.")

if __name__ == "__main__":
    create_placeholder_sprite_sheet()
    pygame.quit()
