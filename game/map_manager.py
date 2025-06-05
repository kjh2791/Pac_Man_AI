# map_manager.py - 미로 맵 관리 시스템

import pygame
import copy
from game.constants import *
import os

class MapManager:
    def __init__(self):
        self.original_map = self.load_map_from_file(os.path.join('assets', 'map.txt'))
        self.reset()
        self.player_start_x, self.player_start_y = self.player_spawn_point

    def load_map_from_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            map_data = []
            for line in lines:
                row = [int(x) for x in line.strip().split() if x]
                if row:
                    map_data.append(row)
            return map_data
        else:
            from game.constants import DEFAULT_MAP
            return DEFAULT_MAP

    def reset(self):
        self.current_map = copy.deepcopy(self.original_map)
        self.width = len(self.current_map[0])
        self.height = len(self.current_map)
        self.pellets_remaining = sum(row.count(PELLET) + row.count(POWER_PELLET) for row in self.current_map)
        self.power_pellets = [(x, y) for y, row in enumerate(self.current_map) for x, v in enumerate(row) if v == POWER_PELLET]
        self.ghost_spawn_points = [(x, y) for y, row in enumerate(self.current_map) for x, v in enumerate(row) if v == GHOST_SPAWN]
        self.player_spawn_point = next(((x, y) for y, row in enumerate(self.current_map) for x, v in enumerate(row) if v == PLAYER_SPAWN), (1, 1))
        self.player_start_x, self.player_start_y = self.player_spawn_point

    def is_wall(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.current_map[y][x] == WALL

    def is_valid_move(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.current_map[y][x] != WALL

    def collect_pellet(self, x, y):
        tile = self.current_map[y][x]
        if tile == PELLET:
            self.current_map[y][x] = EMPTY
            self.pellets_remaining -= 1
            return PELLET_SCORE
        elif tile == POWER_PELLET:
            self.current_map[y][x] = EMPTY
            self.pellets_remaining -= 1
            return POWER_PELLET_SCORE
        return 0

    def render(self, screen):
        for y, row in enumerate(self.current_map):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == WALL:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                elif tile == PELLET:
                    pygame.draw.circle(screen, PELLET_COLOR, rect.center, 2)
                elif tile == POWER_PELLET:
                    pygame.draw.circle(screen, POWER_PELLET_COLOR, rect.center, 6)

    def get_valid_adjacent_tiles(self, x, y):
        """주어진 좌표에서 이동 가능한 인접 타일의 좌표 목록을 반환합니다."""
        valid_tiles = []
        for dx, dy in DIRECTIONS.values():
            next_x, next_y = x + dx, y + dy
            # 맵 범위 내에 있고 벽이 아닌지 확인
            if 0 <= next_y < len(self.current_map) and 0 <= next_x < len(self.current_map[0]) and self.current_map[next_y][next_x] != WALL:
                valid_tiles.append((next_x, next_y))
        return valid_tiles

    def get_spawn_positions(self):
        return {
            'player': self.player_spawn_point,
            'ghosts': self.ghost_spawn_points
        }

    def all_pellets_collected(self):
        """모든 펠릿이 수집되었는지 확인합니다."""
        return self.pellets_remaining == 0