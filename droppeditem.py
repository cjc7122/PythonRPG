import pygame

class DroppedItem:
    def __init__(self, item_id, image, x, y):
        self.item_id = item_id
        self.image = image
        self.image = pygame.transform.scale(image, (image.get_width() // 2, image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.dead = False

    def render(self, screen, map_offset_x, map_offset_y):
        adjusted_x = self.rect.x + map_offset_x
        adjusted_y = self.rect.y + map_offset_y

        screen.blit(self.image, (adjusted_x, adjusted_y))

    def check_collision_with_player(self, player):
        if self.rect.colliderect(player.player_rect):
            player.player_inventory.add_item(self.item_id)
            self.dead = True