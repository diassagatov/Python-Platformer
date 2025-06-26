import pygame

class Platform:
    def __init__(self, x, y, width=100, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        self.rect.x = self.x
        self.rect.y = self.y
        screen.draw.filled_rect(self.rect, (100, 0, 0))

    def move_left(self, speed):
        self.x -= speed
        self.rect.x = self.x
        self.rect.y = self.y

    def reset_if_offscreen(self, width):
        if self.x + self.width < 0:
            self.x = width
        self.rect.x = self.x
        self.rect.y = self.y 