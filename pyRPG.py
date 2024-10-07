import pygame
import pytmx
import json, os
import random, time
from player import Player
from ui_renderer import UIRenderer
from slime_monster import SlimeMonster
from droppeditem import DroppedItem            
import asyncio
from pygame.locals import *
import keyboard

class Game:
    player_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    pant_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    attacking_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    attacking_pant_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    def __init__(self, screen, selected_save, root):
        self.root = root
        self.WIDTH, self.HEIGHT = 800, 600
        self.TILE_SIZE = 16
        self.FPS = 60
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.MAX_MOBS = 10 
        self.mobs = 0
        self.screen = screen
        pygame.display.set_caption("pyRPG")
        self.tmx_data = pytmx.load_pygame("Map1.tmx") 
        self.save_file_path = None
        self.load_images()
        self.WORLD_list = []
        self.load_game(selected_save)
        self.menu_visible = False
        self.menu_selected = 0
        self.FONT_SIZE = pygame.font.Font(None, 36)
        self.menu_items = ["Resume", "Save", "Options", "Quit"]
        self.inventory_visible = False
        self.running = True
        self.clock = pygame.time.Clock()
        self.last_save_time = time.time()
        self.dragging = False
        self.drag_slot_index = -1
        self.dragged_item_image = None
        self.tempslot = None
        self.slot_rects = None
        self.keys = {}
        self.prev_up = False
        self.prev_down = False
        self.prev_enter = False
        self.prev_esc = False
        self.prev_e = False

    def load_images(self):
        # Load player images
        self.player_sprites = self.load_sprites("Player_Sprites")
        self.item_sprites = self.load_sprites("Item_Sprites")
        self.player_images["up"] = [self.player_sprites[f"Playerup{i}"] for i in range(8)]
        self.player_images["down"] = [self.player_sprites[f"Playerdown{i}"] for i in range(8)]
        self.player_images["left"] = [self.player_sprites[f"Playerleft{i}"] for i in range(8)]
        self.player_images["right"] = [self.player_sprites[f"Playerright{i}"] for i in range(8)]

        # Load pant images
        self.pant_images["up"] = [self.player_sprites[f"Pantup{i}"] for i in range(8)]
        self.pant_images["down"] = [self.player_sprites[f"Pantdown{i}"] for i in range(8)]
        self.pant_images["left"] = [self.player_sprites[f"Pantleft{i}"] for i in range(8)]
        self.pant_images["right"] = [self.player_sprites[f"Pantright{i}"] for i in range(8)]

        # Load attacking images
        self.attacking_images["up"] = [self.player_sprites[f"Slashup{i}"] for i in range(7)]
        self.attacking_images["down"] = [self.player_sprites[f"Slashdown{i}"] for i in range(7)]
        self.attacking_images["left"] = [self.player_sprites[f"Slashleft{i}"] for i in range(7)]
        self.attacking_images["right"] = [self.player_sprites[f"Slashright{i}"] for i in range(7)]

        # Load attacking pant images
        self.attacking_pant_images["up"] = [self.player_sprites[f"PantAtkU{i}"] for i in range(7)]
        self.attacking_pant_images["down"] = [self.player_sprites[f"PantAtkD{i}"] for i in range(7)]
        self.attacking_pant_images["left"] = [self.player_sprites[f"PantAtkL{i}"] for i in range(7)]
        self.attacking_pant_images["right"] = [self.player_sprites[f"PantAtkR{i}"] for i in range(7)]

    def load_game(self, selected_save):
        self.save_file_path = f"saves/{selected_save}"
        with open(self.save_file_path, "r") as f:
            save_data = json.load(f)
            self.player = Player(self.player_images, self.pant_images, self.attacking_images, self.attacking_pant_images, save_data, self.tmx_data, save_data["inventory_contents"])   
            self.WORLD_list.append(self.player)
            self.ui_renderer = UIRenderer(self.screen, self.player)

    async def save_game(self):  
        try:
            save_data = {
                "STAMINA_MAX": self.player.STAMINA_MAX,
                "SPRINT_DECREASE_RATE": self.player.SPRINT_DECREASE_RATE,
                "STEALTH_DECREASE_RATE": self.player.STEALTH_DECREASE_RATE,
                "STAMINA_REGEN_RATE": self.player.STAMINA_REGEN_RATE,
                "GAINS": self.player.GAINS,
                "MIN_STAMINA": self.player.MIN_STAMINA,
                "HEALTH_MAX": self.player.HEALTH_MAX,
                "STEALTH_SPEED": self.player.STEALTH_SPEED,
                "NORMAL_SPEED": self.player.NORMAL_SPEED,
                "SPRINT_SPEED": self.player.SPRINT_SPEED,
                "stamina": self.player.stamina, 
                "health": self.player.health,
                "attack_power": self.player.attack_power,
                "player_x": self.player.player_rect.x,
                "player_y": self.player.player_rect.y,
                "inventory_contents": self.player.player_inventory.get_contents()
            }

            with open(self.save_file_path, "w") as f:
                json.dump(save_data, f, indent=4)
        except:
            print(f"Error saving game.")

    def load_sprites(self, directory):
        sprites = {}
        for file_name in os.listdir(directory):
            if file_name.endswith(".png"):
                sprite_name = os.path.splitext(file_name)[0]
                image_path = os.path.join(directory, file_name)
                sprite_image = pygame.image.load(image_path).convert_alpha()
                sprites[sprite_name] = sprite_image
        return sprites

    def render_map_centered(self):
        map_offset_x = self.WIDTH // 2 - self.player.player_rect.centerx
        map_offset_y = self.HEIGHT // 2 - self.player.player_rect.centery

        if self.player.player_rect.left < self.WIDTH // 4:
            map_offset_x += self.player.speed  # Scroll right
        elif self.player.player_rect.right > self.WIDTH * 3 // 4:
            map_offset_x -= self.player.speed  # Scroll left
        if self.player.player_rect.top < self.HEIGHT // 4:
            map_offset_y += self.player.speed  # Scroll down
        elif self.player.player_rect.bottom > self.HEIGHT * 3 // 4:
            map_offset_y -= self.player.speed  # Scroll up

        # Render the "ground" layer
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Ground":
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen.blit(tile, ((x * self.tmx_data.tilewidth) + map_offset_x, (y * self.tmx_data.tileheight) + map_offset_y))
            elif isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Ground2":
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen.blit(tile, ((x * self.tmx_data.tilewidth) + map_offset_x, (y * self.tmx_data.tileheight) + map_offset_y))

        # Sort the WORLD_list by Y value
        self.WORLD_list.sort(key=lambda obj: obj.rect.bottom if isinstance(obj, SlimeMonster) or isinstance(obj, DroppedItem) else obj.player_rect.bottom)
        
        # Render all game objects from the WORLD_list
        for world_obj in self.WORLD_list:
            if isinstance(world_obj, Player):
                world_obj.render(self.screen, self.WIDTH, self.HEIGHT)
            elif isinstance(world_obj, SlimeMonster):
                world_obj.move(self.tmx_data, self.player)
                world_obj.render(self.screen, map_offset_x, map_offset_y)
            elif isinstance(world_obj, DroppedItem):
                world_obj.check_collision_with_player(self.player)
                world_obj.render(self.screen, map_offset_x, map_offset_y)

        # Render the "ground" layer and other relevant layers
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Trees":
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen.blit(tile, ((x * self.tmx_data.tilewidth) + map_offset_x, (y * self.tmx_data.tileheight) + map_offset_y))
                        
        self.ui_renderer.render_ui()

    def render_menu(self):
        menu_surface = pygame.Surface((200, len(self.menu_items) * 40))
        menu_surface.fill((50, 50, 50))
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 255) if i != self.menu_selected else (255, 0, 0)
            text = self.FONT_SIZE.render(item, True, color)
            menu_surface.blit(text, (20, 40 * i))
        self.screen.blit(menu_surface, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - len(self.menu_items) * 20))

    async def handle_menu_events(self):    
        if self.keys["K_UP"]:
            if not self.prev_up:
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
                self.prev_up = True
        else:
            self.prev_up = False
        if self.keys["K_DOWN"]:
            if not self.prev_down:
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
                self.prev_down = True
        else:
            self.prev_down = False
        if self.keys["K_ENTER"]:
            if not self.prev_enter:
                if self.menu_selected == 0:  # Resume
                    self.menu_visible = False
                elif self.menu_selected == 1:  # Save
                    await self.save_game()
                elif self.menu_selected == 2:
                    pass
                elif self.menu_selected == 3:  # Quit
                    self.running = False  
                self.prev_enter = True
        else:
            self.prev_enter = False

    def spawn_something(self):
        random_x = random.randint(300, 1200)  # Adjust range as needed
        random_y = random.randint(300, 1200)  # Adjust range as needed
        slime_monster = SlimeMonster(self.WIDTH, self.HEIGHT, random_x, random_y)
        self.WORLD_list.append(slime_monster)

    def drop_items_on_death(self, obj):
        # Check if the slime drops an item based on the drop probability
        if random.random() < obj.DROP_PROBABILITY:
            # Determine the quantity of the dropped item (1 to 3)
            quantity = random.randint(1, 3)
            for _ in range (quantity):
                x = obj.rect.x + random.randint(-5,5)
                y = obj.rect.y + random.randint(-5,5)
                image = self.item_sprites[f"{obj.dropid}"]
                Drop = DroppedItem(obj.dropid, image, x, y)
                self.WORLD_list.append(Drop)
        else:
            pass

    async def item_drag(self):
            if self.dragging and self.dragged_item_image:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                image_x = mouse_x - self.dragged_item_image.get_width() // 2
                image_y = mouse_y - self.dragged_item_image.get_height() // 2
                self.screen.blit(self.dragged_item_image, (image_x, image_y))
            pygame.display.update()

    async def main(self):
        while self.running:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.inventory_visible:
                            x, y = event.pos
                            # Check if the mouse click is inside a slot
                            for i, rect in enumerate(self.slot_rects):
                                if rect.collidepoint(x, y) and self.player.player_inventory.slots[i].id != 0:
                                    self.dragging = True
                                    self.drag_slot_index = i
                                    self.dragged_item_image = self.player.player_inventory.item_images.get(self.drag_slot_index)
                                    self.tempslot = (self.player.player_inventory.slots[i].id, self.player.player_inventory.slots[i].number)
                                    self.player.player_inventory.slots[i].remove_item()
                                    break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        if self.inventory_visible:
                            x, y = event.pos
                            # Check if the mouse release is inside a slot
                            for i, rect in enumerate(self.slot_rects):
                                if rect.collidepoint(x, y):
                                    # Swap items between the drag slot and the release slot
                                    self.player.player_inventory.slots[i].move_item(self.tempslot[0], self.tempslot[1])
                                    break
                            self.dragging = False
                            self.drag_slot_index = -1
                            self.dragged_item_image = None

            # Handling player movement
            if keyboard.is_pressed('w'):
                self.keys["K_w"] = True
            else:
                self.keys["K_w"] = False
            if keyboard.is_pressed('a'):
                self.keys["K_a"] = True
            else:
                self.keys["K_a"] = False
            if keyboard.is_pressed('s'):
                self.keys["K_s"] = True
            else:
                self.keys["K_s"] = False
            if keyboard.is_pressed('d'):
                self.keys["K_d"] = True
            else:
                self.keys["K_d"] = False
            if keyboard.is_pressed('e'):
                self.keys["K_e"] = True
            else:
                self.keys["K_e"] = False 
            if keyboard.is_pressed('shift'):
                self.keys["K_SHIFT"] = True
            else:
                self.keys["K_SHIFT"] = False
            if keyboard.is_pressed('ctrl'):
                self.keys["K_CTRL"] = True
            else:
                self.keys["K_CTRL"] = False
            if keyboard.is_pressed('space'):
                self.keys["K_SPACE"] = True
            else:
                self.keys["K_SPACE"] = False
            if keyboard.is_pressed('up'):
                self.keys["K_UP"] = True
            else:
                self.keys["K_UP"] = False
            if keyboard.is_pressed('down'):
                self.keys["K_DOWN"] = True
            else:
                self.keys["K_DOWN"] = False
            if keyboard.is_pressed('left'):
                self.keys["K_LEFT"] = True
            else:
                self.keys["K_LEFT"] = False
            if keyboard.is_pressed('right'):
                self.keys["K_RIGHT"] = True
            else:
                self.keys["K_RIGHT"] = False
            if keyboard.is_pressed('enter'):
                self.keys["K_ENTER"] = True
            else:
                self.keys["K_ENTER"] = False 
            if keyboard.is_pressed('esc'):
                self.keys["K_ESC"] = True
            else:
                self.keys["K_ESC"] = False 

            if self.keys["K_ESC"]:
                if not self.prev_esc:
                    self.menu_visible = not self.menu_visible
                    self.prev_esc = True
            else:
                self.prev_esc = False

            if self.menu_visible:
                await self.handle_menu_events()

            if self.keys["K_e"]:
                if not self.prev_e:
                    self.inventory_visible = not self.inventory_visible
                    self.prev_e = True
            else:
                self.prev_e = False

            if self.menu_visible:
                self.screen.fill((0, 0, 0))
                self.render_menu()
                pygame.display.flip()
                self.clock.tick(self.FPS)
                continue
            if self.inventory_visible:
                self.screen.fill((0, 0, 0))
                self.slot_rects = self.player.player_inventory.render_inv(self.screen)
                await self.item_drag()
                self.clock.tick(self.FPS)
                await asyncio.sleep(0)
                continue
            else:
                self.dragging = False
                self.drag_slot_index = -1
                self.dragged_item_image = None

            # Handle player input
            self.ui_renderer.handle_input(self.keys)
            self.player.handle_input(self.keys, self.WORLD_list)

            if self.mobs < self.MAX_MOBS:
                random_number = random.randint(0, 99)

                if random_number < 2:
                    self.spawn_something()
                    self.mobs += 1

            for obj in self.WORLD_list[:]:
                if obj.dead == True:
                    if isinstance(obj, DroppedItem):
                        self.WORLD_list.remove(obj)
                    elif obj != self.player:
                        self.mobs-= 1
                        self.drop_items_on_death(obj)
                        self.WORLD_list.remove(obj)
                    else:
                        #gameover()
                        self.player.health = self.player.HEALTH_MAX
                        self.player.dead = False
                
            # Rendering the map
            self.screen.fill(self.BLACK)
            self.render_map_centered()

            # Update the screen
            #pygame.display.flip()
            pygame.display.update()
            self.root.update()

            # Check if it's time to save the game
            if current_time - self.last_save_time >= 15:
                await self.save_game() 
                self.last_save_time = current_time

            await asyncio.sleep(0)

            self.clock.tick(self.FPS)

        # Quit Pygame
        pygame.quit()
