import pygame
import pytmx
import sys, json
import random
from slime_monster import SlimeMonster
from player import Player

###TODO###
#Create a world LIST and add the player and any mobs/NPCs
#Create player class and add player to world list instead of rendering like we do now
#add mobs world list when they are created.
#modify LIST based on y value or feet.
#BLIT list in order of Y from top to bottom

# Initialize Pygame
pygame.init()

def load_game(selected_save):
    global save_file_path 
    save_file_path = f"saves/{selected_save}"

    # Implement functionality to load the game using the selected save file
    with open(save_file_path, "r") as f:
            save_data = json.load(f)
            # Extract data from the save file
            global STAMINA_MAX, SPRINT_DECREASE_RATE, STEALTH_DECREASE_RATE, STAMINA_REGEN_RATE, STAMINA_GAIN
            global MIN_STAMINA, HEALTH_MAX, STEALTH_SPEED, NORMAL_SPEED, SPRINT_SPEED, stamina, health
            STAMINA_MAX = save_data["STAMINA_MAX"]
            SPRINT_DECREASE_RATE = save_data["SPRINT_DECREASE_RATE"]
            STEALTH_DECREASE_RATE = save_data["STEALTH_DECREASE_RATE"]
            STAMINA_REGEN_RATE = save_data["STAMINA_REGEN_RATE"]
            STAMINA_GAIN = save_data["STAMINA_GAIN"]
            MIN_STAMINA = save_data["MIN_STAMINA"]
            HEALTH_MAX = save_data["HEALTH_MAX"]
            STEALTH_SPEED = save_data["STEALTH_SPEED"]
            NORMAL_SPEED = save_data["NORMAL_SPEED"]
            SPRINT_SPEED = save_data["SPRINT_SPEED"]
            stamina = save_data["stamina"]
            health = save_data["health"]

def save_game():
    save_data = {
        "STAMINA_MAX": STAMINA_MAX,
        "SPRINT_DECREASE_RATE": SPRINT_DECREASE_RATE,
        "STEALTH_DECREASE_RATE": STEALTH_DECREASE_RATE,
        "STAMINA_REGEN_RATE": STAMINA_REGEN_RATE,
        "STAMINA_GAIN": STAMINA_GAIN,
        "MIN_STAMINA": MIN_STAMINA,
        "HEALTH_MAX": HEALTH_MAX,
        "STEALTH_SPEED": STEALTH_SPEED,
        "NORMAL_SPEED": NORMAL_SPEED,
        "SPRINT_SPEED": SPRINT_SPEED,
        "stamina": stamina,
        "health": health
    }

    with open(save_file_path, "w") as f:
        json.dump(save_data, f, indent=4)

# Check if a save file name is provided as a command-line argument
selected_save = sys.argv[1]
load_game(selected_save)  # Call the load_game function with the selected save file name

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 16
FPS = 60
WHITE = (255, 255, 255)
SPRINT_KEY = pygame.K_LSHIFT
STEALTH_KEY = pygame.K_LCTRL
MOB_CAP = 5

# Load separate image sets for each direction
player_images = {
    "up": [pygame.image.load(f"./Player_Sprites/Playerup{i}.png") for i in range(8)],
    "down": [pygame.image.load(f"./Player_Sprites/Playerdown{i}.png") for i in range(8)],
    "left": [pygame.image.load(f"./Player_Sprites/Playerleft{i}.png") for i in range(8)],
    "right": [pygame.image.load(f"./Player_Sprites/Playerright{i}.png") for i in range(8)]
}

pant_images = {
    "up": [pygame.image.load(f"./Player_Sprites/Pantup{i}.png") for i in range(8)],
    "down": [pygame.image.load(f"./Player_Sprites/Pantdown{i}.png") for i in range(8)],
    "left": [pygame.image.load(f"./Player_Sprites/Pantleft{i}.png") for i in range(8)],
    "right": [pygame.image.load(f"./Player_Sprites/Pantright{i}.png") for i in range(8)]
}

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyRPG")

# Load Tiled map
tmx_data = pytmx.load_pygame("Map1.tmx")  # Change "example.tmx" to your tiled map file

# Main character
current_direction = "down"
current_frame = 0
frame_counter = 0
player_image = player_images[current_direction][current_frame]
player_pant = pant_images[current_direction][current_frame]
player_rect = player_image.get_rect()
pant_rect = player_pant.get_rect()
player_width, player_height = player_rect.size
pant_width, pant_height = pant_rect.size
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

# Menu variables
menu_font = pygame.font.Font(None, 36)
menu_items = ["Resume", "Save", "Options", "Quit"]
menu_selected = 0
menu_visible = False

