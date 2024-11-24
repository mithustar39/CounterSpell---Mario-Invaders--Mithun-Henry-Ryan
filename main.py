import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

die_sound = pygame.mixer.Sound("assets/bop.wav")

# Load and scale images
def load_and_scale_image(path, scale_factor):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale_by(image, scale_factor)

# Get screen dimensions for fullscreen mode
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h  # Fullscreen dimensions
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flappy Space Shooter")

# Load and scale background image
background_image = pygame.image.load("assets/background.png").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Scrolling background variables
background_x = 0  # Initial position for background

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player settings
player_image1 = load_and_scale_image("assets/yoshi.png", 0.36)
player_image2 = load_and_scale_image("assets/flyYoshi.png", 0.36)
player_rect = player_image1.get_rect()
player_rect.x = 100
player_rect.y = HEIGHT // 2
player_speed_y = 0
gravity = 0.6
flap_power = -12

# Mirror player settings (on the right side of the screen)
mirror_player_image = load_and_scale_image("assets/mirror_player.png", 0.3)
mirror_player_rect = mirror_player_image.get_rect()
mirror_player_rect.x = WIDTH * 0.9  # Position it on the far right side
mirror_player_base_y = HEIGHT // 2 - HEIGHT*0.16  # Base position for oscillation
mirror_hp = 3

# Enemy settings
enemy_image = load_and_scale_image("assets/goomba.png", 0.1)
enemy_rect = enemy_image.get_rect()
enemy_speed_x = 3
enemies = []

# Bullet settings
bullet_image = load_and_scale_image("assets/fireball.png", 0.3)
mirror_bullet_image = load_and_scale_image("assets/mirrorfireball.png", 0.15)
bullet_speed = 10
mirror_bullet_speed = -10
player_bullets = []
mirror_player_bullets = []
bullet_cooldown = 300  # Cooldown in milliseconds
last_player_bullet_time = 0
last_mirror_bullet_time = 0

# Health bar settings
healthbar_image = load_and_scale_image("assets/healthbar.png", 0.3)
healthbar_rect = healthbar_image.get_rect()
healthbar_rect.x = WIDTH*0.02  # Position it at the top left side
healthbar_rect.y = HEIGHT*0.03  # Position it at the top

# Game variables
max_lives = 12
lives = 11
player_score = 0
level_started = False
boss = None
boss_health = 0

# Font
font = pygame.font.Font(None, 50)

frequency = 1  # How many oscillations per second

# Spawn enemies
def spawn_enemy(count):
    """Spawn a specific number of enemies at random positions above a certain area."""
    for _ in range(count):
        min_y = round(HEIGHT * 0.1)  # Minimum y (10% from the top)
        max_y = round(HEIGHT * 0.9 - enemy_rect.height)  # Maximum y (90% from the top)
        y_position = random.randint(min_y, max_y)  # Ensure it’s within bounds
        enemy = pygame.Rect(WIDTH + random.randint(300, 500), y_position, enemy_rect.width, enemy_rect.height)
        enemies.append(enemy)

# Draw text
def draw_text(text, color, x, y):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def menu():
    # Load and scale background image for the menu
    menu_background = pygame.image.load("assets/intro.png").convert()
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))

    running = True
    while running:
        # Draw the menu background
        screen.blit(menu_background, (0, 0))
        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Start the game
                    return  # Exit the menu and continue to the game
                if event.key == pygame.K_ESCAPE:  # Quit the game
                    pygame.quit()
                    sys.exit()


