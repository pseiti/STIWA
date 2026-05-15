import pygame
import sys
import random
import math
import time
import threading
from queue import Queue

# Import des Hapticore-Plugins (ersetze den Pfad durch den tatsächlichen Pfad zu deinem src-Ordner)
import sys
sys.path.append('./src')  # Pfad zum src-Ordner mit dem Hapticore-Plugin
import hapticore  # Angenommen, das Plugin heißt 'hapticore.py'

# Initialisierung des Hapticore-Geräts
hapticore.initialize(port='COM4')  # Port anpassen!

# Pygame Initialisierung
pygame.init()

# Vollbildmodus aktivieren
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Reiz-Reaktionskompatibilitätsexperiment (Hapticore)")

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Zielort (Mitte des Bildschirms, schwarz)
target_pos = (WIDTH // 2, HEIGHT // 2)
target_radius = 25

# Fadenkreuz (Startposition, weiß)
cross_size = 20
cross_pos = [0, HEIGHT // 2]

# Experiment-Parameter
trials = 10
current_trial = 0
resistance_mode = None  # 'weak_to_strong' oder 'strong_to_weak'
in_experiment = False
trial_start_time = 0
movement_data = []
clock = pygame.time.Clock()

# Widerstandsfunktion (je nach Modus)
def resistance_function(distance):
    max_distance = math.dist((0, HEIGHT // 2), target_pos)
    normalized_distance = distance / max_distance

    if resistance_mode == 'weak_to_strong':
        return 0.9 - 0.8 * normalized_distance  # 0.9 → 0.1
    else:  # strong_to_weak
        return 0.1 + 0.8 * normalized_distance  # 0.1 → 0.9

# Funktion, um eine zufällige Ecke zu wählen
def get_random_corner():
    margin = 50
    if resistance_mode == 'weak_to_strong':
        far_margin = 100
        corners = [
            (far_margin, HEIGHT // 2),
            (WIDTH - far_margin, HEIGHT // 2),
        ]
    else:
        corners = [
            (margin, HEIGHT // 2),
            (WIDTH - margin, HEIGHT // 2),
        ]
    return random.choice(corners)

# Button-Klasse für das Startmenü
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Startmenü
def show_menu():
    global resistance_mode, cross_pos, current_trial, trial_start_time, in_experiment, movement_data
    menu_running = True
    weak_to_strong_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50, "Weak-to-Strong", WHITE, GRAY)
    strong_to_weak_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50, "Strong-to-Weak", WHITE, GRAY)

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                hapticore.close()  # Hapticore-Gerät schließen
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if weak_to_strong_button.is_clicked(event.pos):
                    resistance_mode = 'weak_to_strong'
                    cross_pos = list(get_random_corner())
                    current_trial = 0
                    trial_start_time = 0
                    in_experiment = False
                    movement_data = []
                    menu_running = False
                elif strong_to_weak_button.is_clicked(event.pos):
                    resistance_mode = 'strong_to_weak'
                    cross_pos = list(get_random_corner())
                    current_trial = 0
                    trial_start_time = 0
                    in_experiment = False
                    movement_data = []
                    menu_running = False

        screen.fill(BLACK)
        title = font.render("Wähle den Widerstandsmodus:", True, WHITE)
        screen.blit(title, (WIDTH // 2 - 200, HEIGHT // 2 - 120))
        weak_to_strong_button.draw(screen)
        strong_to_weak_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# Anweisungen (zweizeilig)
font = pygame.font.SysFont("Arial", 32)

# Hauptschleife
running = True
show_menu()  # Startmenü anzeigen

# Anweisungen basierend auf dem gewählten Modus
if resistance_mode == 'weak_to_strong':
    instruction_line1 = font.render("Drehe das Hapticore-Gerät, um das Fadenkreuz zum Ziel zu bewegen.", True, WHITE)
    instruction_line2 = font.render("Der Widerstand wird zum Ziel hin immer stärker.", True, WHITE)
else:
    instruction_line1 = font.render("Drehe das Hapticore-Gerät, um das Fadenkreuz zum Ziel zu bewegen.", True, WHITE)
    instruction_line2 = font.render("Der Widerstand wird zum Ziel hin immer schwächer.", True, WHITE)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if in_experiment:
                    in_experiment = False
                    pygame.event.set_grab(False)
                    show_menu()
                    if resistance_mode == 'weak_to_strong':
                        instruction_line1 = font.render("Drehe das Hapticore-Gerät, um das Fadenkreuz zum Ziel zu bewegen.", True, WHITE)
                        instruction_line2 = font.render("Der Widerstand wird zum Ziel hin immer stärker.", True, WHITE)
                    else:
                        instruction_line1 = font.render("Drehe das Hapticore-Gerät, um das Fadenkreuz zum Ziel zu bewegen.", True, WHITE)
                        instruction_line2 = font.render("Der Widerstand wird zum Ziel hin immer schwächer.", True, WHITE)
            elif not in_experiment and event.key == pygame.K_SPACE:
                in_experiment = True
                trial_start_time = time.time()
                pygame.event.set_grab(True)

    screen.fill(BLACK)

    if not in_experiment:
        screen.blit(instruction_line1, (WIDTH // 2 - 450, HEIGHT // 2 - 50))
        screen.blit(instruction_line2, (WIDTH // 2 - 400, HEIGHT // 2 + 10))
    else:
        # Zielort zeichnen (schwarz)
        pygame.draw.circle(screen, BLACK, target_pos, target_radius)

        # Hapticore-Position abrufen
        angle = hapticore.read_angle()  # Winkel abrufen (0-360°)
        device_pos_x = int((angle / 360) * WIDTH)  # Winkel auf Bildschirmbreite mappen
        device_pos = (device_pos_x, HEIGHT // 2)

        # Widerstand berechnen
        distance_to_target = math.dist(cross_pos, target_pos)
        resistance = resistance_function(distance_to_target)

        # Widerstand an das Hapticore-Gerät senden
        hapticore.set_resistance(resistance)  # Widerstandswerte 0.1-0.9 auf Gerät anwenden

        # Fadenkreuz bewegen (mit Widerstand)
        cross_pos[0] += (device_pos[0] - cross_pos[0]) * 0.4 * resistance
        cross_pos[1] = HEIGHT // 2  # y-Koordinate bleibt konstant

        # Fadenkreuz zeichnen (weiß)
        pygame.draw.line(screen, WHITE, (cross_pos[0] - cross_size, cross_pos[1]), (cross_pos[0] + cross_size, cross_pos[1]), 3)
        pygame.draw.line(screen, WHITE, (cross_pos[0], cross_pos[1] - cross_size), (cross_pos[0], cross_pos[1] + cross_size), 3)

        # Daten aufzeichnen
        movement_data.append({
            "time": time.time() - trial_start_time,
            "device_angle": angle,
            "device_x": device_pos[0],
            "device_y": device_pos[1],
            "cross_x