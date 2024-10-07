# ui_renderer.py

import pygame

class UIRenderer:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.capacity = 9
        self.slots = self.get_last_9_slots()
        self.selected_slot_index = 0
        self.menu_color = (128, 128, 128)
        self.width = 800
        self.height = 600
        self.horizontal_padding = 10
        self.vertical_padding = 10        
        self.grid_x = (self.width - (9 * self.slots[0].square_size)) // 10
        self.grid_y = (self.height - (3 * self.slots[0].square_size)) // 2
        self.item_images = {}
        self.inventory_rect = pygame.Rect(100, 50, self.width, self.height)
        self.prev_left = False
        self.prev_right = False

    def get_last_9_slots(self):
        # Assuming the last 9 slots are slots 27 to 35 (inclusive)
        return self.player.player_inventory.slots[27:36]
    
    def handle_input(self, keys):
        if keys["K_LEFT"]:
            if not self.prev_left:
                self.selected_slot_index = (self.selected_slot_index - 1) % len(self.slots)
                self.prev_left = True
        else:
            self.prev_left = False
        if keys["K_RIGHT"]:
            if not self.prev_right:
                self.selected_slot_index = (self.selected_slot_index + 1) % len(self.slots)
                self.prev_right = True
        else:
            self.prev_right = False
    def render_ui(self):
        status_bar_width = 100
        status_bar_height = 10
        status_bar_padding = 5
        health_bar_x = self.screen.get_width() - status_bar_width - status_bar_padding
        health_bar_y = status_bar_padding
        health_fill_width = (self.player.health / self.player.HEALTH_MAX) * status_bar_width
        health_bar_rect = pygame.Rect(health_bar_x, health_bar_y, health_fill_width, status_bar_height)
        health_color = (0, 255, 0) if self.player.health >= (self.player.HEALTH_MAX * 0.3) else (255, 255, 0)
        
        stamina_bar_x = self.screen.get_width() - status_bar_width - status_bar_padding
        stamina_bar_y = status_bar_padding + (health_bar_y * 2)
        stamina_fill_width = (self.player.stamina / self.player.STAMINA_MAX) * status_bar_width
        stamina_bar_rect = pygame.Rect(stamina_bar_x, stamina_bar_y, stamina_fill_width, status_bar_height)
        stamina_color = (0, 0, 225) if self.player.stamina >= (self.player.STAMINA_MAX * 0.3) else (255, 255, 0)
        
        pygame.draw.rect(self.screen, health_color, health_bar_rect)
        pygame.draw.rect(self.screen, stamina_color, stamina_bar_rect)

        # Calculate the starting position for the grid
        grid_x = 100 + self.horizontal_padding
        grid_y = 50 + self.height - self.vertical_padding - 3 * self.slots[0].square_size

        slot_rects = []
        for slot in self.slots:
            if slot.id != 0:
                item_image_path = f"./Item_Sprites/{slot.id}.png"  # Assuming item images are named by item_id
                try:
                    item_image = pygame.image.load(item_image_path).convert_alpha()
                except pygame.error as e:
                    print("Error loading image:", e)
                    item_image = None
                self.item_images[slot.slot_id] = item_image

        for row in range(1):
            for col in range(9):
                slot_index = row * 9 + col
                slot = self.slots[slot_index]
                square_x = grid_x + col * (slot.square_size + self.horizontal_padding)
                square_y = grid_y + row * (slot.square_size + self.vertical_padding) + 50
                
                # Create a rectangle for the slot
                slot_rect = pygame.Rect(square_x, square_y, slot.square_size, slot.square_size)
                slot_rects.append(slot_rect)

                pygame.draw.rect(self.screen, (255, 255, 255), slot_rect)  # Draw the rectangle for the slot

                if slot.id != 0:
                    item_image = self.item_images.get(slot.slot_id)
                    if item_image:
                        # Calculate the position to blit the image to center it in the rectangle
                        image_x = square_x + (slot.square_size - item_image.get_width()) // 2
                        image_y = square_y + (slot.square_size - item_image.get_height()) // 2
                        self.screen.blit(item_image, (image_x, image_y))

                    slot_number_font = pygame.font.Font(None, 20)  # You can adjust the font size as needed
                    slot_number_text = slot_number_font.render(str(slot.number), True, (0, 0, 0))
                    self.screen.blit(slot_number_text, (square_x + 5, square_y + 5))

                if slot_index == self.selected_slot_index:
                    # Draw a rectangle around the selected slot
                    pygame.draw.rect(self.screen, (255, 0, 0), slot_rect, 2)

        pygame.display.flip()
        return slot_rects