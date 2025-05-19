import pygame
import math
import random

pygame.init()

obrazovka_sirka = 1920
obrazovka_vyska = 1080
screen = pygame.display.set_mode((obrazovka_sirka, obrazovka_vyska))
pygame.display.set_caption("Tour de Bike")

barva_nebe = (135, 206, 235)
barva_trava = (0,154,23)

krok = 10

def generace_bod(x):
    i = x / 10
    obtiznost = 1 + (x / obtiznost_mapy)
    y = (obrazovka_vyska * 0.7
         + math.sin(i * 0.004) * (120 * obtiznost)
         + math.sin(i * 0.025 + math.cos(i * 0.002)) * (60 * obtiznost)
         + math.sin(i * 0.13 + math.cos(i * 0.03)) * (18 + obtiznost * 5)
         + math.sin(i * 0.0025)
         + math.cos(i * 0.7) * 2
    )
    return y

def nahrat_obrazky():
    obrazky = []
    for i in range(14):
        if i < 10:
            img = pygame.image.load(f"img/kolo000{i}.png").convert_alpha()
        else:
            img = pygame.image.load(f"img/kolo00{i}.png").convert_alpha()
        img_sirka = img.get_width()
        img_vyska = img.get_height()
        img = pygame.transform.scale(img, (img_sirka//4, img_vyska//4))
        obrazky.append(img)
    return obrazky

def blitRotate(surf, image, origin, pivot, angle):
    # https://stackoverflow.com/questions/15098900/how-to-set-the-pivot-point-center-of-rotation-for-pygame-transform-rotate
    image_rect = image.get_rect(topleft=(origin[0] - pivot[0], origin[1] - pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)

class CyklistickeKolo(pygame.sprite.Sprite):
    def __init__(self, x, y, obrazky_ramu, obrazek_rafku):
        super().__init__()
        self.x = x
        self.y = y
        self.rychlost_x = 0
        self.rychlost_y = 0
        self.akcelerace = 0.7
        self.top_rychlost = 70
        self.gravitace = 1.2
        self.odpor_vzduchu = 0.02
        self.skok = 25

        self.kolo_polomer = 48
        self.kolo_vzdalenost = 140
        self.x_zadni_kolo = self.x - self.kolo_vzdalenost // 2 
        self.x_predni_kolo = self.x + self.kolo_vzdalenost // 2 
        self.y_zadni_kolo = generace_bod(self.x_zadni_kolo)
        self.y_predni_kolo = generace_bod(self.x_predni_kolo)
        # y je bod doteku kola terenu
        self.rafek_img = pygame.image.load(obrazek_rafku).convert_alpha()
        self.rafek_img = pygame.transform.scale(self.rafek_img, (self.kolo_polomer*2, self.kolo_polomer*2))
        self.rafek_uhel = 0

        self.ram_obrazky = obrazky_ramu
        self.animace_pocet = len(self.ram_obrazky)
        self.animace_index = 0

    def pohyb(self, keys):
        if self.je_na_zemi():
            if keys[pygame.K_a]:
                self.rychlost_x -= self.akcelerace
                self.animace_index -= 0.5
                if self.animace_index < 0:
                    self.animace_index = self.animace_pocet - 1
            if keys[pygame.K_d]:
                self.rychlost_x += self.akcelerace
                self.animace_index += 0.5
                if self.animace_index >= self.animace_pocet:
                    self.animace_index = 0
            if keys[pygame.K_w]:
                self.rychlost_y = -self.skok
        if keys[pygame.K_s]:
            print("Zadni kolo x:", self.x_zadni_kolo)
            print("Predni kolo x:", self.x_predni_kolo)
            print("Zadni kolo y (spodek):", self.y_zadni_kolo)
            print("Predni kolo y (spodek):", self.y_predni_kolo)
            print("zadni kolo generace:", generace_bod(self.x_zadni_kolo))
            print("Predni kolo generace:", generace_bod(self.x_predni_kolo))
            print("Y:", self.y)
            print("x:", self.x)

    def aktualizace(self):
        self.rychlost_y += self.gravitace

        if not self.je_na_zemi(50):
            self.y_zadni_kolo += self.rychlost_y
            self.y_predni_kolo = self.y_zadni_kolo
        else:
            self.y_zadni_kolo += self.rychlost_y
            self.y_predni_kolo += self.rychlost_y

        self.rychlost_x *= (1 - self.odpor_vzduchu)
        self.rychlost_x = max(-self.top_rychlost, min(self.rychlost_x, self.top_rychlost))
        self.x += self.rychlost_x
        self.x_zadni_kolo = self.x - self.kolo_vzdalenost // 2                                  
        self.x_predni_kolo = self.x + self.kolo_vzdalenost // 2

        teren_zadni = generace_bod(self.x_zadni_kolo)
        if self.y_zadni_kolo > teren_zadni:
            self.y_zadni_kolo = teren_zadni
        teren_predni = generace_bod(self.x_predni_kolo)
        if self.y_predni_kolo > teren_predni:
            self.y_predni_kolo = teren_predni
        if self.y_predni_kolo == teren_predni and self.y_zadni_kolo == teren_zadni:
            self.rychlost_y = 0

        self.y = (self.y_zadni_kolo + self.y_predni_kolo - (2*self.kolo_polomer)) / 2

        if self.je_na_zemi():
            self.rychlost_x += math.sin(self.naklon()) * self.gravitace

    def je_na_zemi(self, tolerance=0):
        if self.y_zadni_kolo >= (generace_bod(self.x_zadni_kolo)-tolerance) or self.y_predni_kolo >= (generace_bod(self.x_predni_kolo)-tolerance):
            return True
        else:
            return False

    def naklon(self):
        stred_zadni = self.y_zadni_kolo - self.kolo_polomer
        stred_predni = self.y_predni_kolo - self.kolo_polomer
        return math.atan2(stred_predni - stred_zadni, self.kolo_vzdalenost)
    
    def vykresli(self, kamera_x, kamera_y, screen):
        obvod = self.kolo_polomer * 2 * math.pi
        self.rafek_uhel -= (self.rychlost_x / obvod) * 360
        self.rafek_uhel %= 360

        rotace_rafek_img = pygame.transform.rotate(self.rafek_img, self.rafek_uhel)
        rafek_rect = rotace_rafek_img.get_rect(center=(self.x_zadni_kolo - kamera_x, self.y_zadni_kolo - self.kolo_polomer - kamera_y))
        screen.blit(rotace_rafek_img, rafek_rect)
        rafek_rect = rotace_rafek_img.get_rect(center=(self.x_predni_kolo - kamera_x, self.y_predni_kolo - self.kolo_polomer - kamera_y))
        screen.blit(rotace_rafek_img, rafek_rect)


        ram = self.ram_obrazky[int(self.animace_index)]
        uhel_ramu = -math.degrees(self.naklon())

        blitRotate(screen, ram, (self.x_zadni_kolo - kamera_x, self.y_zadni_kolo - self.kolo_polomer - kamera_y), (0,ram.get_height()), uhel_ramu)

    def hitbox(self):
        vyska_ramu = self.ram_obrazky[0].get_height()

        return pygame.Rect(self.x_zadni_kolo, max(self.y_zadni_kolo, self.y_predni_kolo) - vyska_ramu, self.x_predni_kolo - self.x_zadni_kolo, vyska_ramu)


class Banan(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.svet_x = x
        self.svet_y = y
        self.image = banan_img

    def vykresli(self, screen, kamera_x, kamera_y):
        screen.blit(self.image, (self.svet_x - kamera_x, self.svet_y - kamera_y))
    

def vykresli_ui(screen, km, energie, kolo_x, rychlost):
    text_km = font.render(f"Ujeto: {round(km/1000,1)} km", True, (0, 0, 0))
    screen.blit(text_km, (22, 20))

    pygame.draw.rect(screen, (50, 50, 50), (20, 90, 250, 40))
    if energie > 0:
        pygame.draw.rect(screen, (255, 215, 0), (20, 90, 2.5 * energie, 40))
    pygame.draw.rect(screen, (0, 0, 0), (20, 90, 250, 40), 2)

    screen.blit(tachometr_img, (50, 650))

    stred_x = 250
    stred_y = 845
    delka_rucicky = 170
    uhel = -220 + (abs(rychlost) / 70) * 262
    uhel_rad = math.radians(uhel)
    konec_x = stred_x + delka_rucicky * math.cos(uhel_rad)
    konec_y = stred_y + delka_rucicky * math.sin(uhel_rad)
    pygame.draw.line(screen, (255, 0, 0), (stred_x, stred_y), (konec_x, konec_y), 6)


    if banany:
        nejblizsi_banan = min(banany, key=lambda b: b.svet_x - kolo_x if b.svet_x > kolo_x else float('inf'))
        vzdalenost = nejblizsi_banan.svet_x - kolo_x
        if vzdalenost > 0:
            text_sipka = font.render(f"{round(vzdalenost/1000,1)} km →", True, (0,0,0))
            text_rect = text_sipka.get_rect()
            screen.blit(text_sipka, (obrazovka_sirka - text_rect.width - 20, 20))


def vykresli_teren(screen, kamera_x, kamera_y):
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


font = pygame.font.SysFont("Arial", 50)
banany = pygame.sprite.Group()
banan_img = pygame.image.load("img/banan.png").convert_alpha()
banan_img = pygame.transform.scale(banan_img, (100, 100))

tachometr_img = pygame.image.load("img/tachometr.png").convert_alpha()
tachometr_img = pygame.transform.scale(tachometr_img, (400, 400))

energie = 100
obtiznost_mapy = 25000 # vyssi = tezsi
ztrata_energie = 0.05
pridavek_energie = 30
rust_vzdalenosti_bananu = 1.5

def main():
    bezi = True
    clock = pygame.time.Clock()
    ram_obrazky = nahrat_obrazky()
    obrazek_rafku = "img/rafek.png"  

    kolo = CyklistickeKolo(0, generace_bod(0), ram_obrazky, obrazek_rafku)

    km_ujet = 0
    energie = 100
    vzdalenost_bananu = 1000


    banany.add(Banan(vzdalenost_bananu, generace_bod(vzdalenost_bananu)-random.randint(100,500)))

    while bezi:
        screen.fill(barva_nebe)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bezi = False

        keys = pygame.key.get_pressed()
        if energie > 0:
            kolo.pohyb(keys)
        kolo.aktualizace()

        kamera_x = kolo.x - obrazovka_sirka // 2
        kamera_y = kolo.y - obrazovka_vyska // 1.5

        vykresli_teren(screen, kamera_x, kamera_y)
        kolo.vykresli(kamera_x, kamera_y, screen)

        for banan in banany.copy():
            banan.vykresli(screen, kamera_x, kamera_y)
            hitbox = kolo.hitbox()
            banan_rect = pygame.Rect(banan.svet_x, banan.svet_y, banan.image.get_width(), banan.image.get_height())

            if hitbox.colliderect(banan_rect):
                energie = min(energie + pridavek_energie, 100)
                banany.remove(banan)

                vzdalenost_bananu *= rust_vzdalenosti_bananu
                banany.add(Banan(kolo.x + vzdalenost_bananu, generace_bod(kolo.x + vzdalenost_bananu) - random.randint(100, 500)))

        if kolo.x > vzdalenost_bananu:
            vzdalenost_bananu *= rust_vzdalenosti_bananu
            banany.add(Banan(kolo.x + vzdalenost_bananu, generace_bod(kolo.x + vzdalenost_bananu) - random.randint(100, 500)))

        km_ujet = kolo.x

        energie -= ztrata_energie
        if energie < -10:
            # hrac muze na setrvacnost ziskat energii :) - par sekund
            bezi = False

        vykresli_ui(screen, km_ujet, energie, kolo.x, kolo.rychlost_x)


        pygame.display.flip()
        clock.tick(60)

main()