import pygame
import pytmx
import sys, json
import random, time
from player import Player
from ui_renderer import UIRenderer
from slime_monster import SlimeMonster
from inventory import Inventory
import asyncio

###TODO###

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 16
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAX_MOBS = 10 
mobs = 0
action = None

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyRPG")

# Load Tiled map
tmx_data = pytmx.load_pygame("Map1.tmx")  # Change "example.tmx" to your tiled map file

def load_game(selected_save):
    global save_file_path 
    save_file_path = f"saves/{selected_save}"

    # Implement functionality to load the game using the selected save file
    with open(save_file_path, "r") as f:
            global save_data
            save_data = json.load(f)
            # Extract data from the save file
            global STAMINA_MAX, SPRINT_DECREASE_RATE, STEALTH_DECREASE_RATE, STAMINA_REGEN_RATE, GAINS, player_inventory
            global MIN_STAMINA, HEALTH_MAX, STEALTH_SPEED, NORMAL_SPEED, SPRINT_SPEED, stamina, health, attack_power
            STAMINA_MAX = save_data["STAMINA_MAX"]
            SPRINT_DECREASE_RATE = save_data["SPRINT_DECREASE_RATE"]
            STEALTH_DECREASE_RATE = save_data["STEALTH_DECREASE_RATE"]
            STAMINA_REGEN_RATE = save_data["STAMINA_REGEN_RATE"]
            GAINS = save_data["GAINS"]
            MIN_STAMINA = save_data["MIN_STAMINA"]
            HEALTH_MAX = save_data["HEALTH_MAX"]
            STEALTH_SPEED = save_data["STEALTH_SPEED"]
            NORMAL_SPEED = save_data["NORMAL_SPEED"]
            SPRINT_SPEED = save_data["SPRINT_SPEED"]
            stamina = save_data["stamina"]
            health = save_data["health"]
            attack_power = save_data["attack_power"]
            player_inventory = save_data["inventory"]

    reconstructed_inventory_data = json.loads(player_inventory)
    player_inventory = Inventory.from_dict(reconstructed_inventory_data)

async def save_game():  
    try:
        inventory_data = player_inventory.to_dict()
        inventory_json = json.dumps(inventory_data)
        save_data = {
            "STAMINA_MAX": STAMINA_MAX,
            "SPRINT_DECREASE_RATE": SPRINT_DECREASE_RATE,
            "STEALTH_DECREASE_RATE": STEALTH_DECREASE_RATE,
            "STAMINA_REGEN_RATE": STAMINA_REGEN_RATE,
            "GAINS": GAINS,
            "MIN_STAMINA": MIN_STAMINA,
            "HEALTH_MAX": HEALTH_MAX,
            "STEALTH_SPEED": STEALTH_SPEED,
            "NORMAL_SPEED": NORMAL_SPEED,
            "SPRINT_SPEED": SPRINT_SPEED,
            "stamina": stamina,
            "health": health,
            "attack_power": attack_power,
            "inventory": inventory_json
        }

        with open(save_file_path, "w") as f:
            json.dump(save_data, f, indent=4)
    except:
        print(f"Error saving game.")

# Check if a save file name is provided as a command-line argument
selected_save = sys.argv[1]
load_game(selected_save)  # Call the load_game function with the selected save file name

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

attacking_images = {
    "up": [pygame.image.load(f"./Player_Sprites/Slashup{i}.png") for i in range(7)],
    "down": [pygame.image.load(f"./Player_Sprites/Slashdown{i}.png") for i in range(7)],
    "left": [pygame.image.load(f"./Player_Sprites/Slashleft{i}.png") for i in range(7)],
    "right": [pygame.image.load(f"./Player_Sprites/Slashright{i}.png") for i in range(7)]
}

attacking_pant_images = {
    "up": [pygame.image.load(f"./Player_Sprites/PantAtkU{i}.png") for i in range(7)],
    "down": [pygame.image.load(f"./Player_Sprites/PantAtkD{i}.png") for i in range(7)],
    "left": [pygame.image.load(f"./Player_Sprites/PantAtkL{i}.png") for i in range(7)],
    "right": [pygame.image.load(f"./Player_Sprites/PantAtkR{i}.png") for i in range(7)]
}

WORLD_list = []
player = Player(300, 300, player_images, pant_images, attacking_images, attacking_pant_images, save_data, tmx_data, player_inventory)
WORLD_list.append(player)
ui_renderer = UIRenderer(screen, player)