def render_menu(screen):
    menu_surface = pygame.Surface((200, len(menu_items) * 40))
    menu_surface.fill((50, 50, 50))
    for i, item in enumerate(menu_items):
        color = (255, 255, 255) if i != menu_selected else (255, 0, 0)
        text = menu_font.render(item, True, color)
        menu_surface.blit(text, (20, 40 * i))
    screen.blit(menu_surface, (WIDTH // 2 - 100, HEIGHT // 2 - len(menu_items) * 20))

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
    screen.blit(player_images[current_direction][current_frame], player_pos_centered)
    screen.blit(pant_images[current_direction][current_frame], player_pos_centered)
    mob_spawn(map_offset_x, map_offset_y)

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

# Function to handle menu events
def handle_menu_events():
    global menu_selected, menu_visible, running
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        menu_selected = (menu_selected - 1) % len(menu_items)
    elif keys[pygame.K_DOWN]:
        menu_selected = (menu_selected + 1) % len(menu_items)
    elif keys[pygame.K_RETURN]:
        if menu_selected == 0:  # Resume
            menu_visible = False
        elif menu_selected == 1:  # Save
            save_game()
        elif menu_selected == 2:
            pass
        elif menu_selected == 3:  # Quit
            running = False

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
moving = False
animation_speed = 2
frame_counter = 0
NPC_list = []

def mob_spawn(map_offset_x, map_offset_y):
    num_slime_monsters = len(NPC_list)
    if num_slime_monsters < MOB_CAP:
        num_to_spawn = MOB_CAP - num_slime_monsters
        for _ in range(num_to_spawn):
            random_x = random.randint(6, 12)  # Adjust range as needed
            random_y = random.randint(6, 12)  # Adjust range as needed
            slime_monster = SlimeMonster(random_x, random_y)
            NPC_list.append(slime_monster)  # Add the slime monster to the list

    # Draw all the slime monsters stored in the list
    for slime_monster in NPC_list:
        # Adjust slime monster position based on map offset
        adjusted_x = slime_monster.x + map_offset_x
        adjusted_y = slime_monster.y + map_offset_y
        # Render slime monster at adjusted position
        slime_monster.draw(screen, adjusted_x, adjusted_y)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_visible = not menu_visible
            elif menu_visible:
                handle_menu_events()

    if menu_visible:
        screen.fill((0, 0, 0))
        render_menu(screen)
        pygame.display.flip()
        clock.tick(FPS)
        continue

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
        animation_speed = 1
    elif stealth and stamina >= 1:
        speed = STEALTH_SPEED
        stamina -= STEALTH_DECREASE_RATE
        STAMINA_MAX += STAMINA_GAIN
        animation_speed = 3
    else:
        speed = NORMAL_SPEED
        sprinting = False
        stealth = False
        animation_speed = 2

    # Regenerate stamina when not sprinting
    if not sprinting and stamina < STAMINA_MAX:
        stamina += STAMINA_REGEN_RATE

    if not keys[SPRINT_KEY]:
        sprinting = False
    if not keys[STEALTH_KEY]:
        stealth = False

    PLAYER_SPEED = speed

    # Attempt to move right
    if keys[pygame.K_d]:
        if not moving:
            current_direction = "right"
            moving = True
        if current_direction == "right":
            if frame_counter >= animation_speed:
                current_frame = (current_frame + 1) % 8
                frame_counter = 0
            else:
                frame_counter += 1
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(PLAYER_SPEED, 0)
        potential_secondary_hitbox = secondary_hitbox.move(PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox
    else:
        if current_direction == "right":
            moving = False

    # Attempt to move left
    if keys[pygame.K_a]:
        if not moving:
            current_direction = "left"
            moving = True
        if current_direction == "left":
            if frame_counter >= animation_speed:
                current_frame = (current_frame + 1) % 8
                frame_counter = 0
            else:
                frame_counter += 1
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(-PLAYER_SPEED, 0)
        potential_hitbox = player_hitbox.move(-PLAYER_SPEED, 0)
        potential_secondary_hitbox = secondary_hitbox.move(-PLAYER_SPEED, 0)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox
    else:
        if current_direction == "left":
            moving = False

    # Attempt to move up
    if keys[pygame.K_w]:
        if not moving:
            current_direction = "up"
            moving = True
        if current_direction == "up":
            if frame_counter >= animation_speed:
                current_frame = (current_frame + 1) % 8
                frame_counter = 0
            else:
                frame_counter += 1
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, -PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, -PLAYER_SPEED)
        potential_secondary_hitbox = secondary_hitbox.move(0, -PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox
    else:
        if current_direction == "up":
            moving = False
    
    # Attempt to move down
    if keys[pygame.K_s]:
        if not moving:
            current_direction = "down"
            moving = True
        if current_direction == "down":
            if frame_counter >= animation_speed:
                current_frame = (current_frame + 1) % 8
                frame_counter = 0
            else:
                frame_counter += 1
        # Calculate the potential position after movement
        potential_player_rect = player_rect.move(0, PLAYER_SPEED)
        potential_hitbox = player_hitbox.move(0, PLAYER_SPEED)
        potential_secondary_hitbox = secondary_hitbox.move(0, PLAYER_SPEED)
        
        # Check if moving into a tree
        if not is_hitbox_colliding(tmx_data, potential_hitbox):
            player_rect = potential_player_rect
            player_hitbox = potential_hitbox
            secondary_hitbox = potential_secondary_hitbox
    else:
        if current_direction == "down":
            moving = False

    if not keys[pygame.K_s] and not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_w]:
        current_frame = 0
        frame_counter = 0

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
