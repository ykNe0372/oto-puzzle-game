import pygame

# 文字の表示
def draw_text(screen, txt, x, y, size, color):
    font = pygame.font.Font('Cica-Bold.ttf', size)
    surface = font.render(txt, True, color)
    x = x - surface.get_width()/2
    y = y - surface.get_height()/2
    screen.blit(surface, (x, y))

# 画像の読み込み
def load_img(filename, colorkey=None):
    img = pygame.image.load(filename).convert()
    if (filename != "./data/img/tiles/floor.png") or (filename != "./data/img/tiles/wall.png"):
        colorkey = (255, 255, 255)
        img.set_colorkey(colorkey, pygame.RLEACCEL)
    return img