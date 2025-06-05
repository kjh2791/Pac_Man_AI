# collision.py - 충돌 감지 시스템

import math
from game.constants import *

class CollisionDetector:
    def __init__(self, map_manager):
        self.map_manager = map_manager
    
    def check_wall_collision(self, x, y):
        """벽 충돌 확인"""
        # 픽셀 좌표를 타일 좌표로 변환
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        return self.map_manager.is_wall(tile_x, tile_y)
    
    def can_move_to(self, x, y):
        """해당 위치로 이동 가능한지 확인"""
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        return self.map_manager.is_valid_move(tile_x, tile_y)
    
    def get_tile_center(self, tile_x, tile_y):
        """타일의 중심 픽셀 좌표 반환"""
        center_x = tile_x * TILE_SIZE + TILE_SIZE // 2
        center_y = tile_y * TILE_SIZE + TILE_SIZE // 2
        return center_x, center_y
    
    def pixel_to_tile(self, x, y):
        """픽셀 좌표를 타일 좌표로 변환"""
        return int(x // TILE_SIZE), int(y // TILE_SIZE)
    
    def tile_to_pixel(self, tile_x, tile_y):
        """타일 좌표를 픽셀 좌표로 변환 (중심점)"""
        return self.get_tile_center(tile_x, tile_y)
    
    def is_aligned_with_tile(self, x, y, threshold=2):
        """픽셀 위치가 타일 중심과 정렬되어 있는지 확인"""
        tile_x, tile_y = self.pixel_to_tile(x, y)
        center_x, center_y = self.get_tile_center(tile_x, tile_y)
        
        return (abs(x - center_x) <= threshold and 
                abs(y - center_y) <= threshold)
    
    def get_distance(self, pos1, pos2):
        """두 위치 간의 유클리드 거리 계산"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def check_entity_collision(self, entity1_pos, entity2_pos, collision_radius=TILE_SIZE//2):
        """두 엔티티 간의 충돌 확인"""
        distance = self.get_distance(entity1_pos, entity2_pos)
        return distance <= collision_radius
    
    def check_pellet_collection(self, player_pos):
        """펠릿 수집 확인"""
        tile_x, tile_y = self.pixel_to_tile(player_pos[0], player_pos[1])
        
        # 플레이어가 타일 중심에 충분히 가까운 경우에만 수집
        if self.is_aligned_with_tile(player_pos[0], player_pos[1], threshold=5):
            return self.map_manager.collect_pellet(tile_x, tile_y)
        
        return None
    
    def get_valid_moves_from_position(self, x, y):
        """현재 위치에서 이동 가능한 방향들 반환"""
        tile_x, tile_y = self.pixel_to_tile(x, y)
        valid_moves = []
        
        for direction, (dx, dy) in DIRECTIONS.items():
            next_tile_x = tile_x + dx
            next_tile_y = tile_y + dy
            
            if self.map_manager.is_valid_move(next_tile_x, next_tile_y):
                valid_moves.append(direction)
        
        return valid_moves
    
    def snap_to_tile_center(self, x, y):
        """위치를 가장 가까운 타일 중심으로 스냅"""
        tile_x, tile_y = self.pixel_to_tile(x, y)
        return self.get_tile_center(tile_x, tile_y)
    
    def is_at_intersection(self, x, y):
        """현재 위치가 교차로인지 확인"""
        tile_x, tile_y = self.pixel_to_tile(x, y)
        return self.map_manager.is_intersection(tile_x, tile_y)
    
    def can_change_direction(self, current_pos, current_direction, new_direction):
        """현재 위치에서 방향 전환이 가능한지 확인"""
        x, y = current_pos
        
        # 현재 위치가 타일 중심에 정렬되어 있는지 확인
        if not self.is_aligned_with_tile(x, y, threshold=3):
            return False
        
        # 새로운 방향으로 이동 가능한지 확인
        tile_x, tile_y = self.pixel_to_tile(x, y)
        dx, dy = DIRECTIONS[new_direction]
        next_tile_x = tile_x + dx
        next_tile_y = tile_y + dy
        
        return self.map_manager.is_valid_move(next_tile_x, next_tile_y)
    
    def get_next_position(self, current_pos, direction, speed):
        """다음 위치 계산"""
        x, y = current_pos
        dx, dy = DIRECTIONS[direction]
        
        next_x = x + dx * speed
        next_y = y + dy * speed
        
        # 벽 충돌 확인
        if self.can_move_to(next_x, next_y):
            return (next_x, next_y)
        else:
            # 벽에 부딪히면 현재 위치를 타일 중심으로 스냅
            return self.snap_to_tile_center(x, y)
    
    def handle_tunnel_teleport(self, x, y):
        """터널 순간이동 처리 (맵 가장자리)"""
        # 왼쪽 가장자리에서 오른쪽으로
        if x < 0:
            return (self.map_manager.width * TILE_SIZE - TILE)