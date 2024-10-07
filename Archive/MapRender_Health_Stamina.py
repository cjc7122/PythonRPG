import pygame
import pytmx

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 16
FPS = 60
WHITE = (255, 255, 255)
STEALTH_SPEED = 3  # Speed when in stealth
NORMAL_SPEED = 5  # Normal Speed
SPRINT_SPEED = 8  # Speed when sprinting
SPRINT_KEY = pygame.K_LSHIFT
STEALTH_KEY = pygame.K_LCTRL
STAMINA_MAX = 100  # Maximum stamina
SPRINT_DECREASE_RATE = 1  # Stamina decrease rate when sprinting
STEALTH_DECREASE_RATE = .5 # Stamina decrease rate when in stealth
STAMINA_REGEN_RATE = 0.1  # Stamina regeneration rate when not sprinting
STAMINA_GAIN = .0001
MIN_STAMINA = 1  # Minimum stamina required to sprint
HEALTH_MAX = 100 #Maximum health

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiled Map")

# Load Tiled map
tmx_data = pytmx.load_pygame("Map1.tmx")  # Change "example.tmx" to your tiled map file

# Main character
player_image = pygame.image.load("character.png")  # Replace "character.png" with your character image file
player_rect = player_image.get_rect()
player_width, player_height = player_rect.size
player_rect.x, player_rect.y = 200, 200  # Initial position of the player

# Adjusting hitbox
hitbox_width = 8  # Width of the hitbox
hitbox_height = 24  # Height of the hitbox
hitbox_offset_x = (player_width - hitbox_width) // 2  # Offset to center the hitbox horizontally
hitbox_offset_y = player_height - hitbox_height  # Offset to place the hitbox at the bottom of the player
secondary_hitbox_width = 32
secondary_hitbox_height = 48
secondary_hitbox_color = (0, 0, 255)
secondary_hitbox_offset_y = player_height - secondary_hitbox_height

