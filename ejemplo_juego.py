import pygame
import sys

# Inicializar pygame
pygame.init()

# Configuración de la ventana
ANCHO, ALTO = 600, 400
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mover rectángulo con flechas")

# Colores
VERDE_CLARO = (144, 238, 144)  # lightgreen
AZUL = (0, 0, 255)

# Rectángulo (posición inicial y tamaño)
rect_x, rect_y = 250, 150
rect_ancho, rect_alto = 100, 60
velocidad = 5

# Bucle principal
reloj = pygame.time.Clock()
while True:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Teclas presionadas
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        rect_x -= velocidad
        if rect_x < -rect_ancho:
            rect_x = ANCHO
    if teclas[pygame.K_RIGHT]:
        rect_x += velocidad
        if rect_x > ANCHO:
            rect_x = -rect_ancho
    if teclas[pygame.K_UP]:
        rect_y -= velocidad
        if rect_y < -rect_alto:
            rect_y = ALTO
    if teclas[pygame.K_DOWN]:
        rect_y += velocidad
        if rect_y > ALTO:
            rect_y = -rect_alto

    # Dibujar fondo y rectángulo
    VENTANA.fill(VERDE_CLARO)
    pygame.draw.rect(VENTANA, AZUL, (rect_x, rect_y, rect_ancho, rect_alto))

    # Actualizar pantalla
    pygame.display.flip()
    reloj.tick(60)  # 60 FPS