def game_over_screen():
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("Game Over", RED, WIDTH // 2 - 100, HEIGHT // 3)
        draw_text(f"Your Score: {player_score}", WHITE, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Press ENTER to Restart or ESC to Quit", WHITE, WIDTH // 2 - 200, HEIGHT // 2 + 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def you_win_screen():
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("You Win!", BLUE, WIDTH // 2 - 100, HEIGHT // 3)
        draw_text(f"Your Score: {player_score}", WHITE, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Press ENTER to Restart or ESC to Quit", WHITE, WIDTH // 2 - 200, HEIGHT // 2 + 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Main game loop
def play():
    global player_speed_y, last_player_bullet_time, last_mirror_bullet_time, mirror_hp
    global lives, player_score, level_started, boss, boss_health, background_x
    global player_bullets, mirror_player_bullets, mirror_player_rect

    # Stage management variables
    stage = 1
    stage1_enemies_remaining = 10  # Number of enemies in the first stage
    stage2_enemies_remaining = 20  # Number of enemies in the second stage
    multi_shot_1_cooldown = 5000  # Cooldown duration for multi-shot in milliseconds
    last_multi_shot_1_time = 0  # Last time the multi-shot for K_1 was used

    running = True

    # Spawn initial enemies for Stage 1
    spawn_enemy(stage1_enemies_remaining)

    # Variables for flap effect
    flap_time = 0  # Time when flap started
    flap_duration = 200  # Flap duration in milliseconds (0.5 seconds)
    menu()
    running = True    
    while running:

        # Scroll background
        background_x -= 1.5
        if background_x <= -WIDTH:
            background_x = 0
        screen.blit(background_image, (background_x, 0))
        screen.blit(background_image, (background_x + WIDTH, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player flapping
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            flap_time = pygame.time.get_ticks()  # Reset the flap time whenever the space bar is pressed
            player_speed_y = flap_power

        # Determine which player image to use
        if flap_time > 0 and pygame.time.get_ticks() - flap_time <= flap_duration:
            player_image = player_image2  # Use flyYoshi for flap duration
        else:
            player_image = player_image1  # Use normal yoshi after flap

        # Main player shooting
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_f] and current_time - last_player_bullet_time >= bullet_cooldown:
            player_bullets.append({
                "rect": pygame.Rect(player_rect.x + player_rect.width, player_rect.y + player_rect.height // 2, bullet_image.get_width(), bullet_image.get_height()),
                "dx": bullet_speed,
                "dy": 0
            })
            last_player_bullet_time = current_time

        # Mirror player shooting
        shotangles = [0, 10, 20, -10, -20]  # Spread bullet angles for Stage 3
        if keys[pygame.K_f] and current_time - last_mirror_bullet_time >= bullet_cooldown:
            if stage < 3:  # Stage 1 and Stage 2: straight-line bullets
                mirror_player_bullets.append({
                    "rect": pygame.Rect(mirror_player_rect.x, mirror_player_rect.y + mirror_player_rect.height // 2, mirror_bullet_image.get_width(), mirror_bullet_image.get_height()),
                    "dx": mirror_bullet_speed,
                    "dy": 0
                })
            elif stage == 3:  # Stage 3: shooting spread bullets
                for i in range(5):
                    angle_radians = math.radians(shotangles[i])  # Convert angle to radians
                    dx = mirror_bullet_speed * math.cos(angle_radians)
                    dy = mirror_bullet_speed * math.sin(angle_radians)
                    mirror_player_bullets.append({
                        "rect": pygame.Rect(mirror_player_rect.x, mirror_player_rect.y + mirror_player_rect.height // 2, mirror_bullet_image.get_width(), mirror_bullet_image.get_height()),
                        "dx": dx,
                        "dy": dy
                    })
            last_mirror_bullet_time = current_time

        if keys[pygame.K_a] and (current_time-last_multi_shot_1_time) >= multi_shot_1_cooldown:
            for i in range(5):
                angle_radians = math.radians(shotangles[i])  # Convert angle to radians
                dx = bullet_speed * math.cos(angle_radians)
                dy = bullet_speed * math.sin(angle_radians)
                player_bullets.append({
                    "rect": pygame.Rect(player_rect.x, player_rect.y + player_rect.height // 2, bullet_image.get_width(), bullet_image.get_height()),
                    "dx": dx,
                    "dy": dy
                })
                # Update the last time multi-shot for K_1 was used
            last_multi_shot_1_time = current_time
        
        # Apply gravity to the main player
        player_speed_y += gravity
        player_rect.y += player_speed_y

        # Keep player within screen bounds
        if player_rect.y < 0:
            player_rect.y = 0
            player_speed_y = 0
        if player_rect.y > HEIGHT - player_rect.height - HEIGHT * 0.1:
            player_rect.y = HEIGHT - player_rect.height - HEIGHT * 0.1
            player_speed_y = 0

        current_time = pygame.time.get_ticks() / 1000  # Time in seconds
        # Move mirror player vertically to match the main player
        if stage < 3:
            mirror_player_rect.y = player_rect.y - HEIGHT*0.04
        else:
            # Oscillate the mirror player vertically
            mirror_player_rect.y = mirror_player_base_y + HEIGHT * 0.325 * math.sin(2 * math.pi * frequency * current_time)
            for bullet in player_bullets[:]:
                if mirror_player_rect.colliderect(bullet["rect"]):
                    #draw_health_bar()
                    if mirror_hp <= 0:
                        you_win_screen()
                        break
                    player_bullets.remove(bullet)
                    mirror_hp -= 1
                    player_score += 1  # Assuming 'layer_score' was meant to be 'player_score'
        
        
        # Check collision between mirror player and player bullets
        # Move enemies
        for enemy in enemies[:]:
            enemy.x -= enemy_speed_x
            if enemy.right < 0:
                enemies.remove(enemy)
                lives -= 0.5
            elif enemy.colliderect(player_rect):
                lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    running = False

        # Update bullets
        for bullet in player_bullets[:]:
            bullet["rect"].x += bullet["dx"]
            bullet["rect"].y += bullet["dy"]
            if bullet["rect"].x > WIDTH or bullet["rect"].y < 0 or bullet["rect"].y > HEIGHT:
                player_bullets.remove(bullet)

        for mirror_bullet in mirror_player_bullets[:]:
            mirror_bullet["rect"].x += mirror_bullet["dx"]
            mirror_bullet["rect"].y += mirror_bullet["dy"]
            if mirror_bullet["rect"].x < 0 or mirror_bullet["rect"].y < 0 or mirror_bullet["rect"].y > HEIGHT:
                mirror_player_bullets.remove(mirror_bullet)

        # Check bullet collisions with enemies
        for bullet in player_bullets[:]:
            for enemy in enemies[:]:
                if enemy.colliderect(bullet["rect"]):
                    pygame.mixer.Sound.play(die_sound)
                    player_bullets.remove(bullet)
                    enemies.remove(enemy)
                    player_score += 1
                    break

        for bullet in mirror_player_bullets[:]:
            for enemy in enemies[:]:
                if enemy.colliderect(bullet["rect"]):
                    mirror_player_bullets.remove(bullet)
                    enemies.remove(enemy)
                    player_score += 1
                    break
        
        for bullet in mirror_player_bullets[:]:
            for enemy in enemies[:]:
                if enemy.colliderect(bullet["rect"]):
                    mirror_player_bullets.remove(bullet)
                    enemies.remove(enemy)
                    player_score += 1
                    break

        # Check collision between main player and mirror player bullets
        for bullet in mirror_player_bullets[:]:
            if player_rect.colliderect(bullet["rect"]):
                mirror_player_bullets.remove(bullet)
                lives -= 1
                if lives <= 0:
                    running = False
                break

        # Update health bar width based on current lives
        # Update health bar based on current lives
        total_width = healthbar_image.get_width()
        current_healthbar_width = total_width * ((lives + 1) / max_lives)

        # Create a new cropped rect to only show the portion of the health bar
        cropped_healthbar_rect = pygame.Rect(0, 0, current_healthbar_width, healthbar_image.get_height())

        # Blit the cropped health bar onto the screen
        screen.blit(healthbar_image, healthbar_rect, cropped_healthbar_rect)

        # Draw the player, mirror player, bullets, enemies
        screen.blit(player_image, player_rect)
        screen.blit(mirror_player_image, mirror_player_rect)
        for bullet in player_bullets:
            screen.blit(bullet_image, bullet["rect"])
        for mirror_bullet in mirror_player_bullets:
            screen.blit(mirror_bullet_image, mirror_bullet["rect"])
        for enemy in enemies:
            screen.blit(enemy_image, enemy)

        # Draw score and lives
        draw_text(f"Score: {player_score}", WHITE, 10, 10)
        draw_text(f"Stage: {stage}", WHITE, WIDTH/2, 40)

        # Check stage completion
        if stage == 1 and len(enemies) == 0:
            stage += 1  # Proceed to next stage
            spawn_enemy(stage2_enemies_remaining)
        if stage == 2 and len(enemies) == 0:
            stage += 1  # Proceed to next stage
            spawn_enemy(stage1_enemies_remaining)
        if stage == 3 and len(enemies) == 0:
            gameState = "win"
        if lives < 0:
            gameState = "lose"

        # Update the score
        player_score += 1

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

def reset_game():
    global lives, player_score, stage, enemies, player_bullets, mirror_player_bullets, mirror_hp, level_started
    lives = 11
    player_score = 0
    stage = 1
    enemies = []
    player_bullets = []
    mirror_player_bullets = []
    mirror_hp = 3
    level_started = False
    player_rect.y = HEIGHT // 2  # Reset player position
    mirror_player_rect.y = HEIGHT // 2  # Reset mirror player position

def main():
    while True:
        pygame.mixer.music.load('assets/mp.wav')
        pygame.mixer.music.play(-1)
        # Reset the game to its initial state
        reset_game()

        # Play the game
        play()

        # Once the game ends, decide based on user input
        game_over_screen()

    
if __name__ == "__main__":
    main()