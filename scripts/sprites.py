from settings import *
from math import atan2, degrees

class GroundSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True
        
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.distance = 100
        self.direction = pygame.Vector2(1,0)

        # general setup
        super().__init__(groups)
        self.surface = pygame.image.load(join('images', 'gun', 'gun.png')).convert_alpha()
        self.image = self.surface
        self.rect = self.image.get_frect(center = self.player.rect.center + self.direction * self.distance)
        self.groups = groups

        # reloading attributes
        self.isReloading = False
        self.reload_surfaces = []
        self.reload_start_time = -1
        self.reload_time = 900
        self.max_bullets = 6
        self.has_bullets = 6

        for parent_folder, sub_folders, file_names in walk(join('images', 'gun')):
            if(not sub_folders):
                for file in file_names:
                    self.reload_surfaces.append(pygame.image.load(join('images', 'gun', 'reload', file)).convert_alpha())
                

    def update_direction(self):
        player_pos = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.direction = (mouse_pos - player_pos).normalize() if self.direction else self.direction

    def rotate(self):
        angle = degrees(atan2(self.direction.x, self.direction.y)) - 90

        if self.direction.x > 0 :
            self.image = pygame.transform.rotozoom(self.surface, angle, 0.7)
        else:
            self.image = pygame.transform.rotozoom(self.surface, abs(angle), 0.7)
            self.image = pygame.transform.flip(self.image, False, True)

        self.rect.center = self.player.rect.center + self.direction * self.distance

    def reload(self):
        if not self.isReloading:
            keys = pygame.key.get_just_pressed()
            if self.has_bullets <= 0 or keys[pygame.K_r]:
                Reload(self.reload_surfaces, self, self.groups)
                self.isReloading = True
                self.reload_start_time = pygame.time.get_ticks()
        else:
            if(pygame.time.get_ticks() - self.reload_start_time >= self.reload_time):
                self.isReloading = False
                self.has_bullets = self.max_bullets

    def update(self, _):
        self.update_direction()
        self.rotate()
        self.reload()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        # general setup
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.scale_by(self.image, 0.5)
        
        self.rect = self.image.get_frect(center = pos)

        # move attributes
        self.direction = direction
        self.speed = 600

        # kill attributes
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1000


    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if(pygame.time.get_ticks() - self.spawn_time >= self.life_time): self.kill()

class Reload(pygame.sprite.Sprite):
    def __init__(self, surfaces, gun, groups):
        super().__init__(groups)
        self.surfaces = surfaces
        self.image = surfaces[0]
        self.rect = self.image.get_frect(center = gun.rect.center)
        self.start_time = pygame.time.get_ticks()

        self.active_frame = 0
        self.animation_speed = 5
        self.total_animation_frames = len(self.surfaces)

        self.gun = gun

    def update(self, dt):
        self.rect.center = self.gun.rect.center
        if(self.gun.direction.x < 0):
            self.rect.center += pygame.Vector2(10,0)

        if (self.active_frame < self.total_animation_frames - 1):
            self.active_frame += self.animation_speed * dt
            self.image = self.surfaces[int(self.active_frame)]
        else:
            self.image = self.surfaces[0]
            self.kill()