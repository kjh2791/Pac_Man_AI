# constants.py - 게임 상수 정의

import pygame

# 화면 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# 게임 요소 색상
WALL_COLOR = (50, 50, 200)
PELLET_COLOR = (255, 184, 151)
POWER_PELLET_COLOR = (255, 255, 0)
PLAYER_COLOR = YELLOW
GHOST_COLORS = [RED, PINK, CYAN, ORANGE]

# 맵 타일 정의
EMPTY = 0
WALL = 1
PELLET = 2
POWER_PELLET = 3
GHOST_SPAWN = 4
PLAYER_SPAWN = 5

# 게임 설정
PLAYER_SPEED = 1.2
GHOST_SPEED = 1.0
GHOST_FRIGHTENED_SPEED = 0.8
POWER_PELLET_DURATION = 300  # 프레임 단위 (5초)

# AI 설정
AI_UPDATE_FREQUENCY = 4  # 매 4프레임마다 AI 업데이트 (15fps)
LEARNING_MEMORY_SIZE = 200  # 최근 이동 200개만 기억
LEARNING_PHASES = {
    0: "기본 AI",           # 0-20 이동
    1: "패턴 인식 시작",     # 21-50 이동  
    2: "예측 시작",         # 51-100 이동
    3: "고급 적응",         # 100+ 이동
    4: "마스터 레벨"        # 200+ 이동
}

# 고스트 타입
GHOST_AGGRESSIVE = "aggressive"
GHOST_AMBUSH = "ambush"
GHOST_COOPERATIVE = "cooperative"
GHOST_PREDICTIVE = "predictive"

# 고스트 상태
GHOST_CHASE = "chase"
GHOST_SCATTER = "scatter"
GHOST_FRIGHTENED = "frightened"
GHOST_EATEN = "eaten"

# 방향 정의
DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}

# 키보드 매핑
# ... 기존 상수 ...
KEY_MAPPING = {
    pygame.K_UP: 'UP',
    pygame.K_DOWN: 'DOWN',
    pygame.K_LEFT: 'LEFT',
    pygame.K_RIGHT: 'RIGHT',
    pygame.K_w: 'UP',
    pygame.K_s: 'DOWN',
    pygame.K_a: 'LEFT',
    pygame.K_d: 'RIGHT'
}
MAX_LEARNING_HISTORY = 200

# 점수 시스템
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
GHOST_BASE_SCORE = 200
LEVEL_COMPLETE_BONUS = 1000

# 기본 맵 (20x15 타일)
DEFAULT_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
    [1,3,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,3,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,0,4,4,0,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,0,1,4,4,4,4,1,0,1,2,1,1,1,1],
    [0,0,0,0,2,0,0,1,4,4,4,4,1,0,0,2,0,0,0,0],
    [1,1,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,0,0,0,0,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,5,5,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# 게임 상태
GAME_MENU = "menu"
GAME_PLAYING = "playing"
GAME_PAUSED = "paused"
GAME_OVER = "game_over"
GAME_LEVEL_COMPLETE = "level_complete"