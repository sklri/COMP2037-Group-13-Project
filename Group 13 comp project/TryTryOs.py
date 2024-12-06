import pygame
import sys
from moviepy.editor import VideoFileClip
import time
import subprocess
import os


def playvideo(videopath):
    pygame.init()

clip = VideoFileClip("Cyber AI Entrance.mp4")
window_size = (1024, 768)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Bee a Savior")
clip.preview()

pygame.init()
pygame.font.init()

# Set up the display
window_size = (1024, 768)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Bee a Savior")

# Load the background image
background = pygame.image.load("Cyber.png")

# Load music and sound effects
pygame.mixer.music.load("Song for AI battle.wav")
pygame.mixer.music.set_volume(0.3)  # Lowered background music volume
pygame.mixer.music.play(-1)  # Loop the background music

# Load sound effects
attack_sound = pygame.mixer.Sound("Bee Attack.wav")
jump_sound = pygame.mixer.Sound("Bee Jump.wav")
robot_attack_sound = pygame.mixer.Sound("Robot Attack Sound Effect.wav")  # Updated sound
robot_die_sound = pygame.mixer.Sound("Robot Die Sound Effect.wav")
bee_die_sound = pygame.mixer.Sound("Bee Die Sound Effect.wav")

# Load character and animation images
default_image = pygame.image.load("Default.png")
run_images_right = [pygame.image.load("beew01.png"), pygame.image.load("beew02.png")]
run_images_left = [pygame.image.load("beeleft01.png"), pygame.image.load("beeleft02.png")]

# Load attack animation images
attack_images = [
    pygame.image.load("attack01.png"),
    pygame.image.load("attack02.png"),
    pygame.image.load("attack03.png"),
    pygame.image.load("attack04.png"),
    pygame.image.load("attack05.png"),
]

# Load obstacle images
obstacle_image = pygame.image.load("HorizontalPlatform.png")

# Initialize character rectangle
character_rect = default_image.get_rect()
character_rect.centerx = window_size[0] // 4  # Start at left of screen
character_rect.y = 445

# Define health values
character_health = 100

# After the game variables setup, add these new variables:
death_screen_active = False
respawn_countdown = 3  # Countdown in seconds before respawning

# Jumping variables
is_jumping = False
jump_velocity = 20
gravity = 1
velocity_y = 0

# Animation variables
current_image = default_image
animation_index = 0
animation_timer = 0
animation_delay = 10

# Attack variables
attack = False
attack_start_time = 0
attack_animation_index = 0
is_attacking = False
attack_duration = 350
attack_frame_duration = attack_duration // len(attack_images)

# Obstacles list
obstacles = [
    {"rect": pygame.Rect(600, 550, 150, 30), "image": obstacle_image},
    {"rect": pygame.Rect(700, 400, 150, 30), "image": obstacle_image},
    {"rect": pygame.Rect(600, 250, 150, 30), "image": obstacle_image},
    {"rect": pygame.Rect(100, 400, 150, 30), "image": obstacle_image},
    {"rect": pygame.Rect(200, 550, 150, 30), "image": obstacle_image},
    {"rect": pygame.Rect(200, 250, 150, 30), "image": obstacle_image},
]

