from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, surfaces, pos, groups, collision_sprites):
        # connections
        self.player = player
        self.collision_sprites = collision_sprites

        # setup
        super().__init__(groups)
        self.surfaces = surfaces
        self.image = surfaces[0]
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-50, -40)

        # movement
        self.direction = pygame.Vector2()
        self.speed = 200

        # animation
        self.animation_speed = 10
        self.active_frame = 0

    def collide(self, axis):
        for sprite in self.collision_sprites:
            if self.hitbox_rect.colliderect(sprite.rect):
                if axis == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                if axis == 'vertical':
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        self.active_frame = (self.active_frame + self.animation_speed * dt) % len(self.surfaces)
        self.image = self.surfaces[int(self.active_frame)] 

    def configure_movement_direction(self):
        player_pos = pygame.Vector2(self.player.rect.center)
        own_pos = pygame.Vector2(self.rect.center)
        self.direction = player_pos - own_pos
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.configure_movement_direction()
        self.hitbox_rect.centerx += self.direction.x * self.speed * dt
        self.collide('horizontal')
        self.hitbox_rect.centery += self.direction.y * self.speed * dt
        self.collide('vertical')

        self.rect.center = self.hitbox_rect.center

    def destory(self):
        pass

    def update(self, dt):
        self.animate(dt)
        self.move(dt)


class ExplodeAnimation(pygame.sprite.Sprite):
    def __init__(self, surfaces, target, groups):
        super().__init__(groups)
        self.surfaces = surfaces
        self.target = target
        self.animation_speed = 45
        self.active_frame = 0

        self.image = self.surfaces[0]
        self.rect = self.image.get_frect(center = self.target.rect.center)

    def update(self, dt):
        self.active_frame = (self.active_frame + self.animation_speed * dt)
        if self.active_frame < len(self.surfaces):
            self.image = self.surfaces[int(self.active_frame)]
        else:
            self.kill()
