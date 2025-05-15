import pygame 
import math

pygame.init()

obrazovka_sirka = 1920
obrazovka_vyska = 1080
screen = pygame.display.set_mode((obrazovka_sirka, obrazovka_vyska))
pygame.display.set_caption("Tour de Bike")

barva_nebe = (135, 206, 235)
barva_trava = (0,154,23)

bezi = True
clock = pygame.time.Clock()

krok = 10

def generace_bod(x):
    i = x / 10
    obtiznost = 1 + (x / 25000)

    y = (obrazovka_vyska * 0.7
         + math.sin(i * 0.004 * obtiznost) * (120 * obtiznost)   
         + math.sin(i * 0.025 * obtiznost + math.cos(i * 0.002)) * (60 * obtiznost)  
         + math.sin(i * 0.13 + math.cos(i * 0.03)) * (18 + obtiznost * 5)            
         + math.sin(i * 0.0025)                   
         + math.cos(i * 0.7) * 2                                                     
    )
    return y

kolo_x = 0
kolo_y = generace_bod(kolo_x)
kolo_rychlost_x = 0
kolo_rychlost_y = 0
kolo_akcelerace = 0.7
kolo_top_rychlost = 18
gravitace = 1.2
odpor_vzduchu = 0.02  
kolo_skok = 25

kolo_obrazky = []
for i in range(14):
    if i < 10:
        img = pygame.image.load(f"img/kolo000{i}.png").convert_alpha()
    else:
        img = pygame.image.load(f"img/kolo00{i}.png").convert_alpha()
    img_sirka = img.get_width()
    img_vyska = img.get_height()
    img = pygame.transform.scale(img, (img_sirka/4, img_vyska/4))  
    kolo_obrazky.append(img)

while bezi:
    screen.fill(barva_nebe)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            bezi = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        kolo_rychlost_x -= kolo_akcelerace
    if keys[pygame.K_d]:
        kolo_rychlost_x += kolo_akcelerace

    if keys[pygame.K_w]:
        kolo_y -= kolo_skok

    kolo_rychlost_x = kolo_rychlost_x * (1 - odpor_vzduchu)


    kolo_rychlost_x = max(-kolo_top_rychlost, min(kolo_rychlost_x, kolo_top_rychlost))


    kolo_x += kolo_rychlost_x

    kolo_rychlost_y += gravitace
    kolo_y += kolo_rychlost_y

    teren_y = generace_bod(kolo_x)

    if kolo_y > teren_y:
        kolo_y = teren_y
        kolo_rychlost_y = 0

    kamera_x = kolo_x - obrazovka_sirka // 2
    kamera_y = kolo_y - obrazovka_vyska // 1.5

    dx = img_sirka / 4
    y1 = generace_bod(kolo_x - dx)
    y2 = generace_bod(kolo_x + dx)

    uhel = math.atan2(y2 - y1, 2 * dx)


    if kolo_y == teren_y:
        kolo_rychlost_x += math.sin(uhel) * gravitace

    body = [[0, obrazovka_vyska]]
    x_obrazovka = 0
    x_svet = kamera_x - (kamera_x % krok)

    while x_obrazovka < obrazovka_sirka + krok:
        y = generace_bod(x_svet) - kamera_y
        body.append([x_obrazovka, y])
        x_svet += krok
        x_obrazovka = x_svet - kamera_x

    body.append([obrazovka_sirka, obrazovka_vyska])

    pygame.draw.polygon(screen, barva_trava, body)

    kolo_obrazovka_x = obrazovka_sirka // 2
    kolo_obrazovka_y = kolo_y - kamera_y

    animace_index = int((kolo_x / 30) % 14) 

    kolo_img = pygame.transform.rotate(kolo_obrazky[animace_index], -math.degrees(uhel))
    rect = kolo_img.get_rect(center=(kolo_obrazovka_x, kolo_obrazovka_y - 80))
    screen.blit(kolo_img, rect.topleft)

    pygame.display.update()
    clock.tick(60)

pygame.quit()