def render_map_centered(screen, tmx_data, player):
    # Calculate the offset to keep the player centered
    map_offset_x = WIDTH // 2 - player.player_rect.centerx
    map_offset_y = HEIGHT // 2 - player.player_rect.centery

    # Adjust the offset to handle scrolling when the player reaches the edge of the screen
    if player.player_rect.left < WIDTH // 4:
        map_offset_x += player.speed  # Scroll right
    elif player.player_rect.right > WIDTH * 3 // 4:
        map_offset_x -= player.speed  # Scroll left
    if player.player_rect.top < HEIGHT // 4:
        map_offset_y += player.speed  # Scroll down
    elif player.player_rect.bottom > HEIGHT * 3 // 4:
        map_offset_y -= player.speed  # Scroll up

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

    # Sort the WORLD_list by Y value
    WORLD_list.sort(key=lambda obj: obj.rect.bottom if isinstance(obj, SlimeMonster) else obj.player_rect.bottom)
    
    # Render all game objects from the WORLD_list
    for world_obj in WORLD_list:
        if isinstance(world_obj, Player):
            world_obj.render(screen, WIDTH, HEIGHT)
        elif isinstance(world_obj, SlimeMonster):
            world_obj.move(tmx_data, player)
            world_obj.render(screen, map_offset_x, map_offset_y)

    # Render the "ground" layer and other relevant layers
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Trees":
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, ((x * tmx_data.tilewidth) + map_offset_x, (y * tmx_data.tileheight) + map_offset_y))
                    
    ui_renderer.render_ui()

# Escape Menu #
global menu_selected, menu_visible, running
FONT_SIZE = pygame.font.Font(None, 36)
menu_items = ["Resume", "Save", "Options", "Quit"]
menu_selected = 0
menu_visible = False
inventory_visible = False

def render_menu(screen):
    menu_surface = pygame.Surface((200, len(menu_items) * 40))
    menu_surface.fill((50, 50, 50))
    for i, item in enumerate(menu_items):
        color = (255, 255, 255) if i != menu_selected else (255, 0, 0)
        text = FONT_SIZE.render(item, True, color)
        menu_surface.blit(text, (20, 40 * i))
    screen.blit(menu_surface, (screen.get_width() // 2 - 100, screen.get_height() // 2 - len(menu_items) * 20))

async def handle_menu_events(keys):
    global menu_selected, menu_visible, running
    if keys[pygame.K_UP]:
        menu_selected = (menu_selected - 1) % len(menu_items)
    elif keys[pygame.K_DOWN]:
        menu_selected = (menu_selected + 1) % len(menu_items)
    elif keys[pygame.K_RETURN]:
        if menu_selected == 0:  # Resume
            menu_visible = False
        elif menu_selected == 1:  # Save
            await save_game()
        elif menu_selected == 2:
            pass
        elif menu_selected == 3:  # Quit
            running = False

def render_inventory(player):
    # Draw the grey background for the inventory
    menu_color = (128, 128, 128)  # Grey color for the menu background
    inventory_width = 600  # Adjust as needed
    inventory_height = 400  # Adjust as needed
    inventory_x = (WIDTH - inventory_width) // 2
    inventory_y = (HEIGHT - inventory_height) // 2
    inventory_rect = pygame.Rect(inventory_x, inventory_y, inventory_width, inventory_height)
    pygame.draw.rect(screen, menu_color, inventory_rect)

    # Render inventory contents
    inventory_contents = player.inventory.get_contents()
    for i, item in enumerate(inventory_contents):
        text_surface = FONT_SIZE.render(f"{i + 1}. {item}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (inventory_x + 10, inventory_y + 10 + i * 18)  # Adjust position as needed
        screen.blit(text_surface, text_rect)
    pygame.display.flip()


def spawn_something():
    random_x = random.randint(300, 1200)  # Adjust range as needed
    random_y = random.randint(300, 1200)  # Adjust range as needed
    slime_monster = SlimeMonster(WIDTH, HEIGHT, random_x, random_y)
    WORLD_list.append(slime_monster)

# Game loop
running = True
clock = pygame.time.Clock()
last_save_time = time.time()

async def main(inventory_visible, mobs, WORLD_list, last_save_time, player):
    global menu_selected, menu_visible, running
    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_visible = not menu_visible
                elif menu_visible:   
                    keys = pygame.key.get_pressed()
                    await handle_menu_events(keys)
                elif event.key == pygame.K_e:
                    inventory_visible = not inventory_visible

        if menu_visible:
            screen.fill((0, 0, 0))
            render_menu(screen)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        elif inventory_visible:
            render_inventory(player)
            continue

        # Handling player movement
        keys = pygame.key.get_pressed()

        # Handle player input
        player.handle_input(keys, WORLD_list)

        if mobs < MAX_MOBS:
            random_number = random.randint(0, 99)

            if random_number < 2:
                spawn_something()
                mobs += 1

        for obj in WORLD_list[:]:
            if obj.dead == True:
                if obj != player:
                    mobs-= 1
                    player_inventory.add_item(1, 1)
                    WORLD_list.remove(obj)
                else:
                    #gameover()
                    player.health = player.HEALTH_MAX
                    player.dead = False
            
        # Rendering the map
        screen.fill(BLACK)
        render_map_centered(screen, tmx_data, player)

        # Update the screen
        pygame.display.flip()

        # Check if it's time to save the game
        if current_time - last_save_time >= 15:
            await save_game() 
            last_save_time = current_time

        await asyncio.sleep(0)

        clock.tick(FPS)

asyncio.run(main(inventory_visible, mobs, WORLD_list, last_save_time, player))

# Quit Pygame
pygame.quit()
