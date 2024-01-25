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
tmx_data = pytmx.load_pygame("example.tmx")  # Change "example.tmx" to your tiled map file

# Main character
player_image = pygame.image.load("character.png")  # Replace "character.png" with your character image file
player_rect = player_image.get_rect()
player_rect.x, player_rect.y = 200, 200  # Initial position of the player

# Get the obstacle layer
obstacle_layer = tmx_data.get_layer_by_name("obstacle_layer")

# Rendering the map
def render_map(screen, tmx_data):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer) and layer != obstacle_layer:
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handling player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and not tmx_data.get_tile_properties(int(player_rect.x / TILE_SIZE) - 1, int(player_rect.y / TILE_SIZE), obstacle_layer):
        player_rect.x -= PLAYER_SPEED
    if keys[pygame.K_d] and not tmx_data.get_tile_properties(int(player_rect.x / TILE_SIZE) + 1, int(player_rect.y / TILE_SIZE), obstacle_layer):
        player_rect.x += PLAYER_SPEED
    if keys[pygame.K_w] and not tmx_data.get_tile_properties(int(player_rect.x / TILE_SIZE), int(player_rect.y / TILE_SIZE) - 1, obstacle_layer):
        player_rect.y -= PLAYER_SPEED
    if keys[pygame.K_s] and not tmx_data.get_tile_properties(int(player_rect.x / TILE_SIZE), int(player_rect.y / TILE_SIZE) + 1, obstacle_layer):
        player_rect.y += PLAYER_SPEED

    # Rendering the map
    screen.fill(WHITE)
    render_map(screen, tmx_data)

    # Draw the player
    screen.blit(player_image, player_rect)

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
