import pygame
import pygame.gfxdraw
import math
from fyzika import Vector, Bike, BIKE_LENGTH, WHEEL_RADIUS

pygame.init()

import fyzika
fyzika.GRAVITY = Vector(0, 0.2)

obrazovka_sirka = 1920
obrazovka_vyska = 1080
screen = pygame.display.set_mode((obrazovka_sirka, obrazovka_vyska))
pygame.display.set_caption("Tour de Bike")

barva_nebe = (135, 206, 235)
barva_trava = (0, 154, 23)

fyzika.krok = 10
fyzika.obtiznost_mapy = 10000  # nizsi cislo = tezsi
fyzika.obrazovka_vyska = obrazovka_vyska

def nahrat_obrazky():
    obrazky = []
    for i in range(14):
        if i < 10:
            img = pygame.image.load(f"img/kolo000{i}.png").convert_alpha()
        else:
            img = pygame.image.load(f"img/kolo00{i}.png").convert_alpha()
        img_sirka = img.get_width()
        img_vyska = img.get_height()
        k = BIKE_LENGTH / img_sirka
        img = pygame.transform.smoothscale(img, (img_sirka * k, img_vyska * k))
        obrazky.append(img)
    return obrazky

def blit_rotate_bottom_left(surf, image, bottom_left_pos, angle):
    image_rect = image.get_rect()
    width, height = image_rect.size
    offset_center_to_bl = pygame.math.Vector2(-width / 2, height / 2)
    rotated_offset = offset_center_to_bl.rotate(-angle)
    rotated_center = (bottom_left_pos[0] - rotated_offset.x, bottom_left_pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotozoom(image, angle, 1.0)
    new_rect = rotated_image.get_rect(center=rotated_center)
    surf.blit(rotated_image, new_rect.topleft)

def vykresli_text(surf, text, barva, pozice, zarovnat="left", velikost=50, font="Arial"):
    font = pygame.font.SysFont(font, velikost)
    text_surface = font.render(text, True, barva)
    text_rect = text_surface.get_rect()
    if zarovnat == "left":
        text_rect.topleft = pozice
    elif zarovnat == "center":
        text_rect.center = pozice
    elif zarovnat == "right":
        text_rect.topright = pozice
    surf.blit(text_surface, text_rect)

class EnergetickyPredmet(pygame.sprite.Sprite):
    def __init__(self, x, y, obrazek, pridavek_energie):
        super().__init__()
        self.svet_x = x
        self.svet_y = y
        self.pridavek_energie = pridavek_energie
        self.image = obrazek

    def vykresli(self, screen, kamera_x, kamera_y):
        screen.blit(self.image, (self.svet_x - kamera_x, self.svet_y - kamera_y))

    def hitbox(self):
        return pygame.Rect(self.svet_x, self.svet_y, self.image.get_width(), self.image.get_height())

def vykresli_ui(screen, km, energie, kolo_x, rychlost, cas):
    vykresli_text(screen, f"Ujeto: {round(km/1000,1)} km", (0, 0, 0), (22, 20))

    pygame.draw.rect(screen, (50, 50, 50), (20, 90, 250, 40))
    if energie > 0:
        pygame.draw.rect(screen, (255, 215, 0), (20, 90, 2.5 * energie, 40))
    pygame.draw.rect(screen, (0, 0, 0), (20, 90, 250, 40), 2)

    screen.blit(tachometr_img, (50, 650))

    sekundy = cas // 1000
    minuty = sekundy // 60
    hodiny = minuty // 60
    sekundy = sekundy % 60
    minuty = minuty % 60

    vykresli_text(screen, f"{hodiny}:{minuty}:{sekundy}", (255, 255, 255), (252, 970), zarovnat="center", velikost=30)

    stred_x = 250
    stred_y = 845
    delka_rucicky = 170
    uhel = -220 + (abs(rychlost) / 70) * 262
    uhel_rad = math.radians(uhel)
    konec_x = stred_x + delka_rucicky * math.cos(uhel_rad)
    konec_y = stred_y + delka_rucicky * math.sin(uhel_rad)
    pygame.draw.line(screen, (255, 0, 0), (stred_x, stred_y), (konec_x, konec_y), 6)

    if energie_predmety:
        predmety_vpravo = []
        for predmet in energie_predmety:
            if predmet.svet_x > kolo_x:
                predmety_vpravo.append(predmet)

        nejblizsi = None
        nejmensi_vzdalenost = None

        for predmet in predmety_vpravo:
            rozdil = predmet.svet_x - kolo_x
            if nejmensi_vzdalenost is None or rozdil < nejmensi_vzdalenost:
                nejblizsi = predmet
                nejmensi_vzdalenost = rozdil

        if nejblizsi:
            vzdalenost = nejblizsi.svet_x - kolo_x
            vykresli_text(screen, f"{round(vzdalenost/1000,1)} km →", (0, 0, 0), (obrazovka_sirka - 20, 20), zarovnat="right")

def vykresli_teren(screen, kamera_x, kamera_y):
    body = [[0, obrazovka_vyska]]
    x_svet = kamera_x - (kamera_x % fyzika.krok)

    while True:
        x_obrazovka = x_svet - kamera_x
        if x_obrazovka > obrazovka_sirka + fyzika.krok:
            break
        y = fyzika.generace_bod(x_svet) - kamera_y
        body.append([x_obrazovka, y])
        x_svet += fyzika.krok

    body.append([obrazovka_sirka, obrazovka_vyska])

    pygame.gfxdraw.filled_polygon(screen, body, barva_trava)
    pygame.gfxdraw.aapolygon(screen, body, (10, 50, 10))

def vykresli_kolo(kolo, camera, rafek_img, kolo_img):
    rafek_rear_rot = pygame.transform.rotozoom(rafek_img, (kolo.rear_wheel.get_position().x / (WHEEL_RADIUS)) * (-180 / math.pi), 1.0)
    rafek_front_rot = pygame.transform.rotozoom(rafek_img, (kolo.front_wheel.get_position().x / (WHEEL_RADIUS)) * (-180 / math.pi), 1.0)

    rafek_rect_rear = rafek_rear_rot.get_rect(center=(int(kolo.rear_wheel.position.x - camera.x), int(kolo.rear_wheel.position.y - camera.y)))
    rafek_rect_front = rafek_front_rot.get_rect(center=(int(kolo.front_wheel.position.x - camera.x), int(kolo.front_wheel.position.y - camera.y)))

    screen.blit(rafek_rear_rot, rafek_rect_rear.topleft)
    screen.blit(rafek_front_rot, rafek_rect_front.topleft)

    center = kolo.rear_axel.position
    blit_rotate_bottom_left(screen, kolo_img, (int(center.x - camera.x), int(center.y - camera.y)), (-180 / math.pi) * math.atan2(kolo.front_axel.position.y - kolo.rear_axel.position.y, kolo.front_axel.position.x - kolo.rear_axel.position.x))

font = pygame.font.SysFont("Arial", 50)
banan_img = pygame.image.load("img/banan.png").convert_alpha()
k = 80 / banan_img.get_width()
banan_img = pygame.transform.scale(banan_img, (int(banan_img.get_width() * k), int(banan_img.get_height() * k)))
banan_energie = 30
tycinka_img = pygame.image.load("img/tycinka.png").convert_alpha()
k = 120 / tycinka_img.get_width()
tycinka_img = pygame.transform.scale(tycinka_img, (int(tycinka_img.get_width() * k), int(tycinka_img.get_height() * k)))
tycinka_energie = 50

energie_predmety = pygame.sprite.Group()

tachometr_img = pygame.image.load("img/tachometr.png").convert_alpha()
tachometr_img = pygame.transform.scale(tachometr_img, (400, 400))

obtiznost_mapy = 2500 # nizsi cislo = tezsi
ztrata_energie = 0.05
pridavek_energie = 30
rust_vzdalenosti = 500

def main():
    start_cas = pygame.time.get_ticks()
    bezi = True
    clock = pygame.time.Clock()
    ram_obrazky = nahrat_obrazky()
    rafek_img = pygame.image.load("img/rafek.png").convert_alpha()
    rafek_img = pygame.transform.scale(rafek_img, (WHEEL_RADIUS * 2, WHEEL_RADIUS * 2))

    kolo = Bike(Vector(obrazovka_sirka / 2, 250))

    km_ujet = 0
    vzdalenost_predmetu = 1000

    # TODO: upgrad z bananu na tycinku pro vice energie
    energie_predmety.add(EnergetickyPredmet(1500, fyzika.generace_bod(1500)-250, tycinka_img, tycinka_energie))

    camera = Vector(0, 0)

    while bezi:
        screen.fill(barva_nebe)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        kolo.tick()
        vykresli_kolo(kolo, camera, rafek_img, ram_obrazky[int(kolo.animace_index)])
        camera = fyzika.lerp(camera, kolo.rear_axel.position - Vector(-BIKE_LENGTH / 2 + obrazovka_sirka/2, obrazovka_vyska/2), 0.1)

        vykresli_teren(screen, camera.x, camera.y)
        

        for predmet in energie_predmety.copy():
            predmet.vykresli(screen, camera.x, camera.y)
            zadni = kolo.rear_wheel.get_position()
            predni = kolo.front_wheel.get_position()
            if predmet.hitbox().collidepoint(zadni.x, zadni.y) or predmet.hitbox().collidepoint(predni.x, predni.y):
                kolo.energie = min(kolo.energie + predmet.pridavek_energie, 100)
                energie_predmety.remove(predmet)

        if kolo.rear_axel.get_position().x > vzdalenost_predmetu:
            vzdalenost_predmetu += rust_vzdalenosti
            nova_predmet_x = kolo.rear_axel.get_position().x + vzdalenost_predmetu
            energie_predmety.add(EnergetickyPredmet(nova_predmet_x, fyzika.generace_bod(nova_predmet_x) - 150, banan_img, banan_energie))

        km_ujet = kolo.rear_axel.get_position().x

        kolo.energie -= ztrata_energie
        if kolo.energie < -10:
            energie_predmety.empty()
            main()

        rychlost = kolo.rear_wheel.get_speed().x
        vykresli_ui(screen, km_ujet, kolo.energie, kolo.rear_axel.get_position().x, rychlost, pygame.time.get_ticks() - start_cas)

        pygame.display.flip()
        clock.tick(60)

main()