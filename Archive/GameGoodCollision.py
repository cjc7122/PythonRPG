import pygame
import pytmx

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 16
FPS = 60
WHITE = (255, 255, 255)
PLAYER_SPEED = 5

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
hitbox_height = 16  # Height of the hitbox
hitbox_offset_x = (player_width - hitbox_width) // 2  # Offset to center the hitbox horizontally
hitbox_offset_y = player_height - hitbox_height  # Offset to place the hitbox at the bottom of the player

player_hitbox = pygame.Rect(player_rect.x + (player_width - hitbox_width) // 2, player_rect.bottom - hitbox_height, hitbox_width, hitbox_height)

# Rendering the background and obstacle layers
def render_map(screen, tmx_data, player_rect):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            if layer.name != "Trees":  # Exclude the Trees layer from rendering
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    # Render player above ground1 and below ground2
    screen.blit(player_image, player_rect)

    # Render trees layer after player to ensure player cannot go into trees
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            if layer.name == "Trees":  # Render trees layer
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    prev_player_rect = player_rect.copy()

    # Handling player movement
    keys = pygame.key.get_pressed()
    # Attempt to move right
    if keys[pygame.K_d]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox

    # Attempt to move left
    if keys[pygame.K_a]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(-PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(-PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox

    # Attempt to move up
    if keys[pygame.K_w]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, -PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, -PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox

    # Attempt to move down
    if keys[pygame.K_s]:
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox

    # Update player's hitbox position
    player_hitbox.x = player_rect.x + hitbox_offset_x
    player_hitbox.y = player_rect.y + hitbox_offset_y

    # Rendering the map
    screen.fill(WHITE)
    render_map(screen, tmx_data, player_rect)

    # Draw hitbox rectangle
    pygame.draw.rect(screen, (255, 0, 0), player_hitbox, 2)  # Draw a red rectangle around the hitbox

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
