import numpy as np
import pygame
from enum import Enum
from collections import namedtuple
# 육각 격자에 대한 수학적 설명 : https://www.redblobgames.com/grids/hexagons/
# 오리지널 snakegame 코드 참고 : https://github.com/python-engineer/snake-ai-pytorch/blob/main/snake_game_human.py

class Direction(Enum):
    # (dq, dr)
    one = (1, 0) # 0 rad
    two = (1, -1) # pi/3 rad
    three = (0, -1) # pi*2/3 rad
    four = (-1, 0) # pi rad
    five = (-1, 1) # pi*4/3 rad
    six = (0, 1) # pi*5/3 rad

Axial = namedtuple('Axial', ['q', 'r'])

class Game:
    def __init__(self):
        #경로 설정
        self.PATH =''

        # 기본 상수 설정
        self.cell_num = 10 # 육각격자 한 변에 cell이 몇개 들어가는지
        self.onecellsize = 20 # 육각cell 한변 길이(px)

        self.backgroundcolor = (44, 45, 45)
        self.gridcolor = (160, 165, 167)
        self.foodcolor = (197, 57, 10)
        self.headcolor = (94, 155, 121)
        self.bodycolor = (191, 218, 139)
        self.centercolor = (243, 250, 157)
        self.textcolor = (253, 100, 67)

        self.gridthick = 3
        self.speed = 4 # frames per second
        self.font = pygame.font.SysFont('arial', 25)

        # 화면 크기 설정
        self.screen_width = int((np.sqrt(3)*self.onecellsize) * (self.cell_num * 2 - 1) + 100)
        self.screen_height = int((self.onecellsize) * (3*self.cell_num-1) + 100)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # 화면 타이틀 설정
        pygame.display.set_caption("HEXAGONAL_SNAKE")

        # icon 설정
        gameicon = pygame.image.load(r'icon.png')
        pygame.display.set_icon(gameicon)

        # FPS
        self.clock = pygame.time.Clock()

        # 뱀 상태 초기화
        self.direction = Direction.one
        self.head = Axial(0, 0)
        self.snake = [self.head, Axial(self.head.q-1, self.head.r), Axial(self.head.q-2, self.head.r)]
        self.score = 0
        self.food = None
        self._place_food()
    
    def _place_food(self):
        '''육각격자 내 임의의 점에 food 생성함.'''
        while True:
            q = np.random.randint(-(self.cell_num-1), self.cell_num)
            r = np.random.randint(-(self.cell_num-1), self.cell_num)
            self.food = Axial(q, r)
            if (-(self.cell_num-1) <= q+r <= self.cell_num-1) and not (self.food in self.snake): # 육각 격자에 해당되고, 뱀 위치와 곂치지 않을때
                break

    def _get_center(self, axial):
        '''axial coordinates 를 바탕으로 육각형 중심 좌표 반환함.''' # axial = (q, r)
        q, r = axial
        center = (int(self.onecellsize * (np.sqrt(3)*q + np.sqrt(3)*r/2) + self.screen_width/2), 
                    int(self.onecellsize * (r*3/2) + self.screen_height/2))
        return center
        

    def _get_corner(self, center, size):
        '''중심 좌표를 바탕으로 모서리 좌표 반환함.''' # center = (width, height)
        corner = [[int(center[0] + size * np.cos(np.pi * (1/6 + (1/3)*i))),
                    int(center[1] + size * np.sin(np.pi * (1/6 + (1/3)*i)))] for i in range(6)]
        return corner

    def _draw_screen(self):
        '''배경 그리드, 뱀(머리, 몸통), 먹이, 점수표시 그리기.'''
        # 배경색
        self.screen.fill(self.backgroundcolor)

        # 배경 육각그리드 그리기
        for q in range(-(self.cell_num-1), self.cell_num): # -(self.cell_num-1)에서 (self.cell_num-1)까지
            for r in range(-(self.cell_num-1), self.cell_num):
                if (-(self.cell_num-1) <= q+r <= self.cell_num-1): 
                    center = self._get_center((q, r))  # 육각 격자 중심이 (0, 0)
                    corner = self._get_corner(center, self.onecellsize)
                    pygame.draw.polygon(self.screen, self.gridcolor, corner, self.gridthick)
        
        # 먹이 그리기
        center = self._get_center(self.food)
        corner = self._get_corner(center, self.onecellsize/2)
        pygame.draw.polygon(self.screen, self.foodcolor, corner)

        # 뱀 그리기
        totalcellnum = (3*self.cell_num**2 - 3*self.cell_num + 1) # 육각 격자 총 개수
        centerlist = []
        for i, cell in enumerate(self.snake):
            center = self._get_center(cell)
            centerlist.append(center)
            corner = self._get_corner(center, self.onecellsize - self.gridthick/2)
            # 색이 head -> body로 서서히 변하도록 
            color = (self.headcolor[0] * (1 - i/totalcellnum) + self.bodycolor[0] * (i/totalcellnum),
                    self.headcolor[1] * (1 - i/totalcellnum) + self.bodycolor[1] * (i/totalcellnum),
                    self.headcolor[2] * (1 - i/totalcellnum) + self.bodycolor[2] * (i/totalcellnum))
            pygame.draw.polygon(self.screen, color, corner)

            if i == 0: # 머리
                pygame.draw.polygon(self.screen, self.centercolor, self._get_corner(center, self.onecellsize/2))
        pygame.draw.lines(self.screen, self.centercolor, False, centerlist, 2) # 몸통에 선 표시해야 구분됨.

        # 점수 표시
        text = self.font.render('SCORE : ' + str(self.score), True, self.textcolor)
        self.screen.blit(text, [20, 20])
        pygame.display.update()

    def _hex_distance(self, axial1, axial2):
        '''Axial Coordinates 상에서 거리를 구함.'''
        return (np.abs(axial1.q - axial2.q) + np.abs(axial1.q + axial1.r - axial2.q - axial2.r) + np.abs(axial1.r - axial2.r))/2
    
    def _is_collision(self):
        # 경계면에 닿은 경우
        if self._hex_distance(self.head, Axial(0, 0)) >= self.cell_num:
            return True
        
        # 자기 자신과 부딪친 경우
        if self.head in self.snake[1:]:
            return True
        
        return False

    def play_step(self):
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 게임 종료 버튼 or Ctrl + C
                pygame.quit()
                quit() # 게임을 의도적으로 종료한경우
            
            # 방향 바꾸기
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.direction = Direction.one
                if event.key == pygame.K_2:
                    self.direction = Direction.two
                if event.key == pygame.K_3:
                    self.direction = Direction.three
                if event.key == pygame.K_4:
                    self.direction = Direction.four
                if event.key == pygame.K_5:
                    self.direction = Direction.five
                if event.key == pygame.K_6:
                    self.direction = Direction.six

        # 뱀 머리 위치 업데이트
        self.head = Axial(self.head.q + self.direction.value[0], self.head.r + self.direction.value[1])
        self.snake.insert(0, self.head)

        # 게임 종료 체크
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
        
        # 게임 종료가 아니라면 움직이거나 새로운 음식 추가
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop() # -> 가장 마지막 위치를 제거해 뱀 이동. 만약 음식을 먹으면 가장 마지막 위치가 제거되지 않기 때문에 뱀 길이가 늘어남.


        self._draw_screen()
        self.clock.tick(self.speed)
        return game_over, self.score 


if __name__ == '__main__':
    pygame.init()
    game = Game()

    while True:
        game_over, score = game.play_step()

        if game_over:
            break
    
    print('score : ', score)

    pygame.quit()