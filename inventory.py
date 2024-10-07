import pygame

class Slot:
    def __init__(self, slot_id):
        self.id = 0
        self.number = 0
        self.square_size = 55
        self.slot_id = slot_id
        self.item_image = None

    def set_item(self, item_id, quantity = None):
        if quantity != None:
            self.id = item_id
            self.number = quantity
        else:
            self.id = item_id
            self.number = 1

    def move_item(self, item_id, number):
        self.id = item_id
        self.number = number

    def add_item(self, number):
        self.number += number

    def remove_item(self):
        self.id = 0
        self.number = 0

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.slots = self.create_slots()
        self.menu_color = (128, 128, 128)
        self.inventory_width = 600
        self.inventory_height = 500
        self.horizontal_padding = (self.inventory_width - (9 * self.slots[0].square_size)) // 10
        self.vertical_padding = 10        
        self.grid_x = (self.inventory_width - (9 * self.slots[0].square_size)) // 10
        self.grid_y = (self.inventory_height - (3 * self.slots[0].square_size)) // 2
        self.item_images = {}
        self.inventory_rect = pygame.Rect(100, 50, self.inventory_width, self.inventory_height)

    def render_inv(self, screen):
        pygame.draw.rect(screen, self.menu_color, self.inventory_rect)

        # Calculate the starting position for the grid
        grid_x = 100 + self.horizontal_padding
        grid_y = 50 + self.inventory_height - self.vertical_padding - 3 * self.slots[0].square_size

        # List to store rectangles for each slot
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

        # Iterate over slots and render rectangles
        for row in range(4):
            for col in range(9):
                slot_index = row * 9 + col
                slot = self.slots[slot_index]
                square_x = grid_x + col * (slot.square_size + self.horizontal_padding)
                square_y = grid_y + row * (slot.square_size + self.vertical_padding) - 90
                
                # Create a rectangle for the slot
                slot_rect = pygame.Rect(square_x, square_y, slot.square_size, slot.square_size)
                slot_rects.append(slot_rect)

                pygame.draw.rect(screen, (255, 255, 255), slot_rect)  # Draw the rectangle for the slot

                if slot.id != 0:
                    item_image = self.item_images.get(slot.slot_id)
                    if item_image:
                        # Calculate the position to blit the image to center it in the rectangle
                        image_x = square_x + (slot.square_size - item_image.get_width()) // 2
                        image_y = square_y + (slot.square_size - item_image.get_height()) // 2
                        screen.blit(item_image, (image_x, image_y))

                    slot_number_font = pygame.font.Font(None, 20)  # You can adjust the font size as needed
                    slot_number_text = slot_number_font.render(str(slot.number), True, (0, 0, 0))
                    screen.blit(slot_number_text, (square_x + 5, square_y + 5))
        
        pygame.display.flip()
        return slot_rects  # Return the list of slot rectangles

    def create_slots(self):
        slots = []
        for i in range(self.capacity):
            slot = Slot(i)  # Assuming you have a Slot class defined
            slots.append(slot)
        return slots
    
    def add_item(self, item_id, quantity = None, slot_index = None):
        if slot_index is not None:  # If slot index is provided, add the item to that specific slot
            self.slots[slot_index].set_item(item_id, quantity)
        else:
            for slot in self.slots:
                if slot.id == item_id:
                    slot.add_item(1)
                    return
            # If item not found in inventory, find an empty slot to add the item
            for slot in self.slots:
                if slot.id == 0:
                    slot.set_item(item_id)
                    return
            
    def recreate_inventory(self, inventory_data):
        for slot_index, (item_id, quantity) in enumerate(inventory_data):
            self.add_item(item_id, quantity, slot_index)

    def remove_item(self, item_id):
        for slot in self.slots:
            if slot.id == item_id:
                slot.remove_item(item_id)
                return

    def get_contents(self):
        return [(slot.id, slot.number) for slot in self.slots]
    
    def get_slot_number(self, x, y):
        grid_x = 100 + self.horizontal_padding
        grid_y = 100 + self.inventory_height - self.vertical_padding - 3 * self.slots[0].square_size - 90

        col = (x - grid_x) // (self.slots[0].square_size + self.horizontal_padding)
        row = (y - grid_y) // (self.slots[0].square_size + self.vertical_padding)

        if (x >= grid_x and x <= grid_x + 9 * (self.slots[0].square_size + self.horizontal_padding) and
            y >= grid_y and y <= grid_y + 4 * (self.slots[0].square_size + self.vertical_padding)):

            return int(row * 9 + col)
        else:
            return -1