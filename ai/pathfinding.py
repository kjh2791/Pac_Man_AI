import heapq
import math
from collections import defaultdict

class PathFinder:
    def __init__(self, map_manager):
        self.map_manager = map_manager
        self.cache = {}  # 경로 캐시
        self.cache_max_size = 1000
    
    def heuristic(self, pos1, pos2):
        """휴리스틱 함수 - 맨하탄 거리"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, pos):
        """인접한 유효한 위치들 반환"""
        x, y = pos
        neighbors = []
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if self.map_manager.is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def a_star(self, start, goal, avoid_positions=None):
        """A* 알고리즘으로 최단 경로 찾기"""
        if avoid_positions is None:
            avoid_positions = set()
            
        # 캐시 확인
        cache_key = (start, goal, tuple(sorted(avoid_positions)))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if start == goal:
            return [start]
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = self.heuristic(start, goal)
        
        visited = set()
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current in visited:
                continue
                
            visited.add(current)
            
            if current == goal:
                # 경로 재구성
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                
                # 캐시에 저장
                if len(self.cache) < self.cache_max_size:
                    self.cache[cache_key] = path
                
                return path
            
            for neighbor in self.get_neighbors(current):
                if neighbor in visited or neighbor in avoid_positions:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # 경로를 찾을 수 없음
    
    def find_path_avoiding_ghosts(self, start, goal, ghost_positions, safety_radius=2):
        """고스트를 피해서 경로 찾기"""
        avoid_positions = set()
        
        for ghost_pos in ghost_positions:
            gx, gy = ghost_pos
            # 고스트 주변 안전 거리 내의 모든 위치를 피함
            for dx in range(-safety_radius, safety_radius + 1):
                for dy in range(-safety_radius, safety_radius + 1):
                    avoid_x, avoid_y = gx + dx, gy + dy
                    if self.map_manager.is_valid_position(avoid_x, avoid_y):
                        avoid_positions.add((avoid_x, avoid_y))
        
        return self.a_star(start, goal, avoid_positions)
    
    def find_escape_route(self, player_pos, ghost_positions, max_distance=10):
        """고스트들로부터 가장 멀리 도망갈 수 있는 경로 찾기"""
        best_pos = player_pos
        max_min_distance = 0
        
        # BFS로 일정 거리 내의 모든 위치 탐색
        queue = [(player_pos, 0)]
        visited = {player_pos}
        
        while queue:
            current_pos, distance = queue.pop(0)
            
            if distance >= max_distance:
                continue
            
            # 현재 위치에서 모든 고스트까지의 최소 거리 계산
            min_ghost_distance = min(
                self.heuristic(current_pos, ghost_pos) 
                for ghost_pos in ghost_positions
            )
            
            if min_ghost_distance > max_min_distance:
                max_min_distance = min_ghost_distance
                best_pos = current_pos
            
            # 인접 위치들을 큐에 추가
            for neighbor in self.get_neighbors(current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        
        return self.a_star(player_pos, best_pos)
    
    def find_pellet_path(self, start, pellet_positions, ghost_positions):
        """가장 안전한 펠릿으로의 경로 찾기"""
        best_pellet = None
        best_score = float('-inf')
        
        for pellet_pos in pellet_positions:
            # 펠릿까지의 거리
            distance_to_pellet = self.heuristic(start, pellet_pos)
            
            # 고스트들로부터의 안전도
            min_ghost_distance = min(
                self.heuristic(pellet_pos, ghost_pos) 
                for ghost_pos in ghost_positions
            ) if ghost_positions else 10
            
            # 점수 계산 (가깝고 안전한 펠릿이 높은 점수)
            score = min_ghost_distance - distance_to_pellet * 0.5
            
            if score > best_score:
                best_score = score
                best_pellet = pellet_pos
        
        if best_pellet:
            return self.a_star(start, best_pellet)
        return []
    
    def clear_cache(self):
        """경로 캐시 초기화"""
        self.cache.clear()
    
    def get_direction_to_next_position(self, current_pos, next_pos):
        """현재 위치에서 다음 위치로의 방향 반환"""
        if not next_pos:
            return None
            
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        if dx > 0:
            return 'RIGHT'
        elif dx < 0:
            return 'LEFT'
        elif dy > 0:
            return 'DOWN'
        elif dy < 0:
            return 'UP'
        
        return None

def a_star(start, goal, game_map):
    # A* 알고리즘 구현
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # 경로 복원
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        for neighbor in get_neighbors(current, game_map):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    return []

def get_neighbors(pos, game_map):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= ny < len(game_map) and 0 <= nx < len(game_map[0]) and game_map[ny][nx] != 1:
            neighbors.append((nx, ny))
    return neighbors

def heuristic(a, b):
    # 맨해튼 거리
    return abs(a[0]-b[0]) + abs(a[1]-b[1])