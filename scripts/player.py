from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(join('images','player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-60, -80)

        # animation
        self.states = {'down' : [],'left' : [],'up' : [], 'right' : []}
        self.active_state = 'down'
        self.animation_speed = 7
        self.active_frame = 0

        # loading animation images
        for state in self.states.keys():
            for parent_folder, sub_folders, file_names in (walk(join('images', 'player'))):
                if file_names:
                    sorted(file_names, key= lambda name: int(name.split('.')[0]))
                    for file in file_names:
                        if(file.split('.')[1] == 'png'):
                            self.states[state].append(pygame.image.load(join('images', 'player', state, file)).convert_alpha())

        # movement
        self.direction = pygame.Vector2()
        self.speed = 400

        # bar attributes
        self.shield_active = False
        self.shield_active_btn = 0
        self.all_sprites = groups
        self.health = Health(self.all_sprites, self)
        self.stamina = Stamina(self.all_sprites, self)
        self.shield = None

        # collide
        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        self.speed_boost_on_btn = keys[pygame.K_LSHIFT]
        
        single_pressed_keys = pygame.key.get_just_pressed()
        self.shield_active_btn = single_pressed_keys[pygame.K_e]

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        self.active_frame = (self.active_frame + self.animation_speed * dt) % len(self.states[self.active_state]) if self.direction else 0
        if self.direction.x != 0:
            if self.direction.x > 0: self.active_state = 'right'
            if self.direction.x < 0: self.active_state = 'left'
        if self.direction.y != 0:
            if self.direction.y > 0: self.active_state = 'down'
            if self.direction.y < 0: self.active_state = 'up'
        self.image = self.states[self.active_state][int(self.active_frame)]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)

class Health(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)

        self.player = player
        self.value = 100

        self.surfaces = []

        self.offset = pygame.Vector2(10,-80)

        for _, _, file_names in walk(join('images', 'bars', 'health')):
            for file in file_names:
                self.surfaces.append(pygame.transform.scale2x(pygame.image.load(join('images', 'bars', 'health', file)).convert_alpha()))

        self.image = self.surfaces[0]
        self.active_frame = 0
        self.max_frame_index = len(self.surfaces) - 1
        
        # self.rect = self.image.get_frect(center = (640, 360))
        self.rect = self.image.get_frect(center = self.player.rect.center)

    def update(self, dt):
        self.active_frame = int(self.max_frame_index - self.value / 25)
        self.image = self.surfaces[self.active_frame]
        self.rect.center = self.player.rect.center + self.offset

class Stamina(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)

        self.player = player
        self.value = 100

        self.surfaces = []

        self.offset = pygame.Vector2(10,-55)

        for _, _, file_names in walk(join('images', 'bars', 'health')):
            for file in file_names:
                self.surfaces.append(pygame.transform.scale2x(pygame.image.load(join('images', 'bars', 'stamina', file)).convert_alpha()))

        self.image = self.surfaces[0]
        self.active_frame = 0
        self.max_frame_index = len(self.surfaces) - 1
        
        self.rect = self.image.get_frect(center = self.player.rect.center)

        # movement -> speed boost
        self.max_stamina = 100
        self.value = 100
        self.stamina_drop_rate = 10
        self.stamina_fill_rate = 5

        self.animation_speed = 1

    def speed_control(self, dt):
        if self.player.speed_boost_on_btn:
            if self.value > 0:
                self.player.speed = 400 + self.value * 3
                self.player.animation_speed = 7 + self.value / 10
                self.value -= self.stamina_drop_rate * dt
            else:
                self.player.animation_speed = 7
                self.player.speed = 400

        else:
            self.player.animation_speed = 7
            self.player.speed = 400
            if(self.value <= self.max_stamina):
                self.value += self.stamina_fill_rate * dt
    
    def move(self):
        self.active_frame = int(self.max_frame_index - self.value / 25)

        self.image = self.surfaces[int(self.active_frame)]
        self.rect.center = self.player.rect.center + self.offset

    
    def update(self, dt):
        self.move()
        self.speed_control(dt)

class Shield(pygame.sprite.Sprite):
    def __init__(self, surf, groups, player):
        super().__init__(groups)
        self.player = player
        self.player.shield_active = True


        self.image = surf
        self.rect = self.image.get_frect(center = self.player.rect.center)

        self.duration = 1000
        self.can_take_hits = 2
        self.blast_radius = 500

        self.start_time = pygame.time.get_ticks()
        self.destroy = False
    
    def timer_tick(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration: self.destroy = True
        if self.can_take_hits <= 0: self.destroy = True

    def update(self, dt):
        self.rect.center = self.player.rect.center
        self.timer_tick()

    