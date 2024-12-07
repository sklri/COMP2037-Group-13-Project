import pygame
import sys
import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_style = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Initialize Pygame
pygame.init()
pygame.font.init()

# Set up the display
window_size = (1024, 768)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Try Scrolling")

# Load the full-size background image
full_background = pygame.image.load("stage 2 bg.png")
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
obstacle_image = pygame.image.load("Concrete.png")
obstacle_image = pygame.transform.scale(obstacle_image, (249, 40))

# Load robot animation frames
ganimals_frames = [
    pygame.image.load("ganimals01.png"),
    pygame.image.load("ganimals02.png"),
    pygame.image.load("ganimals03.png"),
    pygame.image.load("ganimals04.png"),
    pygame.image.load("ganimals05.png"),
]

fanimals_frames = [
    pygame.image.load("fanimals01.png"),
    pygame.image.load("fanimals02.png"),
    pygame.image.load("fanimals03.png"),
    pygame.image.load("fanimals04.png"),
    pygame.image.load("fanimals05.png"),
]

# Initialize character rectangle
character_rect = default_image.get_rect()
character_rect.centerx = window_size[0] // 2  # Start at middle of screen
character_rect.y = 445

# Define health values
character_health = 100

# Robot setup
ganimals = [
    {"rect": pygame.Rect(1240, 25, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(3450, 320, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
]

fanimals = [

    {"rect": pygame.Rect(850, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(2350, 450, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},
    {"rect": pygame.Rect(2650, 150, 40, 80), "health": 2, "last_hurt_time": 0, "damage_cooldown": 0, "is_exploding": False, "explosion_index": 0},

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
ganimals_animation_index = 0
ganimals_animation_timer = 0
ganimals_animation_delay = 15

fanimals_animation_index = 0
fanimals_animation_timer = 0
fanimals_animation_delay = 15

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

def draw_quest_bar(surface, remaining_ganimals):
    font = pygame.font.SysFont('Arial', 24)
    quest_text = font.render(f"Quest: Kill all 5 mutated animals", True, (255, 255, 255))
    remaining_text = font.render(f"Remaining: {remaining_ganimals}", True, (255, 255, 255))

def draw_quest_bar(surface, remaining_fanimals):
    font = pygame.font.SysFont('Arial', 24)
    quest_text = font.render(f"Quest: Kill all 5 mutated animals", True, (255, 255, 255))
    remaining_text = font.render(f"Remaining: {remaining_fanimals}", True, (255, 255, 255))
    
    # Draw background rectangle for quest text
    quest_bg = pygame.Surface((400, 60))
    quest_bg.fill((0, 0, 0))
    quest_bg.set_alpha(128)
    surface.blit(quest_bg, (10, 10))
    
    # Draw the text
    surface.blit(quest_text, (20, 15))
    surface.blit(remaining_text, (20, 40))

Jump_X, Jump_Y = 200, 650
Left_X, Left_Y = 100, 800
Right_X, Right_Y = 300, 800
Attack_X, Attack_Y = 1700, 800
ws_x= 130
ws_y = 130

cap = cv2.VideoCapture(0)

# Main loop
running = True
LEFT = False  # Initialize LEFT variable

with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Store previous position
        prev_y = character_rect.y

        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        LEFT = False  # Reset LEFT flag at start of each frame
        
        # Process image
        image = cv2.flip(image, 1)
        image = cv2.resize(image,(1900,1080))
        
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        height, width, _ = image.shape

        # Draw rectangles for controls
        image = cv2.rectangle(image, (Jump_X, Jump_Y), (Jump_X + ws_x, Jump_Y + ws_y), (0, 0, 255), 3)
        image = cv2.rectangle(image, (Left_X, Left_Y), (Left_X + ws_x, Left_Y + ws_y), (0, 0, 255), 3)
        image = cv2.rectangle(image, (Right_X, Right_Y), (Right_X + ws_x, Right_Y + ws_y), (0, 0, 255), 3)
        image = cv2.rectangle(image, (Attack_X, Attack_Y), (Attack_X + ws_x, Attack_Y + ws_y), (0, 0, 255), 3)

        LEFT = False  # Reset LEFT flag at start of each frame

        if results.multi_hand_landmarks:
            for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
                Finger_X = round(hand_landmarks.landmark[8].x * width)
                Finger_Y = round(hand_landmarks.landmark[8].y * height)

                # Jumping logic
                if (Jump_X <= Finger_X <= Jump_X + ws_x and 
                    Jump_Y <= Finger_Y <= Jump_Y + ws_y and 
                    not is_jumping):
                    is_jumping = True
                    velocity_y = jump_velocity
                
                # Attacking logic
                if (Attack_X <= Finger_X <= Attack_X + ws_x and 
                    Attack_Y <= Finger_Y <= Attack_Y + ws_y and 
                    not is_jumping):  
                    attack = True
                    attack_start_time = pygame.time.get_ticks()  # Record the start time of the attack

                # Movement and scrolling logic
                if (Left_X <= Finger_X <= Left_X + ws_x and 
                    Left_Y <= Finger_Y <= Left_Y + ws_y):  
                    LEFT = True
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

                if (Right_X <= Finger_X <= Right_X + ws_x and 
                    Right_Y <= Finger_Y <= Right_Y + ws_y):
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
                    
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_style.get_default_hand_landmarks_style(),
                        mp_drawing_style.get_default_hand_connections_style()
                    )

        if not LEFT:
            current_image = default_image
            animation_index = 0

        # Apply gravity
        character_rect.y -= velocity_y
        velocity_y -= gravity

        # Check if character is on a platform
        on_platform = is_on_platform(character_rect, obstacles)

        # Collision detection with robots
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        for ganimal in ganimals:
            # Adjusted robot position for checking collisions
            ganimal_rect = ganimal["rect"].copy()
            ganimal_rect.y += 50  
            ganimal_rect.x -= scroll_x  # Adjust for scrolling

            # Check if the robot can hurt the character
            if character_rect.colliderect(ganimal_rect):
                # Determine if attack is active
                if attack:
                    # Check if the robot is within damage cooldown
                    if current_time - ganimal["damage_cooldown"] >= 2000:  # 2000 ms = 2 seconds
                        # Damage the robot
                        ganimal["health"] -= 1
                        print(f"Mutated animal hit! Current health: {ganimal['health']}")
                        ganimal["damage_cooldown"] = current_time  # Set the time of the last damage
                        is_attacking = True  # Start the attack animation
                        attack_start_time = current_time  # Record the start time of the attack
                        attack_animation_index = 0  # Reset animation index
                        if ganimal["health"] <= 0:  # Check if the robot's health is zero or less
                            ganimal["is_exploding"] = True  # Start the explosion animation
                            ganimal["explosion_index"] = 0  # Reset explosion frame index
                            print("Mutated animal destroyed!")
                else:
                    # Check if cooldown has expired
                    if current_time - ganimal["last_hurt_time"] >= 3000:  # 3000 ms = 3 seconds
                        character_health -= 25
                        if character_health < 0:
                            character_health = 0  # Prevent negative health
                        print(f"Collision with mutated animal! Player Health: {character_health}")  # Debugging output
                        ganimal["last_hurt_time"] = current_time  # Update last hurt time

                # Prevent movement when colliding with robots
                if character_rect.right > ganimal_rect.left and character_rect.left < ganimal_rect.right:
                    if character_rect.bottom > ganimal_rect.top and character_rect.top < ganimal_rect.bottom:
                        # Determine the direction of collision
                        if character_rect.centery < ganimal_rect.centery:
                            character_rect.bottom = ganimal_rect.top  # Land on top of robot
                            is_jumping = False
                            velocity_y = 0
                        else:
                            character_rect.top = ganimal_rect.bottom  # Push character up
                        break  # Exit the loop after handling collision


        for fanimal in fanimals:
            # Adjusted robot position for checking collisions
            fanimal_rect = fanimal["rect"].copy()
            fanimal_rect.y += 10  # Move the hitbox down by 10 pixels
            fanimal_rect.x -= scroll_x  # Adjust for scrolling

            # Check if the robot can hurt the character
            if character_rect.colliderect(fanimal_rect):
                # Determine if attack is active
                if attack:
                    # Check if the robot is within damage cooldown
                    if current_time - fanimal["damage_cooldown"] >= 2000:  # 2000 ms = 2 seconds
                        # Damage the robot
                        fanimal["health"] -= 1
                        print(f"Mutated animal hit! Current health: {ganimal['health']}")
                        ganimal["damage_cooldown"] = current_time  # Set the time of the last damage
                        is_attacking = True  # Start the attack animation
                        attack_start_time = current_time  # Record the start time of the attack
                        attack_animation_index = 0  # Reset animation index
                        if fanimal["health"] <= 0:  # Check if the robot's health is zero or less
                            fanimal["is_exploding"] = True  # Start the explosion animation
                            fanimal["explosion_index"] = 0  # Reset explosion frame index
                            print("Mutated animal destroyed!")
                else:
                    # Check if cooldown has expired
                    if current_time - fanimal["last_hurt_time"] >= 3000:  # 3000 ms = 3 seconds
                        character_health -= 25
                        if character_health < 0:
                            character_health = 0  # Prevent negative health
                        print(f"Collision with mutated animal! Player Health: {character_health}")  # Debugging output
                        fanimal["last_hurt_time"] = current_time  # Update last hurt time

                # Prevent movement when colliding with robots
                if character_rect.right > fanimal_rect.left and character_rect.left < fanimal_rect.right:
                    if character_rect.bottom > fanimal_rect.top and character_rect.top < fanimal_rect.bottom:
                        # Determine the direction of collision
                        if character_rect.centery < fanimal_rect.centery:
                            character_rect.bottom = fanimal_rect.top  # Land on top of robot
                            is_jumping = False
                            velocity_y = 0
                        else:
                            character_rect.top = fanimal_rect.bottom  # Push character up
                        break  # Exit the loop after handling collision

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

        # Keep the scrolling within bounds
        scroll_x = max(0, min(scroll_x, full_background.get_width() - window_size[0]))

        # Keep character within screen bounds
        character_rect.x = max(0, min(character_rect.x, window_size[0] - character_rect.width))

        # Update obstacle positions based on scroll
        update_obstacle_positions(scroll_x)

        # Robot animation logic
        ganimals_animation_timer += 1
        if ganimals_animation_timer >= ganimals_animation_delay:
            ganimals_animation_index = (ganimals_animation_index + 1) % len(ganimals_frames)
            ganimals_animation_timer = 0

        # Robot animation logic
        fanimals_animation_timer += 1
        if fanimals_animation_timer >= fanimals_animation_delay:
            fanimals_animation_index = (fanimals_animation_index + 1) % len(fanimals_frames)
            fanimals_animation_timer = 0
        

        # Drawing
        window.blit(full_background, (-scroll_x, 0))

        # Draw obstacles
        for obstacle in obstacles:
            window.blit(obstacle["image"], obstacle["rect"])



        # Draw the robots with animation and health bars
        for ganimal in ganimals:
            ganimal_screen_pos = ganimal["rect"].x - scroll_x  # Adjust for scrolling
            if ganimal["is_exploding"]:
                # Add explosion animation counter if it doesn't exist
                if "explosion_counter" not in ganimal:
                    ganimal["explosion_counter"] = 0
                
                # Update explosion frame more slowly
                ganimal["explosion_counter"] += 1
                if ganimal["explosion_counter"] >= 15:  # Increase this number to slow down the explosion
                    if ganimal["explosion_index"] < len(explosion_images):
                        window.blit(explosion_images[ganimal["explosion_index"]], (ganimal_screen_pos, ganimal["rect"].y))
                        ganimal["explosion_index"] += 1  # Move to the next frame
                        ganimal["explosion_counter"] = 0  # Reset counter
                    else:
                        # Remove the robot after explosion animation completes
                        ganimals.remove(ganimal)
                else:
                    # Continue displaying current explosion frame
                    if ganimal["explosion_index"] < len(explosion_images):
                        window.blit(explosion_images[ganimal["explosion_index"]], (ganimal_screen_pos, ganimal["rect"].y))
            else:
                # Draw the robot
                window.blit(ganimals_frames[ganimals_animation_index], (ganimal_screen_pos, ganimal["rect"].y))
                # Draw health bar for the robot
                draw_health_bar(window, ganimal_screen_pos + 75, ganimal["rect"].y - 15, ganimal["health"], 2)  # Max health as 2

        for fanimal in fanimals:
            fanimal_screen_pos = fanimal["rect"].x - scroll_x  # Adjust for scrolling
            if fanimal["is_exploding"]:
                # Add explosion animation counter if it doesn't exist
                if "explosion_counter" not in fanimal:
                    fanimal["explosion_counter"] = 0
                
                # Update explosion frame more slowly
                fanimal["explosion_counter"] += 1
                if fanimal["explosion_counter"] >= 15:  # Increase this number to slow down the explosion
                    if fanimal["explosion_index"] < len(explosion_images):
                        window.blit(explosion_images[fanimal["explosion_index"]], (fanimal_screen_pos, fanimal["rect"].y))
                        fanimal["explosion_index"] += 1  # Move to the next frame
                        fanimal["explosion_counter"] = 0  # Reset counter
                    else:
                        # Remove the robot after explosion animation completes
                        fanimals.remove(fanimal)
                else:
                    # Continue displaying current explosion frame
                    if fanimal["explosion_index"] < len(explosion_images):
                        window.blit(explosion_images[fanimal["explosion_index"]], (fanimal_screen_pos, fanimal["rect"].y))
            else:
                # Draw the robot
                window.blit(fanimals_frames[fanimals_animation_index], (fanimal_screen_pos, fanimal["rect"].y))
                # Draw health bar for the robot
                draw_health_bar(window, fanimal_screen_pos + 75, fanimal["rect"].y - 15, fanimal["health"], 2)  # Max health as 2


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

        for ganimal in ganimals:
            # Draw the robot's hitbox for debugging purposes (adjusted for scrolling)
            adjusted_ganimal_rect = ganimal["rect"].copy()
            adjusted_ganimal_rect.y += 50  
            adjusted_ganimal_rect.x -= scroll_x  # Adjust for scrolling
            pygame.draw.rect(window, (0, 255, 0), adjusted_ganimal_rect, 2)  # Draw robot rectangles in green


        for fanimal in fanimals:
            # Draw the robot's hitbox for debugging purposes (adjusted for scrolling)
            adjusted_fanimal_rect = fanimal["rect"].copy()
            adjusted_fanimal_rect.y += 10 
            adjusted_fanimal_rect.x -= scroll_x  # Adjust for scrolling
            pygame.draw.rect(window, (0, 255, 0), adjusted_fanimal_rect, 2)  # Draw robot rectangles in green

        # Calculate remaining robots and draw quest bar
        remaining_ganimals = len([ganimal for ganimal in ganimals if not ganimal["is_exploding"]])
        draw_quest_bar(window, remaining_ganimals)

        remaining_fanimals = len([fanimal for fanimal in fanimals if not fanimal["is_exploding"]])
        draw_quest_bar(window, remaining_fanimals)

        pygame.display.flip()
        cv2.imshow('Mediapipe Hands', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()