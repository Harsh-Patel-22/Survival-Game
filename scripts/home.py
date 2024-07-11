from settings import *

class CustomFont(pygame.sprite.Sprite):
    def __init__(self, text, size, color, pos, groups):
        super().__init__(groups)
        font = pygame.Font(None, size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_frect(center = pos)

class Button(pygame.sprite.Sprite):
    def __init__(self, type, pos, groups):
        super().__init__(groups)
        self.type = type
        self.btn_size = pygame.Vector2(150, 50)
        self.image = pygame.Surface(self.btn_size)
        self.image.fill('orange')
        self.rect = self.image.get_frect(center = pos)