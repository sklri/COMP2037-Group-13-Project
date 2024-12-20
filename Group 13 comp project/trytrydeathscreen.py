import pygame
import sys
from moviepy.editor import VideoFileClip
import subprocess

pygame.init()
pygame.font.init()

# Set up the display
window_size = (1024, 768)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Bee a Savior")

# Load music and sound effects
pygame.mixer.music.load("Cyberpunk World Theme Song.wav")
pygame.mixer.music.set_volume(0.3)  # Lowered background music volume
pygame.mixer.music.play(-1)  # Loop the background music

# Load sound effects
attack_sound = pygame.mixer.Sound("Bee Attack.wav")
jump_sound = pygame.mixer.Sound("Bee Jump.wav")
robot_attack_sound = pygame.mixer.Sound("Robot Attack Sound Effect.wav")  # Updated sound
robot_die_sound = pygame.mixer.Sound("Robot Die Sound Effect.wav")
bee_die_sound = pygame.mixer.Sound("Bee Die Sound Effect.wav")

# Load the full-size background image
full_background = pygame.image.load("Cyber.png")
full_background = pygame.transform.scale(full_background, (4096, 768))

# Load character and animation images
default_image = pygame.image.load("Default.png")
run_images_right = [pygame.image.load("beew01.png"), pygame.image.load("beew02.png")]
run_images_left = [pygame.image.load("beeleft01.png"), pygame.image.load("beeleft02.png")]

# Load attack animation images
attack_images = [pygame.image.load(f"attack0{i+1}.png") for i in range(5)]
explosion_images = [pygame.image.load(f"Explosion{i+1}.png") for i in range(5)]

# Load obstacle images
obstacle_image = pygame.image.load("HorizontalPlatform.png")

# Load robot animation frames
robot_frames = [
    pygame.image.load("robota01.png"),
    pygame.image.load("robota02.png"),
    pygame.image.load("robota03.png"),
    pygame.image.load("robota04.png"),
    pygame.image.load("robota05.png"),
]

