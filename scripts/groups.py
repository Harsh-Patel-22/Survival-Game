from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2 + 80)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2 + 70)
        for sprite in self:
            if(hasattr(sprite, 'ground')):
                self.display_surface.blit(sprite.image, sprite.rect.center + self.offset)
        for sprite in sorted(self, key=lambda sprite: sprite.rect.centery):
            if(not hasattr(sprite, 'ground')):
                self.display_surface.blit(sprite.image, sprite.rect.center + self.offset - pygame.Vector2(0, sprite.rect.height/5))
