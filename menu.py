import pygame
from hra import main as spust_hru

pygame.init()

obrazovka_sirka = 1920
obrazovka_vyska = 1080
screen = pygame.display.set_mode((obrazovka_sirka, obrazovka_vyska))
pygame.display.set_caption("Tour de Bike - Menu")

menu_img = pygame.image.load("img/main_menu.png").convert_alpha()

# TODO
# zmensit kolo v menu
# zmensit aktualni vybranou energii
# pridat kure
# upgrady, ruzny kola - horsky, silnicka, hardtail

def menu():
    while True:
        screen.blit(menu_img, (0,0))

        tlacitko_start = pygame.Rect(50,335,250,150)
        tlacitko_vylepseni = pygame.Rect(50,535,500,150)
        tlacitko_konec = pygame.Rect(50,750,250,150)
        
        # hitboxy
        pygame.draw.rect(screen, "red",tlacitko_start,1)
        pygame.draw.rect(screen, "red",tlacitko_vylepseni,1)
        pygame.draw.rect(screen, "red",tlacitko_konec,1)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_start.collidepoint(event.pos):
                    spust_hru()
                elif tlacitko_vylepseni.collidepoint(event.pos):
                    print("vylepseni neni :(")
                elif tlacitko_konec.collidepoint(event.pos):
                    pygame.quit()
                    quit()

menu()
