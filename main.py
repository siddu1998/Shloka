# from shloka import speechToEnglish,speechToHindi,record_player_audio

# audio_file=record_player_audio()
# user_hindi=speechToHindi(audio_file)
# user_english=speechToEnglish(audio_file)
# print(user_hindi)
# print(user_english)

import pygame 

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH*0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shloka")

class Soldier(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y 
        self.scale = scale
        img  = pygame.image.load("img/player/Idle/0.png")
        self.image = pygame.transform.scale(img, (int(scale*img.get_width()),int(scale*img.get_height())))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)



player = Soldier(200,200,3)

run = True
while run:
    screen.blit(player.image, player.rect)
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT: #clicked on the cross button
            run = False

    pygame.display.update()

pygame.quit()





