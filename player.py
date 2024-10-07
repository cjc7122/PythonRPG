import pygame
import pytmx
import math
import time
from droppeditem import DroppedItem
from inventory import Inventory

class Player:
    def __init__(self, images, pant_images, attacking_images, attacking_pant_images, save_data, tmx_data, player_inventory_contents):
        # Main Character
        self.player_images = images
        self.pant_images = pant_images
        self.attacking_images = attacking_images
        self.attacking_pant_images = attacking_pant_images
        self.current_direction = "down"
        self.current_frame = 0
        self.frame_counter = 0
        self.current_frame1 = 0
        self.frame_counter1 = 0
        self.animation_speed = 2
        self.player_image = self.player_images[self.current_direction][self.current_frame]
        self.player_pant = self.pant_images[self.current_direction][self.current_frame]
        self.player_rect = self.player_image.get_rect()
        self.pant_rect = self.player_pant.get_rect()
        self.player_width, self.player_height = self.player_rect.size
        self.pant_width, self.pant_height = self.pant_rect.size

        # Hitboxes
        self.hitbox_width = 8
        self.hitbox_height = 24
        self.secondary_hitbox_width = 32
        self.secondary_hitbox_height = 48
        self.secondary_hitbox_color = (0, 0, 255)
        self.hitbox_offset_x = (self.player_width - self.hitbox_width) // 2
        self.hitbox_offset_y = self.player_height - self.hitbox_height
        self.secondary_hitbox_offset_y = self.player_height - self.secondary_hitbox_height

        self.player_hitbox = pygame.Rect(self.player_rect.x + self.hitbox_offset_x, self.player_rect.y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height)   
        self.secondary_hitbox = pygame.Rect(self.player_rect.x, self.player_rect.y + self.secondary_hitbox_offset_y, self.secondary_hitbox_width, self.secondary_hitbox_height)

        # Player Data
        self.STAMINA_MAX = save_data["STAMINA_MAX"]
        self.SPRINT_DECREASE_RATE = save_data["SPRINT_DECREASE_RATE"]
        self.STEALTH_DECREASE_RATE = save_data["STEALTH_DECREASE_RATE"]
        self.STAMINA_REGEN_RATE = save_data["STAMINA_REGEN_RATE"]
        self.GAINS = save_data["GAINS"]
        self.MIN_STAMINA = save_data["MIN_STAMINA"]
        self.HEALTH_MAX = save_data["HEALTH_MAX"]
        self.STEALTH_SPEED = save_data["STEALTH_SPEED"]
        self.NORMAL_SPEED = save_data["NORMAL_SPEED"]
        self.SPRINT_SPEED = save_data["SPRINT_SPEED"]
        self.stamina = save_data["stamina"]
        self.health = save_data["health"]
        self.attack_power = save_data["attack_power"]
        self.player_rect.x = save_data["player_x"]
        self.player_rect.y = save_data["player_y"]
        self.attack_range = 64
        self.inventory_contents = player_inventory_contents
        self.player_inventory = Inventory(len(self.inventory_contents))
        self.player_inventory.recreate_inventory(self.inventory_contents)
    
        self.SPRINT_KEY = "K_SHIFT"
        self.STEALTH_KEY = "K_CTRL"
        self.enable_sprinting = False
        self.enable_stealth = False
        self.speed = self.NORMAL_SPEED
        self.tmx_data = tmx_data
        self.moving = False
        self.attack_animation_length = 0.5  # Animation length in seconds
        self.last_attack_time = 0.0  # Timestamp of the last attack
        self.attacking = False
        self.attack_triggered = False
        self.dead = False

    # Function to check if the player's hitbox is colliding with any obstacles
    def check_collision(self, tmx_data, player_hitbox):
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

    def handle_input(self, keys, mobs):
        if self.stamina < 1:
            self.MIN_STAMINA = 30
    
        if self.stamina >= self.MIN_STAMINA:
            self.MIN_STAMINA = 1

        # Detect sprint key press
        if keys[self.SPRINT_KEY] and self.stamina >= self.MIN_STAMINA:
            self.enable_sprinting = True

        # Detect stealth key press
        if keys[self.STEALTH_KEY] and self.stamina >= self.MIN_STAMINA:
            self.enable_stealth = True

        if not keys[self.STEALTH_KEY]:
            self.enable_stealth = False
        if not keys[self.SPRINT_KEY]:
            self.enable_sprinting = False

        # Determine player speed and stamina consumption
        if self.enable_sprinting and self.stamina >= 1:
            self.speed = self.SPRINT_SPEED
            self.stamina -= self.SPRINT_DECREASE_RATE
            self.STAMINA_MAX += self.GAINS
            self.animation_speed = 1
        elif self.enable_stealth and self.stamina >= 1:
            self.speed = self.STEALTH_SPEED
            self.stamina -= self.STEALTH_DECREASE_RATE
            self.STAMINA_MAX += self.GAINS
            self.animation_speed = 3
        else:
            self.speed = self.NORMAL_SPEED
            self.enable_stealth = False
            self.enable_sprinting = False
            self.animation_speed = 2

        # Regenerate stamina when not sprinting
        if not self.enable_sprinting and not self.enable_stealth and self.stamina < self.STAMINA_MAX:
            self.stamina += self.STAMINA_REGEN_RATE

        if (keys["K_d"] or keys["K_a"]) and (keys["K_w"] or keys["K_s"]):
            self.speed = self.speed / 1.4

        # Check movement keys and update player position
        if keys["K_d"]:
            if not self.moving:
                self.current_direction = "right"
                self.moving = True
            if self.current_direction == "right":
                if self.frame_counter >= self.animation_speed:
                    self.current_frame = (self.current_frame + 1) % 8
                    self.frame_counter = 0
                else:
                    self.frame_counter += 1
            # Calculate the potential position after movement
            potential_player = self.player_rect.move(self.speed, 0)
            potential_hitbox = self.player_hitbox.move(self.speed, 0)
            potential_secondary_hitbox = self.secondary_hitbox.move(self.speed, 0)
            
            # Check if moving into a tree
            if not self.check_collision(self.tmx_data, potential_hitbox):
                self.player_rect = potential_player
                self.player_hitbox = potential_hitbox
                self.secondary_hitbox = potential_secondary_hitbox
        else:
            if self.current_direction == "right":
                self.moving = False

        if keys["K_a"]:
            if not self.moving:
                self.current_direction = "left"
                self.moving = True
            if self.current_direction == "left":
                if self.frame_counter >= self.animation_speed:
                    self.current_frame = (self.current_frame + 1) % 8
                    self.frame_counter = 0
                else:
                    self.frame_counter += 1
            # Calculate the potential position after movement
            potential_player = self.player_rect.move(-self.speed, 0)
            potential_hitbox = self.player_hitbox.move(-self.speed, 0)
            potential_secondary_hitbox = self.secondary_hitbox.move(-self.speed, 0)
            
            # Check if moving into a tree
            if not self.check_collision(self.tmx_data, potential_hitbox):
                self.player_rect = potential_player
                self.player_hitbox = potential_hitbox
                self.secondary_hitbox = potential_secondary_hitbox
        else:
            if self.current_direction == "left":
                self.moving = False

        if keys["K_w"]:
            if not self.moving:
                self.current_direction = "up"
                self.moving = True
            if self.current_direction == "up":
                if self.frame_counter >= self.animation_speed:
                    self.current_frame = (self.current_frame + 1) % 8
                    self.frame_counter = 0
                else:
                    self.frame_counter += 1
            # Calculate the potential position after movement
            potential_player = self.player_rect.move(0, -self.speed)
            potential_hitbox = self.player_hitbox.move(0, -self.speed)
            potential_secondary_hitbox = self.secondary_hitbox.move(0, -self.speed)
            
            # Check if moving into a tree
            if not self.check_collision(self.tmx_data, potential_hitbox):
                self.player_rect = potential_player
                self.player_hitbox = potential_hitbox
                self.secondary_hitbox = potential_secondary_hitbox
        else:
            if self.current_direction == "up":
                self.moving = False

        if keys["K_s"]:
            if not self.moving:
                self.current_direction = "down"
                self.moving = True
            if self.current_direction == "down":
                if self.frame_counter >= self.animation_speed:
                    self.current_frame = (self.current_frame + 1) % 8
                    self.frame_counter = 0
                else:
                    self.frame_counter += 1
            # Calculate the potential position after movement
            potential_player = self.player_rect.move(0, self.speed)
            potential_hitbox = self.player_hitbox.move(0, self.speed)
            potential_secondary_hitbox = self.secondary_hitbox.move(0, self.speed)
            
            # Check if moving into a tree
            if not self.check_collision(self.tmx_data, potential_hitbox):
                self.player_rect = potential_player
                self.player_hitbox = potential_hitbox
                self.secondary_hitbox = potential_secondary_hitbox
        else:
            if self.current_direction == "down":
                self.moving = False

        if not keys["K_s"] and not keys["K_a"] and not keys["K_d"] and not keys["K_w"]:
            self.current_frame = 0
            self.frame_counter = 0

        if keys["K_SPACE"]:
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attack_animation_length:
                self.attacking = True
                self.last_attack_time = current_time

        if self.attacking == True:
            if self.frame_counter1 >= self.animation_speed:
                self.current_frame1 = (self.current_frame1 + 1) % 7
                self.frame_counter1 = 0
            else:
                self.frame_counter1 += 1
            if self.current_frame1 == 2 and self.attack_triggered == False:
                self.attack(mobs)
                self.attack_power += self.GAINS
                self.attack_triggered = True
            if self.current_frame1 == 6:
                self.attacking = False
                self.attack_triggered = False
                self.current_frame1 = 0
                self.frame_counter1 = 0
                    
    def attack(self, mobs):
        for mob in mobs:
            if not isinstance(mob, Player) and not isinstance(mob, DroppedItem):
                # Calculate direction to the mob
                dx = mob.rect.centerx - self.player_rect.centerx
                dy = mob.rect.centery - self.player_rect.centery

                distance_to_mob = math.sqrt(dx ** 2 + dy ** 2)

                # Calculate angle between player and mob
                angle_to_mob = math.atan2(dy, dx)
                angle_to_mob_deg = math.degrees(angle_to_mob)
                
                # Adjust angle based on player's facing direction
                if self.current_direction == "up":
                    angle_to_mob_deg -= 270
                elif self.current_direction == "down":
                    angle_to_mob_deg -= 90
                elif self.current_direction == "left":
                    angle_to_mob_deg -= 180

                angle_to_mob_deg = (angle_to_mob_deg + 360) % 360
                
                # Check if the mob is within the attack range
                if (distance_to_mob <= self.attack_range and (angle_to_mob_deg < 45 or angle_to_mob_deg > 315)):
                    # Perform attack on the mob
                    mob.take_damage(self.attack_power, self.current_direction)

    def get_player_angle_deg(self):
        # Map facing direction to angle in degrees
        if self.current_direction == "up":
            return 0
        elif self.current_direction == "down":
            return 180
        elif self.current_direction == "left":
            return 270
        elif self.current_direction == "right":
            return 90
        else:
            return 0

    def take_damage(self, attack_power):
        if self.enable_stealth == True:
            print("Blocked!")
        else:
            print("Ouch!")
            self.health -= attack_power
            if self.health <= 0:
                self.dead = True

    def render(self, screen, WIDTH, HEIGHT):
        player_pos_centered = (WIDTH // 2 - self.player_rect.width // 2, HEIGHT // 2 - self.player_rect.height // 2)
        hitbox_pos_centered = (player_pos_centered[0] + self.hitbox_offset_x, player_pos_centered[1] + self.hitbox_offset_y)
        secondary_hitbox_pos_centered = (player_pos_centered[0] + self.player_rect.width // 2 - self.secondary_hitbox_width // 2, player_pos_centered[1] + self.secondary_hitbox_offset_y)
        
        # Update the player's hitbox position based on its current position
        self.player_hitbox.x = self.player_rect.x + self.hitbox_offset_x
        self.player_hitbox.y = self.player_rect.y + self.hitbox_offset_y

        if self.attacking == False:
            screen.blit(self.player_images[self.current_direction][self.current_frame], player_pos_centered)
            screen.blit(self.pant_images[self.current_direction][self.current_frame], player_pos_centered)
        else:
            screen.blit(self.attacking_images[self.current_direction][self.current_frame1], player_pos_centered)
            screen.blit(self.attacking_pant_images[self.current_direction][self.current_frame1], player_pos_centered)
        
        # Draw hitbox rectangle at the center of the screen
        pygame.draw.rect(screen, (255, 0, 0), (hitbox_pos_centered[0], hitbox_pos_centered[1], self.hitbox_width, self.hitbox_height), 2)
        pygame.draw.rect(screen, self.secondary_hitbox_color, (secondary_hitbox_pos_centered[0], secondary_hitbox_pos_centered[1], self.secondary_hitbox_width, self.secondary_hitbox_height), 2)