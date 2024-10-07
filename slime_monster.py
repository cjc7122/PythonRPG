import pygame
import random
import pytmx
import time

class SlimeMonster:
    def __init__(self, WIDTH, HEIGHT, x, y):
        self.slime_images = {
            "up": [pygame.image.load(f"./Mob_Sprites/slime/slimeup{i}.png") for i in range(3)],
            "down": [pygame.image.load(f"./Mob_Sprites/slime/slimedown{i}.png") for i in range(3)],
            "left": [pygame.image.load(f"./Mob_Sprites/slime/slimeleft{i}.png") for i in range(3)],
            "right": [pygame.image.load(f"./Mob_Sprites/slime/slimeright{i}.png") for i in range(3)]
        }

        self.image = pygame.image.load("./Mob_Sprites/slime/slimedown0.png")
        self.current_direction = "down"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 4
        self.rect = self.image.get_rect()
        self.width, self.height = self.rect.size
        self.rect.x, self.rect.y = x, y
        self.game_WIDTH = WIDTH
        self.game_HEIGHT = HEIGHT

        self.hitbox_width = 32
        self.hitbox_height = 32
        self.hitbox_offset_x = self.width - self.hitbox_width
        self.hitbox_offset_y = self.height - self.hitbox_height

        self.slime_hitbox = pygame.Rect(self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height)   

        self.move_radius = 200
        self.attack_radius = 48
        self.target = None
        self.max_health = 100
        self.health = self.max_health
        self.dead = False
        self.attack_power = 10
        self.attack_cooldown = 5
        self.last_attack_time = 0
        self.original_location = None
        self.first = True
        self.dx = None
        self.dy = None 

        self.DROP_PROBABILITY = 1 #.2
        self.EXP_GAIN = 3
        self.dropid = 1

    def move(self, tmx_data, player):
        self.current_frame += 1

        player_x = player.player_hitbox.centerx
        player_y = player.player_hitbox.bottom

        # Calculate distance to the player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.bottom
        distance = (dx ** 2 + dy ** 2) ** 0.5

        current_time = time.time()
        
        if distance <= self.attack_radius:
            # Check if enough time has passed since last attack
            if current_time - self.last_attack_time >= self.attack_cooldown:
                # Store the original location if it's not stored yet
                if self.first == True:
                    self.original_location = self.rect.centerx, self.rect.bottom
                    self.dx, self.dy = dx, dy
                    self.first = False
                else:
                    try:
                        # Move towards the player
                        if self.dx != 0:
                            self.rect.centerx += (self.dx // abs(self.dx)) * 3
                            self.current_direction = "right" if self.dx > 0 else "left"
                        if self.dy != 0:
                            self.rect.bottom += (self.dy // abs(self.dy)) * 3
                            self.current_direction = "down" if self.dy > 0 else "up"
                        
                        # Check for collision between player's hitbox and slime's hitbox
                        if self.rect.colliderect(player.player_hitbox):
                            # Attack the player
                            self.attack(player)
                            self.last_attack_time = current_time
                            self.first = True
                            self.dx = self.original_location[0] - self.rect.centerx
                            self.dy = self.original_location[1] - self.rect.bottom
                        elif abs(self.dy) < .2 and abs(self.dx) < .2:
                            self.dx = self.original_location[0] - self.rect.centerx
                            self.dy = self.original_location[1] - self.rect.bottom
                            self.last_attack_time = current_time
                            self.first = True
                    except:
                        self.first = True
                        self.original_location = None
                        self.last_attack_time = current_time
                
            elif self.original_location != None:
                if self.dx != 0:
                    self.rect.centerx += (self.dx // abs(self.dx)) * 3
                    self.current_direction = "right" if self.dx > 0 else "left"
                if self.dy != 0:
                    self.rect.bottom += (self.dy // abs(self.dy)) * 3
                    self.current_direction = "down" if self.dy > 0 else "up" 
                if abs(self.dy) < .2 and abs(self.dx) < .2:
                    self.original_location = None
        else:
            self.original_location = None
            self.first = True
            if self.target is None:
                # If no target, move randomly within the move radius
                move_x = random.randint(self.rect.x - self.move_radius, self.rect.x + self.move_radius)
                move_y = random.randint(self.rect.y - self.move_radius, self.rect.y + self.move_radius)
                # Ensure the slime stays within the game boundaries
                move_x = max(0, min(move_x, self.game_WIDTH - self.width))
                move_y = max(0, min(move_y, self.game_HEIGHT - self.height))
                
                # Set the target position
                self.target = (move_x, move_y)
            else:                
                if distance > self.move_radius:
                    dx = self.target[0] - self.rect.centerx
                    dy = self.target[1] - self.rect.bottom
                    # Move towards the target
                    dx_sign = dx // abs(dx) if dx != 0 else 0
                    dy_sign = dy // abs(dy) if dy != 0 else 0
                    
                    # Check for collision before moving
                    new_x = self.rect.centerx + dx_sign
                    new_y = self.rect.bottom + dy_sign
                    new_hitbox = pygame.Rect(new_x + self.hitbox_offset_x, new_y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height)
                
                    if not self.check_collision(tmx_data, new_hitbox):
                        if dx != 0:
                            self.rect.centerx = new_x
                            self.current_direction = "right" if dx > 0 else "left"
                        if dy != 0:
                            self.rect.bottom = new_y
                            self.current_direction = "down" if dy > 0 else "up"

                        if self.rect.centerx == self.target[0] and self.rect.bottom == self.target[1]:
                            # Reset the target to None
                            self.target = None
                    else:
                        self.target = None
                else:
                    dx_sign = dx // abs(dx) if dx != 0 else 0
                    dy_sign = dy // abs(dy) if dy != 0 else 0

                    # Check for collision before moving
                    new_x = self.rect.centerx + dx_sign
                    new_y = self.rect.bottom + dy_sign
                    new_hitbox = pygame.Rect(new_x + self.hitbox_offset_x, new_y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height)
                
                    if not self.check_collision(tmx_data, new_hitbox):
                        # Move towards the player
                        if dx != 0:
                            self.rect.centerx += dx // abs(dx)
                            self.current_direction = "right" if dx > 0 else "left"
                        if dy != 0:
                            self.rect.bottom += dy // abs(dy)
                            self.current_direction = "down" if dy > 0 else "up"

    def check_collision(self, tmx_data, new_hitbox):
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

        # Get the tile coordinates that intersect with the new hitbox
        intersecting_tiles = []
        for y in range(int(new_hitbox.y // tmx_data.tileheight), int((new_hitbox.y + new_hitbox.height) // tmx_data.tileheight) + 1):
            for x in range(int(new_hitbox.x // tmx_data.tilewidth), int((new_hitbox.x + new_hitbox.width) // tmx_data.tilewidth) + 1):
                intersecting_tiles.append((x, y))

        # Check if any of the intersecting tiles are obstacles
        for x, y in intersecting_tiles:
            tile_gid = tmx_data.get_tile_gid(x, y, obstacle_layer_index)
            if tile_gid != 0:
                return True

        return False

    def attack(self, player):
            # Attack the player
            player.take_damage(self.attack_power)

    def take_damage(self, damage, attack_direction):
        # Reduce the health of the slime monster by the given damage amount
        print("Attack", damage)
        self.health -= damage
        if self.health <= 0:
            self.dead = True
        else:
            # Calculate the knockback distance based on the attack direction
            knockback_distance = 5  # Adjust as needed

            # Adjust the slime's position based on the attack direction
            if attack_direction == "left":
                self.rect.x -= knockback_distance
            elif attack_direction == "right":
                self.rect.x += knockback_distance
            elif attack_direction == "up":
                self.rect.y -= knockback_distance
            elif attack_direction == "down":
                self.rect.y += knockback_distance

    def render(self, screen, map_offset_x, map_offset_y):
        adjusted_x = self.rect.x + map_offset_x
        adjusted_y = self.rect.y + map_offset_y

        # Get the current frame of the animation based on the direction
        frame_index = self.current_frame // self.animation_speed
        frame_count = len(self.slime_images[self.current_direction])
        frame_index %= frame_count
        self.image = self.slime_images[self.current_direction][frame_index]

        # Draw the slime monster on the screen
        screen.blit(self.image, (adjusted_x, adjusted_y))

        # Render health bar if health is less than max health
        if self.health < self.max_health:
            # Calculate health bar dimensions
            bar_width = 32  # Adjust as needed
            bar_height = 5   # Adjust as needed
            bar_padding = 2  # Adjust as needed
            health_width = int((self.health / self.max_health) * bar_width)

            # Draw health bar background
            pygame.draw.rect(screen, (255, 0, 0), (adjusted_x, adjusted_y - bar_height - bar_padding, bar_width, bar_height))

            # Draw health bar foreground (based on current health)
            pygame.draw.rect(screen, (0, 255, 0), (adjusted_x, adjusted_y - bar_height - bar_padding, health_width, bar_height))
        
        # Draw the hitbox
        pygame.draw.rect(screen, (255, 0, 0), (adjusted_x + self.hitbox_offset_x, adjusted_y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height), 1)