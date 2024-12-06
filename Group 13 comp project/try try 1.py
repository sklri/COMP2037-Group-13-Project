import pygame
import sys
import time

# Initialize Pygame
pygame.init()
pygame.font.init()

# Set up the display
window_size = (1024, 768)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Try Scrolling")

# Load the full-size background image
full_background = pygame.image.load("Cyber.png")
full_background = pygame.transform.scale(full_background, (4096, 768))

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

# Load explosion animation images
explosion_images = [
    pygame.image.load("Explosion1.png"),
    pygame.image.load("Explosion2.png"),
    pygame.image.load("Explosion3.png"),
    pygame.image.load("Explosion4.png"),
    pygame.image.load("Explosion5.png"),
]

# Load AI image
ai_image = pygame.image.load("AI.png")
ai_rect = ai_image.get_rect()
ai_rect.x = 3800  # Set the world x-coordinate where you want the AI to appear
ai_rect.y = 300   # Set the y-coordinate where you want the AI to appear

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

# Initialize character rectangle
character_rect = default_image.get_rect()
character_rect.centerx = window_size[0] // 2  # Start at middle of screen
character_rect.y = 445

# Define health values
character_health = 100

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
    # Draw the outer border
    pygame.draw.rect(surface, (255, 0, 0), (x, y, 150, 15))  # Increased size
    # Draw the health level
    health_percentage = health / max_health
    health_color = (0, 255, 0) if health > 0 else (255, 0, 0)
    pygame.draw.rect(surface, health_color, (x, y, 150 * health_percentage, 15))  # Increased size

def draw_quest_bar(surface, remaining_robots):
    font = pygame.font.SysFont('Arial', 24)
    quest_text = font.render(f"Quest: Kill all 5 robots", True, (255, 255, 255))
    remaining_text = font.render(f"Remaining: {remaining_robots}", True, (255, 255, 255))
    
    # Draw background rectangle for quest text
    quest_bg = pygame.Surface((300, 60))
    quest_bg.fill((0, 0, 0))
    quest_bg.set_alpha(128)
    surface.blit(quest_bg, (10, 10))
    
    # Draw the text
    surface.blit(quest_text, (20, 15))
    surface.blit(remaining_text, (20, 40))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Store previous position
    prev_y = character_rect.y

    # Jumping logic
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        velocity_y = jump_velocity

    # Apply gravity
    character_rect.y -= velocity_y
    velocity_y -= gravity

    # Check if character is on a platform
    on_platform = is_on_platform(character_rect, obstacles)

    # Collision detection with robots
    current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
    for robot in robots:
        # Adjusted robot position for checking collisions
        robot_rect = robot["rect"].copy()
        robot_rect.x -= scroll_x  # Adjust for scrolling

        # Check if the robot can hurt the character
        if character_rect.colliderect(robot_rect):
            # Determine if attack is active
            if attack:
                # Check if the robot is within damage cooldown
                if current_time - robot["damage_cooldown"] >= 2000:  # 2000 ms = 2 seconds
                    # Damage the robot
                    robot["health"] -= 1
                    print(f"Robot hit! Current health: {robot['health']}")
                    robot["damage_cooldown"] = current_time  # Set the time of the last damage
                    is_attacking = True  # Start the attack animation
                    attack_start_time = current_time  # Record the start time of the attack
                    attack_animation_index = 0  # Reset animation index
                    if robot["health"] <= 0:  # Check if the robot's health is zero or less
                        robot["is_exploding"] = True  # Start the explosion animation
                        robot["explosion_index"] = 0  # Reset explosion frame index
                        print("Robot destroyed!")
            else:
                # Check if cooldown has expired
                if current_time - robot["last_hurt_time"] >= 3000:  # 3000 ms = 3 seconds
                    character_health -= 25
                    if character_health < 0:
                        character_health = 0  # Prevent negative health
                    print(f"Collision with robot! Player Health: {character_health}")  # Debugging output
                    robot["last_hurt_time"] = current_time  # Update last hurt time

            # Prevent movement when colliding with robots
            if character_rect.right > robot_rect.left and character_rect.left < robot_rect.right:
                if character_rect.bottom > robot_rect.top and character_rect.top < robot_rect.bottom:
                    # Determine the direction of collision
                    if character_rect.centery < robot_rect.centery:
                        character_rect.bottom = robot_rect.top  # Land on top of robot
                        is_jumping = False
                        velocity_y = 0
                    else:
                        character_rect.top = robot_rect.bottom  # Push character up
                    break  # Exit the loop after handling collision

    # Check for left mouse click to initiate attack
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]:  # Left mouse button
        attack = True
        attack_start_time = pygame.time.get_ticks()  # Record the start time of the attack

    # Check if the attack duration has expired
    if attack and pygame.time.get_ticks() - attack_start_time > attack_duration:
        attack = False  # Reset attack state

    # Attack animation logic
    if is_attacking:
        if current_time - attack_start_time >= attack_frame_duration:
            attack_animation_index += 1
            attack_start_time = current_time  # Reset the start time for the next frame
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
    if keys[pygame.K_a]:  # Use 'A' for left movement
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

    if keys[pygame.K_d]:  # Use 'D' for right movement
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
            # Add explosion animation counter if it doesn't exist
            if "explosion_counter" not in robot:
                robot["explosion_counter"] = 0
            
            # Update explosion frame more slowly
            robot["explosion_counter"] += 1
            if robot["explosion_counter"] >= 15:  # Increase this number to slow down the explosion
                if robot["explosion_index"] < len(explosion_images):
                    window.blit(explosion_images[robot["explosion_index"]], (robot_screen_pos, robot["rect"].y))
                    robot["explosion_index"] += 1  # Move to the next frame
                    robot["explosion_counter"] = 0  # Reset counter
                else:
                    # Remove the robot after explosion animation completes
                    robots.remove(robot)
            else:
                # Continue displaying current explosion frame
                if robot["explosion_index"] < len(explosion_images):
                    window.blit(explosion_images[robot["explosion_index"]], (robot_screen_pos, robot["rect"].y))
        else:
            # Draw the robot
            window.blit(robot_frames[robot_animation_index], (robot_screen_pos, robot["rect"].y))
            # Draw health bar for the robot
            draw_health_bar(window, robot_screen_pos + 75, robot["rect"].y - 15, robot["health"], 2)  # Max health as 2


    # Draw the AI image
    window.blit(ai_image, (ai_rect.x - scroll_x, ai_rect.y))

    # Draw the character
    if is_attacking:
        window.blit(attack_images[attack_animation_index], character_rect.topleft)  # Draw attack animation
    else:
        window.blit(current_image, character_rect.topleft)

    # Draw the player's health bar in the top right corner
    draw_health_bar(window, window_size[0] - 160, 20, character_health, 100)  # Increased size

    # Draw rectangles for debugging
    pygame.draw.rect(window, (255, 0, 0), character_rect, 2)  # Draw player rectangle in red
    for robot in robots:
        # Draw the robot's hitbox for debugging purposes (adjusted for scrolling)
        adjusted_robot_rect = robot["rect"].copy()
        adjusted_robot_rect.x -= scroll_x  # Adjust for scrolling
        pygame.draw.rect(window, (0, 255, 0), adjusted_robot_rect, 2)  # Draw robot rectangles in green

    # Calculate remaining robots and draw quest bar
    remaining_robots = len([robot for robot in robots if not robot["is_exploding"]])
    draw_quest_bar(window, remaining_robots)

    pygame.display.flip()

pygame.quit()
sys.exit()