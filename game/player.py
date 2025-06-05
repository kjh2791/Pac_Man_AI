import pygame
import time
from game.constants import *
import os

class Player:
    def __init__(self, x, y, learning_system=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.speed = 0.1  # 타일당 이동 시간(초)
        self.last_move_time = time.time()
        self.score = 0
        self.lives = 3
        self.powered_up = False
        self.power_time = 0
        self.power_duration = 3 # 파워 펠릿 지속 시간 (초)
        self.move_history = []
        self.last_positions = []
        self.learning_system = learning_system
        self.last_pellet_time = time.time()
        self.frame_count = 0
        self.player_imgs = [
            pygame.image.load(os.path.join('assets', 'sprites', 'player_0.png')).convert_alpha(),
            pygame.image.load(os.path.join('assets', 'sprites', 'player_1.png')).convert_alpha()
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in KEY_MAPPING:
            self.next_direction = KEY_MAPPING[event.key]

    def update(self, map_manager, ghost_positions):
        current_time = time.time()
        if self.powered_up and current_time - self.power_time > self.power_duration:
            self.powered_up = False
        if current_time - self.last_move_time >= self.speed:
            self.move(map_manager, ghost_positions)
            self.last_move_time = current_time

    def move(self, map_manager, ghost_positions):
        dx, dy = DIRECTIONS[self.next_direction]
        nx, ny = self.x + dx, self.y + dy
        prev_pos = (self.x, self.y)
        moved = False
        if map_manager.is_valid_move(nx, ny):
            self.record_move((self.x, self.y), (nx, ny))
            self.x, self.y = nx, ny
            self.direction = self.next_direction
            moved = True
        else:
            dx, dy = DIRECTIONS[self.direction]
            nx, ny = self.x + dx, self.y + dy
            if map_manager.is_valid_move(nx, ny):
                self.record_move((self.x, self.y), (nx, ny))
                self.x, self.y = nx, ny
                moved = True
        # 펠릿 수집
        score = map_manager.collect_pellet(self.x, self.y)
        self.score += score
        if score == POWER_PELLET_SCORE:
            self.powered_up = True
            self.power_time = time.time()
            # 파워펠릿 먹은 타이밍 기록
            if self.learning_system:
                self.learning_system.power_pellet_timing.append(time.time() - self.last_pellet_time)
            self.last_pellet_time = time.time()
        # 이동 데이터 분석
        if self.learning_system and moved:
            # 코너링 습관: 방향 전환 시점 기록
            is_corner = False
            if self.direction != self.next_direction:
                is_corner = True
            # 고스트 위치 정보도 analyze_player_move에 전달
            self.learning_system.analyze_player_move(prev_pos, (self.x, self.y), {
                'direction': self.direction,
                'next_direction': self.next_direction,
                'is_corner': is_corner,
                'score': self.score
            }, ghost_positions)

    def record_move(self, from_pos, to_pos):
        move_data = {
            'from': from_pos,
            'to': to_pos,
            'direction': self.direction,
            'timestamp': time.time()
        }
        self.move_history.append(move_data)
        self.last_positions.append(to_pos)
        if len(self.last_positions) > 10:
            self.last_positions.pop(0)
        if len(self.move_history) > MAX_LEARNING_HISTORY:
            self.move_history.pop(0)

    def get_pos(self):
        return (self.x, self.y)

    def reset(self, x, y):
        self.x, self.y = x, y
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.powered_up = False

    def render(self, screen):
        # 애니메이션: 프레임 카운터로 입 열고 닫기
        self.frame_count = (self.frame_count + 1) % 30
        img_idx = 0 if self.frame_count < 15 else 1
        player_img = self.player_imgs[img_idx]
        center_x = self.x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.y * TILE_SIZE + TILE_SIZE // 2
        rect = player_img.get_rect(center=(center_x, center_y))
        # 방향에 따라 이미지 회전
        angle = 180
        if self.direction == 'UP':
            angle = -90
        elif self.direction == 'LEFT':
            angle = 0
        elif self.direction == 'DOWN':
            angle = 90
        rotated_img = pygame.transform.rotate(player_img, angle)
        screen.blit(rotated_img, rect)

    def lose_life(self):
        """생명 잃기"""
        self.lives -= 1
        self.reset(self.start_x, self.start_y)
        return self.lives <= 0

    def is_powered_up(self):
        """파워업 상태 확인"""
        return self.powered_up

    def get_power_time_left(self):
        """파워업 남은 시간"""
        if not self.powered_up:
            return 0
        elapsed = time.time() - self.power_time
        return max(0, self.power_duration - elapsed)

    def clear_learning_data(self):
        """학습 데이터 초기화 (새 게임 시작 시)"""
        self.move_history.clear()
        self.last_positions.clear()