# Initialize character
character_rect = default_image.get_rect(center=(window_size[0] // 2, 445))
character_health = 100

# Game state
scroll_x = 0
is_jumping = False
velocity_y = 0
game_over = False


# Define health values
character_health = 100
starting_position = (window_size[0] // 2, 445)  # Original starting position

# Robot setup
robots = [
    {"rect": pygame.Rect(850, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(1240, 150, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(2350, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(2650, 150, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(3450, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
]

# Define the scroll margins
SCROLL_MARGIN = window_size[0] // 2  # Middle of the screen

# Variables for scrolling
scroll_x = 0
scroll_speed = 5
world_x = SCROLL_MARGIN  # Track the character's position in the world

# Jumping variables
is_jumping = False
jump_velocity = 20
gravity = 1
velocity_y = 0
boss_fight_active = 0

# Animation variables
current_image = default_image
animation_index = 0
animation_timer = 0
animation_delay = 10

# Robot animation variables
robot_animation_index = 0
robot_animation_timer = 0
robot_animation_delay = 15

# Attack variables
attack = False
attack_start_time = 0
attack_animation_index = 0
is_attacking = False
attack_duration = 350  # Total duration for the attack animation (in milliseconds)
attack_frame_duration = attack_duration // len(attack_images)  # Duration of each frame

# Obstacles list with world coordinates
obstacles = [
    {"rect": pygame.Rect(600, 550, 150, 30), "world_x": 600, "image": obstacle_image},
    {"rect": pygame.Rect(800, 400, 150, 30), "world_x": 800, "image": obstacle_image},
    {"rect": pygame.Rect(1200, 350, 150, 30), "world_x": 1200, "image": obstacle_image},
    {"rect": pygame.Rect(1600, 350, 150, 30), "world_x": 1600, "image": obstacle_image},
    {"rect": pygame.Rect(1900, 550, 150, 30), "world_x": 1900, "image": obstacle_image},
    {"rect": pygame.Rect(2200, 400, 150, 30), "world_x": 2200, "image": obstacle_image},
    {"rect": pygame.Rect(2600, 350, 150, 30), "world_x": 2600, "image": obstacle_image},
]

# After the game variables setup, add these new variables:
death_screen_active = False
respawn_countdown = 3  # Countdown in seconds before respawning

def stop_music():
    pygame.mixer.music.stop()


# Function to run another Python file
def run_other_script():
    print("TryTryOs.py...")
    subprocess.run(['python', 'TryTryOs.py'])  # Adjust 'python' to 'python3' if needed

def update_obstacle_positions(scroll_x):
    for obstacle in obstacles:
        obstacle["rect"].x = obstacle["world_x"] - scroll_x

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
    pygame.draw.rect(surface, (255, 0, 0), (x, y, 150, 15))  # Outer border
    health_percentage = health / max_health
    health_color = (0, 255, 0) if health > 0 else (255, 0, 0)
    pygame.draw.rect(surface, health_color, (x, y, 150 * health_percentage, 15))  # Health level

def draw_quest_bar(surface, remaining_robots):
    font = pygame.font.SysFont('Arial', 24)
    quest_text = font.render(f"Quest: Kill all 5 robots", True, (255, 255, 255))
    remaining_text = font.render(f"Remaining: {remaining_robots}", True, (255, 255, 255))
    
    quest_bg = pygame.Surface((300, 60))
    quest_bg.fill((0, 0, 0))
    quest_bg.set_alpha(128)
    surface.blit(quest_bg, (10, 10))
    surface.blit(quest_text, (20, 15))
    surface.blit(remaining_text, (20, 40))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()


     # Check if player is dead
    if character_health <= 0 and not death_screen_active:
        death_screen_active = True
        bee_die_sound.play()
        death_start_time = pygame.time.get_ticks()
        pygame.mixer.music.pause()  # Pause background music instead of stopping
        
    # Handle death screen
    if death_screen_active:
        # Create a semi-transparent overlay
        overlay = pygame.Surface(window_size)
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        window.blit(overlay, (0, 0))
        
        # Display death message and countdown
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
                
                # Reset robots
                robots = [
                    {"rect": pygame.Rect(850, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
                    {"rect": pygame.Rect(1240, 150, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
                    {"rect": pygame.Rect(2350, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
                    {"rect": pygame.Rect(2650, 150, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
                    {"rect": pygame.Rect(3450, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
                ]
                
                # Reset character position and scroll values
                character_rect.topleft = starting_position
                world_x = SCROLL_MARGIN
                scroll_x = 0
                
                # Reset movement and animation states
                is_jumping = False
                velocity_y = 0
                current_image = default_image
                animation_index = 0
                animation_timer = 0
                
                # Resume background music
                pygame.mixer.music.unpause()
        
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
    if keys[pygame.K_SPACE] and not is_jumping and character_health > 0:
        is_jumping = True
        velocity_y = jump_velocity
        jump_sound.play()  # Play jump sound

    # Apply gravity
    character_rect.y -= velocity_y
    velocity_y -= gravity

    # Check if character is on a platform
    on_platform = is_on_platform(character_rect, obstacles)

    # Collision detection with robots
    current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
    for robot in robots:
        robot_rect = robot["rect"].copy()
        robot_rect.x -= scroll_x  # Adjust for scrolling

        # Check if the robot can hurt the character
        if character_rect.colliderect(robot_rect):
            if attack:
                if current_time - robot["damage_cooldown"] >= 2000:
                    robot["health"] -= 1
                    print(f"Robot hit! Current health: {robot['health']}")
                    robot["damage_cooldown"] = current_time
                    is_attacking = True
                    attack_start_time = current_time
                    attack_animation_index = 0
                    attack_sound.play()  # Play attack sound
                    if robot["health"] <= 0:
                        robot["is_exploding"] = True
                        robot["explosion_index"] = 0
                        robot_die_sound.play()  # Play robot die sound
                        print("Robot destroyed!")
            else:
                if current_time - robot["last_hurt_time"] >= 3000:  # 3 seconds
                    character_health -= 25
                    if character_health < 0:
                        character_health = 0  # Prevent negative health
                    robot_attack_sound.play()  # Play robot attack sound
                    print(f"Collision with robot! Player Health: {character_health}")
                    robot["last_hurt_time"] = current_time

            # Prevent movement when colliding with robots
            if character_rect.right > robot_rect.left and character_rect.left < robot_rect.right:
                if character_rect.bottom > robot_rect.top and character_rect.top < robot_rect.bottom:
                    if character_rect.centery < robot_rect.centery:
                        character_rect.bottom = robot_rect.top
                        is_jumping = False
                        velocity_y = 0
                    else:
                        character_rect.top = robot_rect.bottom
                    break  # Exit the loop after handling collision
# Check for left mouse click to initiate attack
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and character_health > 0:  # Left mouse button
        attack = True
        attack_start_time = pygame.time.get_ticks()  # Record the start time of the attack

    # Check if the attack duration has expired
    if attack and pygame.time.get_ticks() - attack_start_time > attack_duration:
        attack = False  # Reset attack state

    # Attack animation logic
    if is_attacking:
        if current_time - attack_start_time >= attack_frame_duration:
            attack_animation_index += 1
            attack_start_time = current_time
            if attack_animation_index >= len(attack_images):
                is_attacking = False  # End attack animation
                attack_animation_index = 0  # Reset the animation index

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

    # Movement and scrolling logic
    if keys[pygame.K_a] and character_health > 0:  # Use 'A' for left movement
        world_x -= scroll_speed
        if scroll_x > 0:
            scroll_x -= scroll_speed
            character_rect.x = SCROLL_MARGIN
        else:
            character_rect.x = world_x
        
        animation_timer += 1
        if animation_timer >= animation_delay:
            animation_index = (animation_index + 1) % len(run_images_left)
            current_image = run_images_left[animation_index]
            animation_timer = 0

    if keys[pygame.K_d] and character_health > 0:  # Use 'D' for right movement
        world_x += scroll_speed
        if world_x > SCROLL_MARGIN and scroll_x < full_background.get_width() - window_size[0]:
            scroll_x += scroll_speed
            character_rect.x = SCROLL_MARGIN
        else:
            character_rect.x = world_x
        
        animation_timer += 1
        if animation_timer >= animation_delay:
            animation_index = (animation_index + 1) % len(run_images_right)
            current_image = run_images_right[animation_index]
            animation_timer = 0
    else:
        if not keys[pygame.K_a]:
            current_image = default_image
            animation_index = 0

    # Keep the scrolling within bounds
    scroll_x = max(0, min(scroll_x, full_background.get_width() - window_size[0]))

    # Keep character within screen bounds
    character_rect.x = max(0, min(character_rect.x, window_size[0] - character_rect.width))

    # Update obstacle positions based on scroll
    update_obstacle_positions(scroll_x)

    # Robot animation logic
    robot_animation_timer += 1
    if robot_animation_timer >= robot_animation_delay:
        robot_animation_index = (robot_animation_index + 1) % len(robot_frames)
        robot_animation_timer = 0

    # Drawing
    window.blit(full_background, (-scroll_x, 0))

    # Draw obstacles
    for obstacle in obstacles:
        window.blit(obstacle["image"], obstacle["rect"])

    # Draw the robots with animation and health bars
    for robot in robots:
        robot_screen_pos = robot["rect"].x - scroll_x  # Adjust for scrolling
        if robot["is_exploding"]:
            if "explosion_counter" not in robot:
                robot["explosion_counter"] = 0
            
            robot["explosion_counter"] += 1
            if robot["explosion_counter"] >= 15:  # Slow down the explosion
                if robot["explosion_index"] < len(explosion_images):
                    window.blit(explosion_images[robot["explosion_index"]], (robot_screen_pos, robot["rect"].y))
                    robot["explosion_index"] += 1
                    robot["explosion_counter"] = 0
                else:
                    robots.remove(robot)  # Remove the robot after explosion
            else:
                if robot["explosion_index"] < len(explosion_images):
                    window.blit(explosion_images[robot["explosion_index"]], (robot_screen_pos, robot["rect"].y))
        else:
            window.blit(robot_frames[robot_animation_index], (robot_screen_pos, robot["rect"].y))
            draw_health_bar(window, robot_screen_pos + 75, robot["rect"].y - 15, robot["health"], 2)  # Max health as 2
            
    # Draw the character
    if is_attacking:
        window.blit(attack_images[attack_animation_index], character_rect.topleft)  # Attack animation
    else:
        window.blit(current_image, character_rect.topleft)

    # Draw the player's health bar
    draw_health_bar(window, window_size[0] - 160, 20, character_health, 100)  # Increased size

    # # # Draw rectangles for debugging
    # pygame.draw.rect(window, (255, 0, 0), character_rect, 2)  # Player rectangle in red
    # for robot in robots:
    #     adjusted_robot_rect = robot["rect"].copy()
    #     adjusted_robot_rect.x -= scroll_x  # Adjust for scrolling
    #     pygame.draw.rect(window, (0, 255, 0), adjusted_robot_rect, 2)  # Robot rectangles in green

# Calculate remaining robots and draw quest bar
    remaining_robots = len([robot for robot in robots if robot["health"] > 0])
    
    draw_quest_bar(window, remaining_robots)
    
    if remaining_robots == 0:
        stop_music()
        run_other_script()
        break

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()