# Import file sistem
import pygame
import sys

# Import File code dari folder lain
from Scripts.utils import load_image, load_images
from Scripts.tilemaps import Tilemap

# Mengintialize kan FPS pada game
RENDER_SCLAE = 1.0
FPS = 60

'''
Fungsi program ini untuk mengedit map didalam game lalu menyimpannya

Di dalam fungsi ini terdapat
'''

class Editor:
    def __init__(self, map_path:str) -> None:

        # =============================== Set up Pygame ==========================================
        pygame.init()
        pygame.display.set_caption("Editor Ninja Game")

        # ============================ Set up tampilan layar ====================================
        self.Layar = pygame.display.set_mode((800, 430))
        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        # ==================== Pre-Load gambar yang akan di tampilkan =========================
        self.assets = {
            'decor': load_images('/tiles/decor'),
            'grass': load_images('/tiles/grass'),
            'large_decor': load_images('/tiles/large_decor'),
            'stone': load_images('/tiles/stone'),
            'spawners': load_images('/tiles/spawners')
        }

        self.tilemap = Tilemap(self, tile_size = 32)
        self.map_path = map_path

        try:
            self.tilemap.load(f'maps/{self.map_path}.json')
        except FileNotFoundError:
            pass

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.on_grid = True

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.scroll = [0, 0]

    def run(self):
        from mainMenu import MainMenu

        while True:
            # ============================= Menampilkan Background ==============================
            self.Layar.blit(pygame.transform.scale(load_image('/background.png'), self.Layar.get_size()), (0, 0))

            # ================================= Camera Settings =======================================
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # ================================= Menampilkan Item di Dalam List Tilemap =======================================
            self.tilemap.render(self.Layar, offset=render_scroll)
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            # ============== Mengambil Posisi Mouse Dan Meletak kan Objek Pada Posisi Mouse ==========================
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] / RENDER_SCLAE, mouse_pos[1] / RENDER_SCLAE)
            tile_pos = (int((mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size))

            # ============== Mengecek Input User Apakah Mau Di dalam Grid Atau DI luar Grid ==========================
            if self.on_grid:
                self.Layar.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.Layar.blit(current_tile_img, mouse_pos)

            # ========================= Meletakkan Item Dan Menghapus Item =====================================
            if self.clicking and self.on_grid:
                self.tilemap.tilemap[f"{tile_pos[0]};{tile_pos[1]}"] = {"type": self.tile_list[self.tile_group], "variant": self.tile_variant, "pos": tile_pos}
            if self.right_clicking:
                tile_Loc = f"{tile_pos[0]};{tile_pos[1]}"
                if tile_Loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_Loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_rect = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_rect.collidepoint(mouse_pos):
                        self.tilemap.offgrid_tiles.remove(tile)

            pygame.draw.rect(self.Layar, (255, 255, 255), (self.Layar.get_width() - 40, self.Layar.get_height() - 40, 40, 40))
            current_tile_img.set_alpha(1000)
            self.Layar.blit(current_tile_img, (self.Layar.get_width() - 35, self.Layar.get_height() - 35))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.on_grid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_j:
                        self.on_grid = not self.on_grid
                    if event.key == pygame.K_k:
                        self.tilemap.save(self.map_path + '.json')
                    if event.key == pygame.K_l:
                        self.tilemap.autotile()
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_ESCAPE:
                        MainMenu().run()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    try:
        map = sys.argv[1]
        Editor(map).run()
    except:
        print("Error Invalid Arguments")