# set up ai
ai_image = pygame.image.load("AI.png")
ai_rect = ai_image.get_rect()
ai = [
    {
        "rect": pygame.Rect(window_size[0] // 2 - 80, 300, 40, 80),  # Center position
        "health": 100,
        "last_hurt_time": 0,
        "damage_cooldown": 1000,
        "direction": 1,  # 1 for down, -1 for up
        "speed": 2,
        "original_y": 200,  # Store original y position
        "movement_range": 100  # How far it moves up and down
    }
]

def stop_music():
    pygame.mixer.music.stop()

# Function to run another Python file
def run_other_script():
    print("trytrystagetwo.py...")
    subprocess.run(['python', 'trytrystagetwo.py'])  # Adjust 'python' to 'python3' if needed


# Add collision detection function for AI and character attacks
def check_attack_collision(attack_rect, ai_enemy):
    return attack_rect.colliderect(ai_enemy["rect"])

#move_ai function for up and down movement
def move_ai(ai_enemy):
    # Calculate movement boundaries
    upper_bound = ai_enemy["original_y"] - ai_enemy["movement_range"]
    lower_bound = ai_enemy["original_y"] + ai_enemy["movement_range"]
    
    # Move the AI up and down
    ai_enemy["rect"].y += ai_enemy["speed"] * ai_enemy["direction"]
    
    # Change direction when reaching boundaries
    if ai_enemy["rect"].y >= lower_bound:
        ai_enemy["direction"] = -1
    elif ai_enemy["rect"].y <= upper_bound:
        ai_enemy["direction"] = 1


def check_collision(rect, velocity_y):
    for obstacle in obstacles:
        if rect.colliderect(obstacle["rect"]):
            if velocity_y < 0 and rect.bottom <= obstacle["rect"].top + abs(velocity_y):
                return obstacle["rect"]
    return None

def is_on_platform(character_rect, obstacles):
    foot_rect = pygame.Rect(character_rect.x, character_rect.bottom, character_rect.width, 2)
    for obstacle in obstacles:
        if foot_rect.colliderect(obstacle["rect"]):
            return True
    return False

def draw_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, (255, 0, 0), (x, y, 150, 15))
    health_percentage = health / max_health
    health_color = (0, 255, 0) if health > 0 else (255, 0, 0)
    pygame.draw.rect(surface, health_color, (x, y, 150 * health_percentage, 15))

