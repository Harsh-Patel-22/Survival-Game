from settings import *
from player import *
from enemy import *
from sprites import * 
from groups import * 
from home import *
from random import randint, choice
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Survival Game')

        self.welcomeScreen()

        self.running = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        

        # gun properties
        self.shoot_btn = False
        self.can_shoot = True
        self.shot_time = 0
        self.cooldown_time = 200

        # enemy properties
        self.enemy_spawn_rate = 2000

        self.player_can_get_hit = True
        self.player_hit_time = 0
        self.player_hit_cooldown = 1000

        self.load_images()
        self.load_sounds()
        self.setup()
        
    def welcomeScreen(self):
        # imports and required setup
        playerimage = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        playerimage = pygame.transform.scale_by(playerimage, 3)
        playerrect = playerimage.get_frect(center=(WINDOW_WIDTH * 0.8, WINDOW_HEIGHT/2 + 50))

        button_sprites = pygame.sprite.Group()
        all_home_sprites = pygame.sprite.Group() 
        
        btn_distance = 100
        
        CustomFont(text = 'Survival game', 
                   size = 80, 
                   color = 'white', 
                   pos = (WINDOW_WIDTH * 0.3, 150), 
                   groups = all_home_sprites)

        playbtn = Button(type='play', pos=(WINDOW_WIDTH * 0.3, WINDOW_HEIGHT/3 + btn_distance), groups=(all_home_sprites, button_sprites))
        exitbtn = Button(type='exit', pos=(WINDOW_WIDTH * 0.3, WINDOW_HEIGHT/3 + 2*btn_distance), groups=(all_home_sprites, button_sprites))

        CustomFont(text='Play',
                   size= 40,
                   color='blue',
                   pos = playbtn.rect.center,
                   groups=all_home_sprites)

        CustomFont(text='Exit',
                   size= 40,
                   color='blue',
                   pos = exitbtn.rect.center,
                   groups=all_home_sprites)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
            if(pygame.mouse.get_pressed()[0]):
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                for btn in button_sprites:
                    if mouse_pos.x > btn.rect.left and mouse_pos.x < btn.rect.right and mouse_pos.y > btn.rect.top and mouse_pos.y < btn.rect.bottom:
                        if btn.type == 'play':
                            return
                        else:
                            pygame.quit()
                            sys.exit()

            # draw
            self.display_surface.fill('black')
            all_home_sprites.draw(self.display_surface)
            self.display_surface.blit(playerimage, playerrect)

            # render     
            pygame.display.update()   
        
    def pause_window(self):
        print()
        while True:

            keys = pygame.key.get_just_pressed()
            if(keys[pygame.K_p]): return
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.display_surface.fill('black')        
            pygame.display.update()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()
        self.shield_surf = pygame.image.load(join('images', 'shield', 'shield.png')).convert_alpha()
        # self.crosshairs_surf = pygame.image.load(join('images', 'gun', 'crosshairs.jpg')).convert_alpha()
        self.enemies_surf = {'bat': [], 'blob': [], 'skeleton': []}

        for enemy in self.enemies_surf.keys():
            for _, _, file_names in walk(join('images', 'enemies')):
                if file_names:
                    for filename in file_names:
                        self.enemies_surf[enemy].append(pygame.image.load(join('images', 'enemies', enemy, filename)).convert_alpha())

        self.blast_surfaces = []

        for parent_folder, sub_folders, file_names in walk(join('images', 'blast')):
            if file_names:
                for file in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    self.blast_surfaces.append(pygame.image.load(join('images', 'blast', file)).convert_alpha())

    def load_sounds(self):
        self.game_sounds = {}
        for parent_folder, _, file_names in walk(join('audio')):
            for file in file_names:
                name = file.split('.')[0]
                self.game_sounds[name] = pygame.mixer.Sound(join(parent_folder, file))
                self.game_sounds[name].set_volume(0.3)

        print(self.game_sounds)

    def shoot(self):
        if ((not self.gun.isReloading) and pygame.mouse.get_pressed()[0] and self.can_shoot):
            if self.gun.direction.x > 0: pos = self.gun.rect.center + self.gun.direction * 80
            else:
                pos = self.gun.rect.center + self.gun.direction
                if self.gun.direction.y != 0: pos[1] += abs(self.gun.direction.y) * 20
           
            Bullet(self.bullet_surf, pos, self.gun.direction, (self.all_sprites, self.bullet_sprites))
            self.game_sounds['shoot'].play()
            self.gun.has_bullets -= 1
            self.shot_time = pygame.time.get_ticks()
            self.can_shoot = False

    def gun_time_tick(self):
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.shot_time >= self.cooldown_time:
                self.can_shoot = True

    def player_time_tick(self):
        if pygame.time.get_ticks() - self.player_hit_time >= self.player_hit_cooldown:
            self.player_can_get_hit = True

    def create_shield(self):
        if self.player.shield_active_btn:
            self.player.shield = Shield(self.shield_surf, self.all_sprites, self.player)

    def destroy_shield(self):
        if self.player.shield.destroy:
            shield_pos = pygame.Vector2(self.player.shield.rect.center)
            for enemy in self.enemy_sprites:
                enemy_pos = pygame.Vector2(enemy.rect.center)
                print((enemy_pos - shield_pos).magnitude())
                if((enemy_pos - shield_pos).magnitude() <= self.player.shield.blast_radius):
                    enemy.kill()

            self.player.shield.kill()
            self.player.shield_active = False

    def destroy_enemy(self, enemy):
        ExplodeAnimation(self.blast_surfaces, enemy, self.all_sprites)

    def setup(self):
        self.enemies_spawn_points = []
        map = load_pygame(join('data','maps','world.tmx')) 
        for x,y,image in map.get_layer_by_name('Ground').tiles():
            GroundSprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in map.get_layer_by_name('Entities'):
            if(obj.name == 'Player'):
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            if(obj.name == 'Enemy'):
                self.enemies_spawn_points.append((obj.x,obj.y))
        
        
        self.enemy_spawn_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_spawn_event, self.enemy_spawn_rate)

    def run(self):
        self.game_sounds['music'].play(-1)
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            keys = pygame.key.get_just_pressed()
            if keys[pygame.K_SPACE]: self.pause_window()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_spawn_event:
                    pos = choice(self.enemies_spawn_points)
                    surfaces = choice(list(self.enemies_surf.values()))
                    Enemy(self.player, surfaces, pos, (self.all_sprites, self.enemy_sprites), self.collision_sprites)


            # hitting logic
            for enemy in self.enemy_sprites:
                collide = pygame.sprite.spritecollide(enemy, self.bullet_sprites, True)
                if collide:
                    enemy.kill()
                    self.game_sounds['impact'].play()
                    self.destroy_enemy(enemy)
                    # dmg logic -> UI, healthdrop, knockback
                    pass

            if self.player_can_get_hit:
                self.player_can_get_hit = False
                self.player_hit_time = pygame.time.get_ticks()
                collide = pygame.sprite.spritecollide(self.player, self.enemy_sprites, True, pygame.sprite.collide_mask)
                if(collide):
                    if(not self.player.shield_active):
                        self.player.health.value -= 25
                        if self.player.health.value <= 0:
                            self.running = False
                    else:
                        self.player.shield.can_take_hits -= 1
                        if(self.player.shield.can_take_hits <= 0): self.destroy_shield()
            
            for bullet in self.bullet_sprites:
                collide = pygame.sprite.spritecollide(bullet, self.collision_sprites, False)
                if collide:
                    bullet.kill()

            self.gun_time_tick()
            self.shoot()
            self.player_time_tick()
            self.create_shield()
            
            # update
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)

            # render
            pygame.display.update()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()