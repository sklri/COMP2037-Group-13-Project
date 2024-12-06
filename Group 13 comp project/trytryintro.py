import pygame
import time
from moviepy.editor import VideoFileClip
import subprocess  # For running another Python file

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1024, 768
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bee a Savior")

# Load images
try:
    background = pygame.image.load('Main.png')
    button_image = pygame.image.load('Start button.png')
    button_pressed_image = pygame.image.load('instruction.png')
except pygame.error as e:
    print(f"Error loading image: {e}")
    pygame.quit()
    exit()

# Load and play background music
try:
    pygame.mixer.music.load('Theme Song.wav')
    pygame.mixer.music.set_volume(0.2)  # Set volume to 20%
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
except pygame.error as e:
    print(f"Error loading music: {e}")
    pygame.quit()
    exit()

# Button position
button_rect = button_image.get_rect(center=(width // 2, height // 2))
button_pressed = False
start_time = 0

# Function to run another Python file
def run_other_script():
    print("Running trytrydeathscreen.py...")
    subprocess.run(['python', 'trytrydeathscreen.py'])  # Adjust 'python' to 'python3' if needed

# Main loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):  # Check if the button is pressed
                pygame.mixer.music.stop()  # Stop background music
                button_pressed = True
                start_time = time.time()  # Record the time when the button is pressed

    # Draw the background
    window.blit(background, (0, 0))

    # Check if button has been pressed
    if button_pressed:
        window.blit(button_pressed_image, button_rect.topleft)
        # Check if 5 seconds have passed
        if time.time() - start_time > 5:
            def playvideo(videopath):
                pygame.init()

            clip = VideoFileClip("Lab Scene.mp4")
            window_size = (1024, 768)
            window = pygame.display.set_mode(window_size)
            pygame.display.set_caption("Bee a Savior")
            clip.preview()
            
            run_other_script()  # Run the TryTryOs.py script
            running = False
 
    else:
        window.blit(button_image, button_rect.topleft)

    # Update the display
    pygame.display.flip()

pygame.quit()