# Main loop
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
        # Check if player is dead
    if character_health == 0 and not death_screen_active:
        death_screen_active = True
        bee_die_sound.play()
        death_start_time = pygame.time.get_ticks()
        pygame.mixer.music.pause()  # Pause background music

    # Handle death screen
    if death_screen_active:
        overlay = pygame.Surface(window_size)
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        window.blit(overlay, (0, 0))

        font = pygame.font.SysFont('Arial', 48)
        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - death_start_time) / 1000  # Convert to seconds

        if time_elapsed <= 3:  # Show death message for 3 seconds
            death_text = font.render("YOU DIED", True, (255, 0, 0))
            text_rect = death_text.get_rect(center=(window_size[0]//2, window_size[1]//2))
            window.blit(death_text, text_rect)
        else:
            remaining_time = max(0, respawn_countdown - (time_elapsed - 3))
            if remaining_time > 0:
                countdown_text = font.render(f"Respawning in {int(remaining_time)}...", True, (255, 255, 255))
                text_rect = countdown_text.get_rect(center=(window_size[0]//2, window_size[1]//2))
                window.blit(countdown_text, text_rect)
            else:
                # Reset game state
                character_health = 100
                death_screen_active = False
                character_rect.topleft = (window_size[0] // 4, 445)  # Reset position
                pygame.mixer.music.unpause()  # Resume background music

        pygame.display.flip()
        continue  # Skip the rest of the loop while in death screen
    
            # Reset movement and animation states
        is_jumping = False
        velocity_y = 0
        current_image = default_image
        animation_index = 0
        animation_timer = 0
        
        # Restart background music
        pygame.mixer.music.play(-1)
        
        continue  # Skip the rest of the loop and start fresh


    # Store previous position
    prev_y = character_rect.y

    # Jumping logic
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        velocity_y = jump_velocity
        jump_sound.play()

    # Apply gravity
    character_rect.y -= velocity_y
    velocity_y -= gravity

    # Check if character is on a platform
    on_platform = is_on_platform(character_rect, obstacles)

    # Check for left mouse click to initiate attack
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]:
        attack = True
        attack_start_time = pygame.time.get_ticks()

    current_time = pygame.time.get_ticks()
    
    # Check if the attack duration has expired
    if attack and current_time - attack_start_time > attack_duration:
        attack = False

    # Attack animation logic
    if is_attacking:
        if current_time - attack_start_time >= attack_frame_duration:
            attack_animation_index += 1
            attack_start_time = current_time
            attack_sound.play()
            if attack_animation_index >= len(attack_images):
                is_attacking = False
                attack_animation_index = 0

    # Collision detection with obstacles
    collision_rect = check_collision(character_rect, velocity_y)
    if collision_rect and velocity_y < 0:
        character_rect.bottom = collision_rect.top
        is_jumping = False
        velocity_y = 0
    elif character_rect.y >= 445:
        character_rect.y = 445
        is_jumping = False
        velocity_y = 0
    elif not on_platform and not is_jumping:
        is_jumping = True
        velocity_y = 0

    # Movement logic
    if keys[pygame.K_a]:
        character_rect.x -= 5
        animation_timer += 1
        if animation_timer >= animation_delay:
            animation_index = (animation_index + 1) % len(run_images_left)
            current_image = run_images_left[animation_index]
            animation_timer = 0

    if keys[pygame.K_d]:
        character_rect.x += 5
        animation_timer += 1
        if animation_timer >= animation_delay:
            animation_index = (animation_index + 1) % len(run_images_right)
            current_image = run_images_right[animation_index]
            animation_timer = 0
    else:
        if not keys[pygame.K_a]:
            current_image = default_image
            animation_index = 0

    if mouse_buttons[0] and not is_attacking:
        attack = True
        is_attacking = True
        attack_start_time = current_time


        # Check for collision with AI during attack
        for ai_enemy in ai:
            if ai_enemy["health"] > 0:
                attack_rect = pygame.Rect(
                    character_rect.x + (50 if current_image in run_images_right else -50),
                    character_rect.y,
                    100,
                    character_rect.height
                )
                
                if check_attack_collision(attack_rect, ai_enemy):
                    if current_time - ai_enemy["last_hurt_time"] > ai_enemy["damage_cooldown"]:
                        ai_enemy["health"] -= 10  # Damage dealt to AI
                        ai_enemy["last_hurt_time"] = current_time

    # Update AI
    for ai_enemy in ai:
        if ai_enemy["health"] > 0:
            move_ai(ai_enemy)
            # Check for collision between character and AI
            if character_rect.colliderect(ai_enemy["rect"]):
                if current_time - ai_enemy["last_hurt_time"] > ai_enemy["damage_cooldown"]:
                    character_health -= 10
                    ai_enemy["health"] -= 12
                    robot_attack_sound.play()
                    ai_enemy["last_hurt_time"] = current_time
                    
    # Keep character within screen bounds
    character_rect.x = max(0, min(character_rect.x, window_size[0] - character_rect.width))

    # Drawing
    window.blit(background, (0, 0))

    # Draw AI enemies
    for ai_enemy in ai:
        if ai_enemy["health"] > 0:
            window.blit(ai_image, ai_enemy["rect"])
            # Draw AI health bar
            draw_health_bar(window, ai_enemy["rect"].x, ai_enemy["rect"].y - 20, ai_enemy["health"], 100)
    
    # Draw obstacles
    for obstacle in obstacles:
        window.blit(obstacle["image"], obstacle["rect"])

    # Draw the character
    if is_attacking:
        window.blit(attack_images[attack_animation_index], character_rect.topleft)
    else:
        window.blit(current_image, character_rect.topleft)

    # Draw the player's health bar
    draw_health_bar(window, window_size[0] - 160, 20, character_health, 100)

    # Draw debug rectangles
    # pygame.draw.rect(window, (255, 0, 0), character_rect, 2)
    for ai_enemy in ai:
        # if ai_enemy["health"] > 0:
        #     pygame.draw.rect(window, (0, 255, 0), ai_enemy["rect"], 2)
        if ai_enemy["health"] <= 0 and character_health > 0:
                stop_music()
                run_other_script() 
                
    pygame.display.flip()

pygame.quit()
sys.exit()