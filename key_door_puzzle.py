#!/usr/bin/env python3
# La línea de arriba se llama "shebang". Le dice al sistema operativo
# que este archivo debe ejecutarse con el intérprete de Python 3.
"""
Key Door Puzzle - Match keys to doors by shape.

Controls:
    Arrow keys or WASD to move the key
    Mouse to move the key (alternative)
    ESC to quit
    SPACE or ENTER to start next level / restart

Author: Orami
"""
# El bloque de arriba, entre comillas triples, es un docstring de módulo.
# Sirve como documentación del archivo completo (no se ejecuta como código).

import pygame

# Importa la librería pygame, que contiene todas las funciones para
# crear ventanas, dibujar formas, leer el teclado y el mouse, etc.
import random

# Importa el módulo random, usado para elegir formas y posiciones al azar.
import sys

# Importa el módulo sys, usado para cerrar el programa correctamente (sys.exit()).
import math

# Importa el módulo math, usado para cálculos con ángulos y raíces (la estrella y el movimiento con mouse).

# ============================================================
# CONSTANTS
# ============================================================
# Las constantes son variables que no cambian durante la ejecución.
# Por convención en Python se escriben en MAYÚSCULAS.

# Window
WINDOW_WIDTH = 800
# Ancho de la ventana del juego, en píxeles.
WINDOW_HEIGHT = 600
# Alto de la ventana del juego, en píxeles.
WINDOW_TITLE = "Key Door Puzzle"
# Texto que aparece en la barra de título de la ventana.
FPS = 60
# Cuadros por segundo (Frames Per Second) a los que correrá el juego.

# Colors
# Los colores en pygame se representan como tuplas de 3 números (R, G, B),
# cada uno entre 0 y 255 (rojo, verde y azul).
BLACK = (0, 0, 0)
# Color negro, usado como fondo de varias pantallas.
WHITE = (255, 255, 255)
# Color blanco, usado para texto y bordes de las formas.
GRAY = (100, 100, 100)
# Color gris, usado para texto secundario y puertas cerradas.
DARK_GRAY = (40, 40, 40)
# Color gris oscuro, usado dentro de las puertas ya abiertas.
GREEN = (0, 255, 0)  # Código RGB para verde
# Color verde puro. Esta es la línea que faltaba y causaba el NameError:
# se usa para dibujar el check (marca de verificación) cuando una puerta
# recién se abre.

# Shape colors
# Diccionario que asocia cada nombre de forma con su color correspondiente.
# Las llaves (keys) del diccionario son cadenas de texto (strings),
# y los valores son tuplas RGB como las definidas arriba.
COLORS = {
    "square": (50, 150, 255),  # Blue
    "triangle": (50, 200, 100),  # Green
    "circle": (220, 80, 80),  # Red
    "star": (255, 200, 50),  # Yellow
}

SHAPES = list(COLORS.keys())
# COLORS.keys() devuelve las llaves del diccionario ("square", "triangle", etc).
# list(...) las convierte en una lista de Python para poder usarlas con random.sample() y random.choice().

# Game settings
KEY_SIZE = 30
# Tamaño (en píxeles) de la llave que el jugador mueve.
DOOR_WIDTH = 60
# Ancho de cada puerta.
DOOR_HEIGHT = 90
# Alto de cada puerta.
KEY_SPEED = 5
# Velocidad de movimiento de la llave cuando se usa teclado.
INITIAL_TIME = 30
# Tiempo inicial, en segundos, para completar el primer nivel.
TIME_REDUCTION = 2
# Cantidad de segundos que se resta el límite de tiempo por cada nivel.
MIN_TIME = 10
# Tiempo mínimo permitido, para que el juego no se vuelva imposible.
INITIAL_LIVES = 3
# Cantidad de vidas con las que empieza el jugador.
DOOR_MARGIN = 40
# Espacio en píxeles entre una puerta y otra.


# ============================================================
# DRAWING FUNCTIONS
# ============================================================
# Estas funciones reciben una "surface" (superficie de dibujo de pygame)
# y dibujan una forma geométrica sobre ella.


def draw_square(surface, x, y, size, color, filled=True):
    """Draw a square shape."""
    # filled=True es un valor por defecto: si no se indica lo contrario,
    # el cuadrado se dibuja relleno.
    rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
    # pygame.Rect crea un rectángulo a partir de la esquina superior izquierda,
    # el ancho y el alto. Restamos la mitad del tamaño para que (x, y)
    # sea el CENTRO del cuadrado, no la esquina.
    # // es división entera (sin decimales), típica de Python.
    if filled:
        pygame.draw.rect(surface, color, rect)
        # Dibuja el rectángulo relleno con el color indicado.
    pygame.draw.rect(surface, WHITE, rect, 2)
    # Dibuja el borde blanco del rectángulo. El último número (2) es el
    # grosor del borde en píxeles.


