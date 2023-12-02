# Import file sistem
import pygame
import sys
import random
import math

# Import File code dari folder lain
from Scripts.utils import load_image, load_images, Animation
from Scripts.entities import Player, Enemy
from Scripts.tilemaps import Tilemap
from Scripts.particle import Particle
from Scripts.clouds import Clouds
from Scripts.spark import Spark

# Mengintialize kan FPS pada game
FPS = 60

class Game:
    def __init__(self, map_path:str) -> None:

        # =============================== Set up Pygame ==========================================
        pygame.init()
        pygame.display.set_caption("Ninja Game")

        # ============================ Set up tampilan layar ====================================
        self.screen = pygame.display.set_mode((800, 430))
        self.clock = pygame.time.Clock()
        self.map_path = map_path

        # ==================== Pre-Load gambar yang akan di tampilkan =========================
        self.assets = {
            'decor': load_images('/tiles/decor'),
            'grass': load_images('/tiles/grass'),
            'large_decor': load_images('/tiles/large_decor'),
            'spawners': load_images('/tiles/spawners'),
            'stone': load_images('/tiles/stone'),
            'clouds': load_images('/clouds'),
            'background': load_image('/background.png'),
            'gun': load_image('/gun.png'),
            'projectile': load_image('/projectile.png'),
            'player': load_image('/entities/player.png'),
            'icon': load_image('/Icon.png'),
            'enemy-idle': Animation(load_images('/entities/enemy/idle'), img_dur=6),
            'enemy-run': Animation(load_images('/entities/enemy/run'), img_dur=4),
            'player-idle': Animation(load_images('/entities/player/idle', is2scale=False), img_dur=6),
            'player-run': Animation(load_images('/entities/player/run', is2scale=False), img_dur=4),
            'player-jump': Animation(load_images('/entities/player/jump')),
            'player-slide': Animation(load_images('/entities/player/slide')),
            'player-wall-slide': Animation(load_images('/entities/player/wall_slide')),
            'particles-leaf': Animation(load_images('/particles/leaf'), img_dur=20, loop=False),
            'particles-particle': Animation(load_images('/particles/particle'), img_dur=6, loop=False)
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('Assets/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('Assets/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('Assets/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('Assets/sfx/shoot.wav'),
            'ambiance': pygame.mixer.Sound('Assets/sfx/ambience.wav')
        }

        self.sfx['jump'].set_volume(0.7)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['ambiance'].set_volume(0.2)

        # ========================== Menampilkan Icon Di Pojok screen ===================================
        pygame.display.set_icon(self.assets['icon'])

        pygame.mixer.music.load('Assets/Play_music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # =========================== Player Settings ========================================
        self.ammo = 30
        self.scroll = [0, 0]
        self.movement = [False, False]
        self.player = Player(self, 'player', (300, 100), (30, 30), 150, self.ammo)

        # =========================== Background Settings ====================================
        self.clouds = Clouds(self.assets['clouds'], count = 10)
        self.tilemap = Tilemap(self, tile_size = 32)
        self.camera = True

        # Load Map
        self.load_map(self.map_path)

    def load_map(self, path):
        self.tilemap.load('maps/' + path + '.json')
        self.transition = -30

        # =========================== Spawn Player Dan Enemy ====================================
        self.enemy = []
        self.projectiles_enemy = []
        self.projectiles_player = []

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemy.append(Enemy(self, spawner['pos'], (16, 30)))

        # ================================== Particle ===========================================
        self.sparks = []
        self.leaf_spawner = []
        self.particles = []

        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawner.append(pygame.Rect(16 + tree['pos'][0], 5 + tree['pos'][1], 23, 13))

        # ================================== player ===========================================
        self.dead = 0

    # =============================== Memulai Game ===========================================
    def run(self):
        from mainMenu import MainMenu

        while True:
            #self.sfx['ambiance'].play(-1)

            # Jika player mati maka akan mereset map dan player
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 20:
                    self.load_map(self.map_path)

            if len(self.enemy) == 100:
                self.transition += 1
                if self.transition > 30:
                    MainMenu().run()

            if self.transition < 0:
                self.transition += 1

            # ============================= Menampilkan Background ==============================
            self.screen.blit(pygame.transform.scale(self.assets['background'], self.screen.get_size()), (0, 0))

            # ================================= Camera Settings =======================================
            if self.camera:
                self.scroll[0] += (self.player.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 30
            else:
                if self.player.pos[0] > self.scroll[0] + 630: 
                    self.scroll[0] += self.player.rect().centerx - self.scroll[0] - 100
                elif self.player.pos[0] < self.scroll[0] + 80:
                        self.scroll[0] += self.player.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]
                if self.player.pos[1] > self.scroll[1] + 320: 
                    self.scroll[1] += self.screen.get_height() / 2
                elif self.player.pos[1] < self.scroll[1] + 50: 
                    self.scroll[1] -= self.screen.get_height() / 2

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # =============================== Menampilkan Awan Dan Evoirement ==========================
            self.clouds.update()
            self.clouds.render(self.screen, offset = render_scroll)
            self.tilemap.render(self.screen, offset = render_scroll)

            # =============================== Menampilkan Enemy Yang Ada di Map ==========================
            for enemy in self.enemy.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.screen, offset=render_scroll)
                if kill:
                    self.enemy.remove(enemy)

            # ========================================= Menampilkan Peluru =================================================
            for projectile in self.projectiles_enemy.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.screen.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                # ========================================= Ketika Peluru Hancur =================================================
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles_enemy.remove(projectile)
                    for _ in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles_enemy.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.sfx['hit'].play()
                        self.projectiles_enemy.remove(projectile)
                        self.dead += 1
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for projectile in self.projectiles_player.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.screen.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                # ========================================= Ketika Peluru Hancur =================================================
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles_player.remove(projectile)
                    for _ in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles_player.remove(projectile)

            # ================================================= Particle =====================================================
            for rect in self.leaf_spawner:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            for particle in self.particles.copy():
                destroy = particle.update()
                particle.render(self.screen, offset = render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if destroy:
                    self.particles.remove(particle)

            for spark in self.sparks.copy():
                destory = spark.update()
                spark.render(self.screen, offset=render_scroll)
                if destory:
                    self.sparks.remove(spark)

            # ============================= Menampilkan Dan Mengerakan Player =================================
            if not self.dead:
                self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * 2.5, 0))
                self.player.render(self.screen, offset = render_scroll)

            # ==================== Mengambil Input User Untuk Mengerakan Player ===========================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and not (self.movement[0] or self.movement[1]):
                        self.player.shoot()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_ESCAPE:
                        MainMenu().run()
                    if event.key == pygame.K_c:
                        self.camera = not self.camera
                    if event.key == pygame.K_q:
                        self.player.dash()
                    if event.key == pygame.K_r:
                        self.player.ammo = self.ammo

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transtion_surf = pygame.Surface(self.screen.get_size())
                pygame.draw.circle(transtion_surf, (255, 255, 255), (self.screen.get_width() // 2, self.screen.get_height() // 2), (20 - abs(self.transition)) * 16)
                transtion_surf.set_colorkey((255, 255, 255))
                self.screen.blit(transtion_surf, (0, 0))

            # =============================== Mengupdate Pygame Atau FPS ======================================
            pygame.display.update()
            self.clock.tick(FPS)

# ================== Main Function =====================
if __name__ == "__main__":
        map = sys.argv[1]
        Game(map).run()