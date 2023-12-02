import pygame
import sys

from Scripts.utils import load_image

class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Main Menu")

        self.screen = pygame.display.set_mode((800, 430))   
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load('Assets/MainMenu_Music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.click = False
        self.right_click = False

        self.map_select = False
        self.main = ''

    def run(self):
        from game import Game
        from editor import Editor

        running = True
        while running:
            self.screen.blit(pygame.transform.scale(load_image('/BackgroundCastle.png'), self.screen.get_size()), (0,0))

            mx, my = pygame.mouse.get_pos()

            if self.map_select:
                map_1 = pygame.Rect(40, 60, 80, 80)
                map_2 = pygame.Rect(140, 60, 80, 80)
                
                pygame.draw.rect(self.screen, (255, 0, 0), map_1)
                pygame.draw.rect(self.screen, (255, 0, 0), map_2)

            else:
                game_button = pygame.Rect(self.screen.get_width() // 2 - 50, self.screen.get_height() // 2 + 54, 100, 100)
                editor_button = pygame.Rect(self.screen.get_width() // 2 - 150, self.screen.get_height() // 2 + 65, 80, 80)
                button_3 = pygame.Rect(self.screen.get_width() // 2 + 68, self.screen.get_height() // 2 + 65, 80, 80)

                pygame.draw.rect(self.screen, (255, 255, 255), game_button)
                pygame.draw.rect(self.screen, (255, 0, 0), editor_button)
                pygame.draw.rect(self.screen, (255, 0, 0), button_3)

            if self.click:
                if self.map_select:
                    maps = [
                        (map_1, 'world1'),
                        (map_2, 'world2')
                    ]

                    for map_rect, map_name in maps:
                        if map_rect.collidepoint(mx, my):
                            if self.main == 'game':
                                Game(map_name).run()
                            if self.main == 'editor':
                                Editor(map_name).run()
                else:
                    buttons = [
                        (game_button, 'game'),
                        (editor_button, 'editor'),
                        (button_3, 'online'),
                        #(button_4, 'settings'),
                        #(button_5, 'character')
                    ]

                    for button, action in buttons:
                        if button.collidepoint(mx, my):
                            if action in ('game', 'editor'):
                                self.map_select = True
                            if action == 'online':
                                print("Ini Game Multiplayer")
                            self.main = action

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.map_select:
                            running = False
                        else:
                             self.map_select = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click = False

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MainMenu()
    game.run()