player_hitbox = pygame.Rect(player_rect.x + (player_width - hitbox_width) // 2, player_rect.bottom - hitbox_height, hitbox_width, hitbox_height)
secondary_hitbox = pygame.Rect(player_rect.centerx - secondary_hitbox_width // 2, player_rect.centery - secondary_hitbox_height // 2, secondary_hitbox_width, secondary_hitbox_height)

stamina = STAMINA_MAX
health = HEALTH_MAX

# Function to render the map with the player centered and adjust for scrolling
def render_map_centered(screen, tmx_data, player_rect, player_hitbox):
    # Calculate the offset to keep the player centered
    map_offset_x = WIDTH // 2 - player_rect.centerx
    map_offset_y = HEIGHT // 2 - player_rect.centery

    # Adjust the offset to handle scrolling when the player reaches the edge of the screen
    if player_rect.left < WIDTH // 4:
        map_offset_x += PLAYER_SPEED  # Scroll right
    elif player_rect.right > WIDTH * 3 // 4:
        map_offset_x -= PLAYER_SPEED  # Scroll left
    if player_rect.top < HEIGHT // 4:
        map_offset_y += PLAYER_SPEED  # Scroll down
    elif player_rect.bottom > HEIGHT * 3 // 4:
        map_offset_y -= PLAYER_SPEED  # Scroll up

    # Render the "ground" layer
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Ground":
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, ((x * tmx_data.tilewidth) + map_offset_x, (y * tmx_data.tileheight) + map_offset_y))
        elif isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Ground2":
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, ((x * tmx_data.tilewidth) + map_offset_x, (y * tmx_data.tileheight) + map_offset_y))



    # Calculate the position of the player and hitbox relative to the center of the screen
    player_pos_centered = (WIDTH // 2 - player_rect.width // 2, HEIGHT // 2 - player_rect.height // 2)
    hitbox_pos_centered = (player_pos_centered[0] + hitbox_offset_x, player_pos_centered[1] + hitbox_offset_y)
    secondary_hitbox_pos_centered = (player_pos_centered[0] + player_rect.width // 2 - secondary_hitbox_width // 2, player_pos_centered[1] + secondary_hitbox_offset_y)

    # Render player at the center of the screen
    screen.blit(player_image, player_pos_centered)

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Trees":
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, ((x * tmx_data.tilewidth) + map_offset_x, (y * tmx_data.tileheight) + map_offset_y))


    # Draw hitbox rectangle at the center of the screen
    pygame.draw.rect(screen, (255, 0, 0), (hitbox_pos_centered[0], hitbox_pos_centered[1], hitbox_width, hitbox_height), 2)
    pygame.draw.rect(screen, secondary_hitbox_color, (secondary_hitbox_pos_centered[0], secondary_hitbox_pos_centered[1], secondary_hitbox_width, secondary_hitbox_height), 2)

    # Draw stamina bar
    status_bar_width = 100
    status_bar_height = 10
    status_bar_padding = 5
    health_bar_x = WIDTH - status_bar_width - status_bar_padding
    health_bar_y = status_bar_padding
    health_fill_width = (health / HEALTH_MAX) * status_bar_width
    health_bar_rect = pygame.Rect(health_bar_x, health_bar_y, health_fill_width, status_bar_height)
    health_color = (0, 255, 0) if health >= (HEALTH_MAX * .3) else (255, 255, 0)
    stamina_bar_x = WIDTH - status_bar_width - status_bar_padding
    stamina_bar_y = status_bar_padding + (health_bar_y * 2)
    stamina_fill_width = (stamina / STAMINA_MAX) * status_bar_width
    stamina_bar_rect = pygame.Rect(stamina_bar_x, stamina_bar_y, stamina_fill_width, status_bar_height)
    stamina_color = (0, 0, 225) if stamina >= (STAMINA_MAX * .3) else (255, 255, 0)
    
    pygame.draw.rect(screen, health_color, health_bar_rect)
    pygame.draw.rect(screen, stamina_color, stamina_bar_rect)

# Function to check if the player's hitbox is colliding with any obstacles
def is_hitbox_colliding(tmx_data, player_hitbox):
    obstacle_layer_name = "Trees"  # Change this to the name of your obstacle layer
    obstacle_layer_index = None

    # Find the index of the obstacle layer
    for i, layer in enumerate(tmx_data.visible_layers):
        if isinstance(layer, pytmx.TiledTileLayer) and layer.name == obstacle_layer_name:
            obstacle_layer_index = i
            break

    # If obstacle layer not found, return False
    if obstacle_layer_index is None:
        return False

    # Get the tile coordinates that intersect with the player's hitbox
    intersecting_tiles = []
    for y in range(int(player_hitbox.y // tmx_data.tileheight), int((player_hitbox.y + player_hitbox.height) // tmx_data.tileheight) + 1):
        for x in range(int(player_hitbox.x // tmx_data.tilewidth), int((player_hitbox.x + player_hitbox.width) // tmx_data.tilewidth) + 1):
            intersecting_tiles.append((x, y))

    # Check if any of the intersecting tiles are obstacles
    for x, y in intersecting_tiles:
        tile_gid = tmx_data.get_tile_gid(x, y, obstacle_layer_index)
        if tile_gid != 0:
            return True

    return False

def print_tile_data(tmx_data, player_rect):
    player_tile_x = int(player_rect.centerx // tmx_data.tilewidth)
    player_tile_y = int(player_rect.centery // tmx_data.tileheight)

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            if 0 <= player_tile_y < layer.height and 0 <= player_tile_x < layer.width:
                tile_gid = layer.data[player_tile_y][player_tile_x]
                tile_properties = tmx_data.get_tile_properties_by_gid(tile_gid)
                print("Tile Data for Player's Position:")
                print("Layer Name:", layer.name)
                print("Tile GID:", tile_gid)
                print("Tile Properties:", tile_properties)

# Game loop
running = True
clock = pygame.time.Clock()
sprinting = False
stealth = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    prev_player_rect = player_rect.copy()

    # Handling player movement
    keys = pygame.key.get_pressed()

    if stamina < 1:
        MIN_STAMINA = 30
    
    if stamina >= MIN_STAMINA:
        MIN_STAMINA = 1

    # Detect sprint key press
    enable_sprinting = keys[SPRINT_KEY] and stamina >= MIN_STAMINA
    if enable_sprinting:
        sprinting = True

    # Detect stealth key press
    enable_stealth = keys[STEALTH_KEY] and stamina >= MIN_STAMINA
    if enable_stealth:
        stealth = True

    # Decrease stamina when sprinting
    if sprinting and stamina >= 1:
        speed = SPRINT_SPEED
        stamina -= SPRINT_DECREASE_RATE
        STAMINA_MAX += STAMINA_GAIN
    elif stealth and stamina >= 1:
        speed = STEALTH_SPEED
        stamina -= STEALTH_DECREASE_RATE
        STAMINA_MAX += STAMINA_GAIN
    else:
        speed = NORMAL_SPEED
        sprinting = False
        stealth = False

    # Regenerate stamina when not sprinting
    if not sprinting and stamina < STAMINA_MAX:
        stamina += STAMINA_REGEN_RATE

    if not keys[SPRINT_KEY]:
        sprinting = False

    PLAYER_SPEED = SPRINT_SPEED if sprinting else NORMAL_SPEED

    # Attempt to move right
    if keys[pygame.K_d]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(PLAYER_SPEED, 0)
        potential_secondary_hitbox = secondary_hitbox.move(PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox

    # Attempt to move left
    if keys[pygame.K_a]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(-PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(-PLAYER_SPEED, 0)
        potential_secondary_hitbox = secondary_hitbox.move(-PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox

    # Attempt to move up
    if keys[pygame.K_w]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, -PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, -PLAYER_SPEED)
        potential_secondary_hitbox = secondary_hitbox.move(0, -PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox

    # Attempt to move down
    if keys[pygame.K_s]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, PLAYER_SPEED)
        potential_secondary_hitbox = secondary_hitbox.move(0, PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox

    # Update player's hitbox position
    player_hitbox.x = player_rect.x + hitbox_offset_x
    player_hitbox.y = player_rect.y + hitbox_offset_y 

    # Rendering the map
    screen.fill(WHITE)
    render_map_centered(screen, tmx_data, player_rect, player_hitbox)

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
