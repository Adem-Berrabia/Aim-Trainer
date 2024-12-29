import time
import math
import random
from collections import deque
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50
LABEL_FONT = pygame.font.SysFont("comicsans", 24)

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = (255, 0, 0)
    SECOND_COLOR = (255, 255, 255)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        self.size += self.GROWTH_RATE if self.grow else -self.GROWTH_RATE
        return self.size > 0

    def draw(self, win):
        layers = [self.COLOR, self.SECOND_COLOR, self.COLOR, self.SECOND_COLOR]
        for i, color in enumerate(layers):
            pygame.draw.circle(win, color, (self.x, self.y), int(self.size * (1 - 0.2 * i)))

    def collide(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2) <= self.size

def format_time(secs):
    milli = int((secs % 1) * 100)
    seconds = int(secs % 60)
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}:{milli:02d}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    metrics = [
        f"Time: {format_time(elapsed_time)}",
        f"Speed: {round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0} t/s",
        f"Hits: {targets_pressed}",
        f"Lives: {LIVES - misses}"
    ]
    positions = [5, 200, 450, 650]
    for text, pos in zip(metrics, positions):
        label = LABEL_FONT.render(text, 1, "black")
        win.blit(label, (pos, 5))

def end_screen(win, elapsed_time, targets_pressed, clicks):
    win.fill(BG_COLOR)
    stats = [
        f"Time: {format_time(elapsed_time)}",
        f"Speed: {round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0} t/s",
        f"Hits: {targets_pressed}",
        f"Accuracy: {round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0}%",
        "Press 'R' to Restart or 'Q' to Quit"
    ]
    for i, text in enumerate(stats):
        label = LABEL_FONT.render(text, 1, "white")
        win.blit(label, (get_middle(label), 100 + i * 100))
    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    main()
                    waiting_for_input = False
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    quit()

def get_middle(surface):
    return WIDTH // 2 - surface.get_width() // 2

def main():
    run = True
    targets = deque()
    clock = pygame.time.Clock()
    targets_pressed, clicks, misses = 0, 0, 0
    start_time = time.time()
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        elapsed_time = time.time() - start_time
        mouse_pos = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        for target in list(targets):  # Avoid modifying deque while iterating
            if not target.update():  # Remove targets that shrink below size 0
                targets.popleft()
                misses += 1
                if misses >= LIVES:
                    end_screen(WIN, elapsed_time, targets_pressed, clicks)
            elif click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)

        WIN.fill(BG_COLOR)
        for target in targets:
            target.draw(WIN)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