def draw_triangle(surface, x, y, size, color, filled=True):
    """Draw a triangle shape."""
    points = [
        (x, y - size // 2),
        (x - size // 2, y + size // 2),
        (x + size // 2, y + size // 2),
    ]
    # Lista de 3 tuplas (x, y): son los 3 vértices del triángulo,
    # calculados a partir del centro (x, y) y el tamaño.
    if filled:
        pygame.draw.polygon(surface, color, points)
        # pygame.draw.polygon dibuja un polígono relleno usando la lista de puntos.
    pygame.draw.polygon(surface, WHITE, points, 2)
    # Dibuja solo el borde del triángulo (grosor 2).


def draw_circle(surface, x, y, size, color, filled=True):
    """Draw a circle shape."""
    radius = size // 2
    # El radio es la mitad del tamaño total.
    if filled:
        pygame.draw.circle(surface, color, (x, y), radius)
        # pygame.draw.circle recibe la superficie, el color, el centro (x, y) y el radio.
    pygame.draw.circle(surface, WHITE, (x, y), radius, 2)
    # Dibuja solo el borde del círculo.


def draw_star(surface, x, y, size, color, filled=True):
    """Draw a 5-pointed star shape."""
    points = []
    # Lista vacía donde se irán agregando los puntos de la estrella.
    for i in range(10):
        # Una estrella de 5 puntas necesita 10 vértices:
        # alternando entre puntas exteriores e interiores.
        angle = math.radians(i * 36 - 90)
        # Convierte grados a radianes, que es lo que usan las funciones
        # trigonométricas de Python (math.cos, math.sin).
        # 36 grados es 360/10 (los 10 vértices repartidos en el círculo).
        # Restamos 90 para que la primera punta apunte hacia arriba.
        radius = size // 2 if i % 2 == 0 else size // 4
        # Los vértices en posición par usan el radio grande (puntas),
        # los impares usan un radio más chico (huecos entre puntas).
        # i % 2 es el resto de la división entre 2 (par o impar).
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        # Fórmulas trigonométricas para convertir ángulo + radio en coordenadas x, y.
        points.append((px, py))
        # Agrega el punto calculado a la lista.

    if filled:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 2)


def draw_shape(surface, shape, x, y, size, color, filled=True):
    """Draw any shape by name."""
    # Esta función funciona como un "selector": según el texto que llegue
    # en shape, llama a la función de dibujo correspondiente.
    if shape == "square":
        draw_square(surface, x, y, size, color, filled)
    elif shape == "triangle":
        draw_triangle(surface, x, y, size, color, filled)
    elif shape == "circle":
        draw_circle(surface, x, y, size, color, filled)
    elif shape == "star":
        draw_star(surface, x, y, size, color, filled)


def get_shape_rect(shape, x, y, size):
    """Get collision rectangle for a shape."""
    # Para simplificar las colisiones, todas las formas usan un
    # rectángulo cuadrado como "caja de colisión", sin importar su forma real.
    return pygame.Rect(x - size // 2, y - size // 2, size, size)


# ============================================================
# KEY CLASS
# ============================================================
# En Python, "class" define un molde para crear objetos.
# Aquí, la clase Key representa la llave que mueve el jugador.


class Key:
    """Key that the player moves to match a door."""

    def __init__(self, shape, x, y):
        # __init__ es el "constructor": se ejecuta automáticamente
        # cada vez que se crea un objeto Key(...).
        # self representa al propio objeto que se está creando.
        self.shape = shape
        # Guarda la forma de la llave (por ejemplo "circle").
        self.color = COLORS[shape]
        # Busca en el diccionario COLORS el color que corresponde a esa forma.
        self.x = x
        self.y = y
        # Posición actual de la llave en pantalla.
        self.size = KEY_SIZE
        # Tamaño de la llave, tomado de la constante global.
        self.speed = KEY_SPEED
        # Velocidad de movimiento.
        self.target_door = None
        # Variable reservada para uso futuro (no se usa activamente en este juego).
        self.inserted = False
        # Indica si la llave ya fue insertada en la puerta correcta.

    def update(self, keys_pressed, mouse_pos=None):
        """Move key based on input."""
        # mouse_pos=None es un valor por defecto: si no se pasa el mouse,
        # se asume que no se está usando.
        if mouse_pos:
            # Si se recibió una posición de mouse (no es None ni (0,0) falsy)...
            # Smooth movement toward mouse
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            # Diferencia entre la posición del mouse y la posición actual de la llave.
            dist = math.sqrt(dx * dx + dy * dy)
            # Distancia entre ambos puntos (teorema de Pitágoras).
            if dist > 5:
                # Solo se mueve si la distancia es mayor a 5 píxeles,
                # para evitar que la llave "tiemble" cuando ya está muy cerca.
                self.x += (dx / dist) * self.speed * 2
                self.y += (dy / dist) * self.speed * 2
                # (dx / dist) y (dy / dist) son el "vector normalizado" (dirección),
                # que luego se multiplica por la velocidad para saber cuánto moverse.
        else:
            # Arrow/WASD movement
            # Si no hay mouse, se mueve la llave según las teclas presionadas.
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.x -= self.speed
                # keys_pressed es una lista de booleanos que indica qué teclas
                # están presionadas en este instante. pygame.K_LEFT es la flecha izquierda.
            if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.x += self.speed
            if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                self.y -= self.speed
            if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                self.y += self.speed

        # Keep within bounds
        self.x = max(self.size, min(WINDOW_WIDTH - self.size, self.x))
        self.y = max(self.size, min(WINDOW_HEIGHT - self.size, self.y))
        # Esta línea "encierra" la posición de la llave dentro de la ventana.
        # min(...) evita que se pase del borde derecho/inferior.
        # max(...) evita que se pase del borde izquierdo/superior.

    def get_rect(self):
        """Get collision rectangle."""
        return get_shape_rect(self.shape, self.x, self.y, self.size)

    def draw(self, surface):
        """Draw the key."""
        draw_shape(surface, self.shape, self.x, self.y, self.size, self.color)

        # Draw key handle (small circle at bottom)
        handle_y = self.y + self.size // 2 + 10
        # Posición vertical del "mango" de la llave, debajo de la forma principal.
        pygame.draw.circle(surface, self.color, (int(self.x), int(handle_y)), 8)
        # int(...) convierte a número entero, porque pygame.draw.circle
        # necesita coordenadas enteras, no decimales.
        pygame.draw.circle(surface, WHITE, (int(self.x), int(handle_y)), 8, 2)


# ============================================================
# DOOR CLASS
# ============================================================


class Door:
    """Door that accepts a key of matching shape."""

    def __init__(self, shape, x, y):
        self.shape = shape
        self.color = COLORS[shape]
        self.x = x
        self.y = y
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.opened = False
        # Indica si la puerta ya fue abierta.
        self.flash_timer = 0
        # Contador de cuadros que dura el "destello" verde al abrir la puerta.

    def check_collision(self, key):
        """Check if key matches this door."""
        if key.shape != self.shape:
            return False
            # Si la forma de la llave no coincide con la de la puerta,
            # no puede haber colisión válida (se corta la función acá).

        door_rect = self.get_rect()
        key_rect = key.get_rect()
        return door_rect.colliderect(key_rect)
        # colliderect() es un método de pygame.Rect que devuelve True
        # si dos rectángulos se superponen.

    def open(self):
        """Mark door as opened."""
        self.opened = True
        self.flash_timer = 30
        # Se activa el destello verde durante 30 cuadros (medio segundo a 60 FPS).

    def update(self):
        """Update door animation."""
        if self.flash_timer > 0:
            self.flash_timer -= 1
            # Cada cuadro que pasa, el contador de destello baja en 1,
            # hasta llegar a 0 y dejar de mostrar el color verde.

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(
            self.x - self.width // 2, self.y - self.height // 2, self.width, self.height
        )

    def draw(self, surface):
        """Draw the door."""
        rect = self.get_rect()

        if self.opened:
            # Open door - darker interior
            pygame.draw.rect(surface, DARK_GRAY, rect)
            pygame.draw.rect(surface, self.color, rect, 3)

            # Draw checkmark
            check_color = GREEN if self.flash_timer > 0 else self.color
            # Operador ternario de Python: si flash_timer es mayor a 0,
            # usa GREEN; si no, usa el color normal de la puerta.
            # Esta es la línea que fallaba antes por falta de la constante GREEN.
            pygame.draw.line(
                surface,
                check_color,
                (self.x - 15, self.y),
                (self.x - 5, self.y + 10),
                3,
            )
            pygame.draw.line(
                surface,
                check_color,
                (self.x - 5, self.y + 10),
                (self.x + 15, self.y - 10),
                3,
            )
            # Dos líneas que juntas forman una marca de verificación (check).
        else:
            # Closed door
            pygame.draw.rect(surface, GRAY, rect)
            pygame.draw.rect(surface, self.color, rect, 3)

            # Draw keyhole shape
            draw_shape(surface, self.shape, self.x, self.y, 25, self.color, False)
            # filled=False: solo se dibuja el contorno de la forma,
            # simulando el "ojo de la cerradura".

            # Draw handle
            handle_x = self.x + self.width // 2 - 10
            pygame.draw.circle(surface, self.color, (handle_x, self.y), 5)


# ============================================================
# LEVEL CLASS
# ============================================================


class Level:
    """A single game level with doors and a key."""

    def __init__(self, level_number):
        self.level_number = level_number
        self.doors = []
        # Lista vacía que va a contener los objetos Door del nivel.
        self.key = None
        # Se asignará más abajo, dentro de setup_level().
        self.completed = False
        self.time_limit = max(MIN_TIME, INITIAL_TIME - level_number * TIME_REDUCTION)
        # El límite de tiempo baja con cada nivel, pero nunca por debajo de MIN_TIME.
        self.timer = self.time_limit
        self.setup_level()
        # Llama al método que arma las puertas y la llave del nivel.

    def setup_level(self):
        """Create doors and key for this level."""
        # Number of doors increases with level
        num_doors = min(4, 2 + self.level_number // 2)
        # A partir del nivel 1, el número de puertas empieza en 2 y sube,
        # pero nunca pasa de 4.

        # Randomly select shapes for doors
        door_shapes = random.sample(SHAPES, num_doors)
        # random.sample elige "num_doors" formas distintas (sin repetir)
        # de la lista SHAPES.

        # Calculate door positions (spread across the top)
        total_width = num_doors * (DOOR_WIDTH + DOOR_MARGIN) - DOOR_MARGIN
        # Ancho total que ocupan todas las puertas juntas, con sus márgenes.
        start_x = (WINDOW_WIDTH - total_width) // 2 + DOOR_WIDTH // 2
        # Posición X inicial para que el grupo de puertas quede centrado.

        for i, shape in enumerate(door_shapes):
            # enumerate() devuelve el índice (i) y el valor (shape) de cada
            # elemento de la lista, al mismo tiempo.
            x = start_x + i * (DOOR_WIDTH + DOOR_MARGIN)
            y = 100
            self.doors.append(Door(shape, x, y))
            # Crea una nueva puerta y la agrega a la lista self.doors.

        # Create key (must match one of the doors)
        key_shape = random.choice(door_shapes)
        # random.choice elige un elemento al azar de la lista.
        key_x = WINDOW_WIDTH // 2
        key_y = WINDOW_HEIGHT - 100
        self.key = Key(key_shape, key_x, key_y)

    def update(self):
        """Update level state."""
        self.timer -= 1 / FPS
        # Resta el tiempo transcurrido en un cuadro (1 dividido entre los FPS).

        for door in self.doors:
            door.update()
            # Actualiza la animación de destello de cada puerta.

        # Check if key reached correct door
        for door in self.doors:
            if not door.opened and door.check_collision(self.key):
                door.open()
                self.key.inserted = True
                self.completed = True
                return True
                # return corta la función inmediatamente y devuelve True,
                # indicando que el nivel se completó.

        # Check time out
        if self.timer <= 0:
            return False
            # Devuelve False si se acabó el tiempo.

        return None
        # Si no pasó nada especial todavía, devuelve None (ni ganó ni perdió).

    def draw(self, surface):
        """Draw the level."""
        # Draw doors
        for door in self.doors:
            door.draw(surface)

        # Draw key
        if not self.key.inserted:
            self.key.draw(surface)
            # Solo se dibuja la llave si todavía no fue insertada en una puerta.


# ============================================================
# GAME CLASS
# ============================================================


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        # Inicializa todos los módulos internos de pygame (video, audio, fuentes, etc).
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Crea la ventana del juego con el ancho y alto definidos.
        pygame.display.set_caption(WINDOW_TITLE)
        # Pone el título en la barra de la ventana.
        self.clock = pygame.time.Clock()
        # Objeto que controla la velocidad del bucle principal (los FPS).

        # Fonts (using Font instead of SysFont for Python 3.14 compatibility)
        self.font_large = pygame.font.Font(None, 48)
        # pygame.font.Font(None, tamaño) crea una fuente usando la fuente
        # por defecto de pygame (None), en vez de una fuente instalada
        # en el sistema. Esto evita el error de SysFont que tuviste antes.
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)

        self.state = "menu"  # menu, playing, level_complete, game_over, win
        # Variable que controla en qué pantalla está el juego.
        self.level_number = 0
        self.lives = INITIAL_LIVES
        self.score = 0
        self.high_score = 0
        self.level = None
        self.running = True
        # Mientras sea True, el bucle principal del juego sigue corriendo.
        self.use_mouse = True
        # Indica si se está usando el mouse o el teclado para mover la llave.

    def start_game(self):
        """Start a new game."""
        self.level_number = 1
        self.lives = INITIAL_LIVES
        self.score = 0
        self.level = Level(self.level_number)
        self.state = "playing"

    def next_level(self):
        """Advance to the next level."""
        self.level_number += 1
        self.score += 100
        self.level = Level(self.level_number)
        self.state = "playing"

    def handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            # pygame.event.get() devuelve la lista de eventos ocurridos
            # desde la última vez que se llamó (teclas, mouse, cerrar ventana, etc).
            if event.type == pygame.QUIT:
                self.running = False
                return
                # Se activa cuando el usuario cierra la ventana con la X.

            if event.type == pygame.KEYDOWN:
                # Se activa una sola vez quando se presiona una tecla
                # (no se repite mientras se mantiene apretada).
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    else:
                        self.running = False
                    return

                if event.key == pygame.K_TAB:
                    self.use_mouse = not self.use_mouse
                    # not invierte el valor booleano: True pasa a False y viceversa.

                if self.state == "menu":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        # El operador "in" revisa si event.key es igual a
                        # alguno de los valores dentro de la tupla.
                        self.start_game()

                elif self.state == "playing":
                    pass  # Handled in update
                    # pass es una instrucción que no hace nada; se usa quando
                    # la sintaxis exige un bloque de código pero no hay nada que ejecutar.

                elif self.state == "level_complete":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.next_level()

                elif self.state == "game_over":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = "menu"

                elif self.state == "win":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = "menu"

    def update(self):
        """Update game state."""
        if self.state != "playing":
            return
            # Si no se está jugando (por ejemplo, se está en el menú),
            # no hay nada que actualizar.

        # Update key movement
        keys_pressed = pygame.key.get_pressed()
        # Devuelve una lista con el estado (presionada o no) de todas las teclas.
        mouse_pos = pygame.mouse.get_pos() if self.use_mouse else None
        # Si se está usando mouse, obtiene su posición actual; si no, usa None.
        self.level.key.update(keys_pressed, mouse_pos)

        # Update level
        result = self.level.update()

        if result is True:
            # Level completed
            self.score += int(self.level.timer) * 10
            if self.level_number >= 10:
                self.state = "win"
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                self.state = "level_complete"

        elif result is False:
            # Time out - lose a life
            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                # Restart current level
                self.level = Level(self.level_number)

    def draw_menu(self):
        """Draw main menu."""
        self.screen.fill(BLACK)
        # Pinta toda la pantalla de negro antes de dibujar encima.

        # Title
        title = self.font_large.render("KEY DOOR PUZZLE", True, WHITE)
        # render() convierte un texto en una imagen (Surface) que se puede dibujar.
        # El segundo parámetro (True) activa el antialiasing (bordes suaves).
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        # get_rect(center=...) genera un rectángulo centrado en el punto indicado.
        self.screen.blit(title, title_rect)
        # blit() dibuja una imagen sobre otra superficie, en la posición del rectángulo.

        # Draw sample shapes
        for i, shape in enumerate(SHAPES):
            x = WINDOW_WIDTH // 2 - 150 + i * 100
            y = 250
            draw_shape(self.screen, shape, x, y, 40, COLORS[shape])

        # Instructions
        instructions = [
            "Match the key to the correct door",
            "",
            "Arrow keys / WASD / Mouse to move",
            "TAB to switch control mode",
            "",
            "Press SPACE to start",
        ]
        for i, line in enumerate(instructions):
            color = WHITE if line else WHITE
            # Nota: esta línea siempre da WHITE en ambos casos (no cambia nada),
            # se deja igual que en el original para no alterar el comportamiento.
            text = self.font_small.render(line, True, GRAY if not line else WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 350 + i * 30))
            self.screen.blit(text, text_rect)

    def draw_hud(self):
        """Draw heads-up display."""
        # HUD significa "Head-Up Display": la información que se ve mientras se juega.
        # Level
        level_text = self.font_small.render(
            f"Level: {self.level_number}/10", True, WHITE
        )
        # f"..." es un f-string: permite insertar variables dentro del texto
        # usando llaves {}.
        self.screen.blit(level_text, (10, 10))

        # Lives
        lives_text = self.font_small.render(f"Lives: {self.lives}", True, (220, 50, 50))
        self.screen.blit(lives_text, (10, 35))

        # Score
        score_text = self.font_small.render(
            f"Score: {self.score}", True, (255, 200, 50)
        )
        self.screen.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))
        # Se resta el ancho del texto para que quede alineado a la derecha.

        # Timer
        time_color = WHITE
        if self.level.timer < 10:
            time_color = (220, 50, 50)
            # Cuando quedan menos de 10 segundos, el texto se pone rojo como aviso.
        timer_text = self.font_small.render(
            f"Time: {int(self.level.timer)}s", True, time_color
        )
        self.screen.blit(timer_text, (WINDOW_WIDTH - timer_text.get_width() - 10, 35))

        # Control mode
        mode = "Mouse" if self.use_mouse else "Keyboard"
        mode_text = self.font_tiny.render(
            f"Controls: {mode} (TAB to switch)", True, GRAY
        )
        self.screen.blit(mode_text, (10, WINDOW_HEIGHT - 25))

        # Key shape hint
        hint = f"Find the {self.level.key.shape} door"
        hint_text = self.font_small.render(hint, True, self.level.key.color)
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        self.screen.blit(hint_text, hint_rect)

    def draw_level_complete(self):
        """Draw level complete screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        # pygame.Surface crea una superficie nueva en blanco, del tamaño indicado.
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        # set_alpha controla la transparencia (0 = invisible, 255 = totalmente opaco).
        self.screen.blit(overlay, (0, 0))
        # Dibuja el overlay semi-transparente sobre toda la pantalla,
        # creando un efecto de oscurecido.

        text = self.font_large.render("LEVEL COMPLETE!", True, (50, 200, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(text, rect)

        bonus = f"Time bonus: +{int(self.level.timer) * 10} points"
        bonus_text = self.font_medium.render(bonus, True, WHITE)
        bonus_rect = bonus_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        self.screen.blit(bonus_text, bonus_rect)

        next_text = self.font_small.render("Press SPACE for next level", True, GRAY)
        next_rect = next_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70)
        )
        self.screen.blit(next_text, next_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("GAME OVER", True, (220, 50, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)

        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        )
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_small.render(
            "Press SPACE to return to menu", True, GRAY
        )
        restart_rect = restart_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        )
        self.screen.blit(restart_text, restart_rect)

    def draw_win(self):
        """Draw win screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("YOU WIN!", True, (255, 200, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)

        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        )
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_small.render(
            "Press SPACE to return to menu", True, GRAY
        )
        restart_rect = restart_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        )
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Main game loop."""
        while self.running:
            # Este es el bucle principal del juego: se repite mientras
            # self.running sea True, muchas veces por segundo.
            self.handle_events()
            self.update()

            # Draw based on state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.screen.fill(BLACK)
                self.level.draw(self.screen)
                self.draw_hud()
            elif self.state == "level_complete":
                self.screen.fill(BLACK)
                self.level.draw(self.screen)
                self.draw_hud()
                self.draw_level_complete()
            elif self.state == "game_over":
                self.draw_game_over()
            elif self.state == "win":
                self.draw_win()

            pygame.display.flip()
            # flip() actualiza toda la ventana con todo lo que se dibujó
            # en este cuadro (equivalente a "mostrar el resultado en pantalla").
            self.clock.tick(FPS)
            # Pausa el bucle lo necesario para no superar los FPS definidos.

        pygame.quit()
        # Cierra pygame de forma ordenada al salir del bucle.
        sys.exit()
        # Termina el programa por completo.


# ============================================================
# ENTRY POINT
# ============================================================
# Este bloque solo se ejecuta si el archivo se corre directamente
# (no si se importa como módulo desde otro archivo).

if __name__ == "__main__":
    game = Game()
    # Crea una instancia (objeto) de la clase Game, llamando a __init__.
    game.run()
    # Arranca el bucle principal del juego.
