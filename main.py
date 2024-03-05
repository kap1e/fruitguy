import random
import sys
import time
from math import sqrt

import pygame
import pygame.freetype

pygame.init()
running = True

my_font = pygame.font.SysFont('Comic Sans MS', 20)
final_font = pygame.font.SysFont('Comic Sans MS', 25)

with open('styles.txt', 'r') as file:
    data = file.read()
start_time = time.time()  # Записываем время начала игры
level = 1  # Текущий уровень сложности


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, mass, color_name, position):
        super().__init__()
        self.image = pygame.image.load(f'sprites/{color_name}.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=position)
        self.mass = mass
        self.velocity_y = gravity * mass


def update_level():
    global level, gravity
    elapsed_time = time.time() - start_time  # Вычисляем сколько времени прошло
    if elapsed_time > 5:  # Каждые 30 секунд увеличиваем уровень сложности
        level = 1 + int(elapsed_time // 30)
        gravity = 1 + (level - 1) * 0.1  # Увеличиваем гравитацию с уровнем сложности
        for ball in balls:
            ball[3] = gravity * ball[5]  # Обновляем вертикальную скорость шариков


def draw_level():
    level_text = my_font.render(f'Level: {level}', True, white)
    screen.blit(level_text, (300, 10))  # Отображаем уровень сложности в правом верхнем углу


# настройки экрана
screen_width, screen_height = 500, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('FruitGuy')

final = 0
lose = False
lost_life = False

# Цвета
black = (40, 40, 40)
white = (255, 255, 255)

colors = [
    (255, 0, 0),  # красный
    (255, 165, 0),  # кранжевый
    (255, 255, 0),  # желтый
    (0, 255, 0),  # зеленый
    (0, 0, 255),  # синий
    (75, 0, 130),  # индиго
    (238, 130, 238),  # фиолетовый
    (255, 192, 203),  # розовый
    (255, 255, 255)  # белый
]

# виды шариков (радиус, масса, цвет)
ball_types = [
    (10, 1, colors[0]),
    (20, 2, colors[1]),
    (30, 3, colors[2]),
    (40, 4, colors[3]),
    (50, 5, colors[4]),
    (60, 6, colors[5]),
    (70, 7, colors[6]),
    (80, 8, colors[7]),
    (90, 9, colors[8])
]

balls = []  # список для хранения шариков (позиция, скорость, радиус, масса, цвет)

gravity = 1  # сила гравитации
score = 0
next_ball_type = random.choice(ball_types[:3])


def show_start_screen():
    start = False
    while not start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                start = True  # Пользователь нажал клавишу или кликнул мышью, начинаем игру

        screen.fill(black)
        text = my_font.render(data, True, white)
        text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()


show_start_screen()


def show_next_ball():
    pygame.draw.circle(screen, next_ball_type[2], (50, screen_height - 50), next_ball_type[0])


# рисуем бокс
container_x, container_y, container_width, container_height = 150, 100, 300, 500
container_color = white
container_border = pygame.Rect(container_x, container_y, container_width, container_height)

"""
ball[0]: Позиция шарика по оси X (горизонтальная координата).
ball[1]: Позиция шарика по оси Y (вертикальная координата).
ball[2]: Горизонтальная скорость шарика.
ball[3]: Вертикальная скорость шарика.
ball[4]: Радиус шарика.
ball[5]: Масса шарика.
ball[6]: Цвет шарика.
"""


def handle_collisions():
    global balls, score, final  # очев
    balls_to_remove = []
    new_balls = []
    if not final:

        for i, ball1 in enumerate(balls):

            for j, ball2 in enumerate(balls[i + 1:], start=i + 1):

                # расчет результативного вектора
                dx = ball2[0] - ball1[0]
                dy = ball2[1] - ball1[1]
                #
                # if dy == 120:
                #     final = True
                #     break

                distance = sqrt(dx ** 2 + dy ** 2)

                if distance < ball1[4] + ball2[4]:
                    if ball1[4] == ball2[4] and ball1 not in balls_to_remove and ball2 not in balls_to_remove:
                        # находим следующий размер шарика
                        for size, mass, colour in ball_types:
                            if size == ball1[4]:
                                index = ball_types.index((size, mass, colour))
                                if index + 1 < len(ball_types):

                                    new_size, new_mass, new_colour = ball_types[index + 1]
                                    new_x = (ball1[0] + ball2[0]) / 2
                                    new_y = (ball1[1] + ball2[1]) / 2
                                    new_balls.append(
                                        [new_x, new_y, 0, gravity * new_mass, new_size, new_mass, new_colour])
                                    score += new_mass * 2
                                    break

                                else:
                                    final = True
                                    break

                        balls_to_remove.append(ball1)

                        balls_to_remove.append(ball2)
                    else:
                        # обрабатываем нахлёст

                        overlap = (ball1[4] + ball2[4]) - distance

                        # берем нормализированный вектор
                        nx = dx / distance
                        ny = dy / distance

                        # распределяем перекрытие между шариками в зависимости от их масс
                        total_mass = ball1[5] + ball2[5]
                        shift_ball1 = (overlap * (ball2[5] / total_mass))
                        shift_ball2 = (overlap * (ball1[5] / total_mass))

                        # откидываем шары назад
                        ball1[0] -= nx * shift_ball1
                        ball1[1] -= ny * shift_ball1
                        ball2[0] += nx * shift_ball2
                        ball2[1] += ny * shift_ball2

        # удаляем старые шарики и добавляем новые
        balls = [ball for ball in balls if ball not in balls_to_remove] + new_balls


def update_balls():
    global running, lost_life, lose
    for ball in balls:
        ball[1] += gravity  # вертикальное движение
        # ball[3] += gravity  # добавляем гравитацию

        # ограничение движения внутри контейнера
        if ball[1] + ball[2] > container_y + container_height:
            ball[1] = container_y + container_height - ball[2]

        # проверка верхней границы
        if ball[1] - ball[2] <= container_y:
            lose = True  # выводим в мэйн и останавливаем
            break

    if not final and not lose:
        for ball in balls:
            ball[0] += ball[2]  # горизонтальное движение
            ball[1] += ball[3]  # вертикальное движение

            # запрет шарикам вылетать за бокс
            if ball[0] < container_x + ball[4]:
                ball[0] = container_x + ball[4]
            elif ball[0] > container_x + container_width - ball[4]:
                ball[0] = container_x + container_width - ball[4]

            # вообще оно должно было работать по другому, но отталкивание шаров идет и на тех, которые находятся в сосуде
            # надо при оверлапе переделать
            if ball[1] < container_y + ball[4]:
                ball[1] = container_y + ball[4]
            elif ball[1] > container_y + container_height - ball[4]:
                ball[1] = container_y + container_height - ball[4]
                ball[3] = 0  # останавливаем вертикальное движение при касании дна


# text_surface = my_font.render('Some Text', False, (250, 250, 0))
# screen.blit(text_surface, (10, 10))

lives = 3  # Игрок начинает с 3 жизнями


def lose_life():
    global lives, lose, lost_life

    if lost_life:  # Если условие проигрыша активировано
        lives -= 1  # Теряем одну жизнь
        if lives == 0:  # Если жизни закончились, игра окончательно проиграна
            lose = True  # Активируем финальное состояние игры
        else:
            lost_life = False  # Сбрасываем условие проигрыша для продолжения игры


def draw_lives():
    lives_text = my_font.render(f'Lives: {lives}', True, white)
    screen.blit(lives_text, (150, 10))  # Отображаем количество жизней в левом верхнем углу


def draw_text(text):
    img = my_font.render(text, True, white)
    screen.blit(img, (10, 10))


def draw_final_text(text):
    img = final_font.render(text, True, white)
    screen.blit(img, (30, 30))

    # мэйн


while running:
    if not final and not lose:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if container_border.collidepoint(x, y):
                    # выбор случайного типа шарика из первых трёх?

                    radius, mass, color = random.choice(ball_types[:4])
                    balls.append([x, 150, 0, gravity * next_ball_type[1], next_ball_type[0], next_ball_type[1],
                                  next_ball_type[2]])  # добавляем шарик с указанным цветом
                    next_ball_type = random.choice(ball_types[:4])

        # отрисовка сосуда
        screen.fill(black)
        update_level()
        draw_lives()
        draw_level()
        lose_life()

        pygame.draw.rect(screen, container_color, container_border, 2)

        draw_text(f'Ваш счёт {score}')

        update_balls()
        handle_collisions()

        # отрисовка шариков

        for ball in balls:
            pygame.draw.circle(screen, ball[6], (int(ball[0]), int(ball[1])), ball[4])
        show_next_ball()
        pygame.display.update()
        pygame.display.flip()
        pygame.time.delay(10)

    elif final:
        screen.fill(black)
        draw_final_text(f"Вы победили! Ваш счёт: {score}")
        pygame.display.update()
        pygame.display.flip()
        pygame.time.delay(10)

    elif lose:
        screen.fill(black)
        draw_final_text(f"Вы проиграли! Ваш счёт: {score}")
        pygame.display.update()
        pygame.display.flip()
        pygame.time.delay(10)

pygame.quit()
sys.exit()
