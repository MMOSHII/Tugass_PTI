import pygame
import os

BASE_IMG_PATH = 'Assets/images'

def load_image(path, is2scale: bool = True):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))

    if is2scale:
        return pygame.transform.scale2x(img)
    else:
        return img

def load_images(path, is2scale: bool = True):
    images = []

    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name, is2scale))

    return images

class Animation:
    def __init__(self, images, img_dur = 5, loop = True) -> None:
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
