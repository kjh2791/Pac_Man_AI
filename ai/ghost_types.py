import pygame
from ai.pathfinding import a_star
from game.constants import *
import os
import time

class Ghost:
    def __init__(self, x, y, color, learning_system):
        self.init_x, self.init_y = x, y
        self.x, self.y = x, y
        self.color = color
        self.learning = learning_system
        self.state = "chase"
        self.path = []
        self.behavior_tree = None
        self.speed = 0.22  # 고스트 이동 딜레이(초)
        self.last_move_time = time.time()
        self.respawn_delay = 0.5 # 리스폰 후 움직이기까지 대기 시간(초)
        self.respawn_time = 0 # 리스폰 시간 기록
        self.post_respawn_chase_duration = 2.0 # 리스폰 대기 후 플레이어 파워업과 관계없이 chase 상태 유지 시간(초)
        self.post_respawn_end_time = 0 # post_respawn_chase 상태가 끝나는 시간
        self.frightened_speed_multiplier = 0.5 # 파워펠릿 상태 시 속도 배율 (느려짐)
        # 이미지 로딩
        self.ghost_imgs = {
            RED: pygame.image.load(os.path.join('assets', 'sprites', 'ghost_red.png')).convert_alpha(),
            PINK: pygame.image.load(os.path.join('assets', 'sprites', 'ghost_pink.png')).convert_alpha(),
            CYAN: pygame.image.load(os.path.join('assets', 'sprites', 'ghost_cyan.png')).convert_alpha(),
            ORANGE: pygame.image.load(os.path.join('assets', 'sprites', 'ghost_orange.png')).convert_alpha(),
            'frightened': pygame.image.load(os.path.join('assets', 'sprites', 'ghost_frightened.png')).convert_alpha()
        }
        # Behavior Tree는 사용하지 않음
        self.behavior_tree = None

    def update(self, player_pos, game_map, other_ghosts, player=None):
        current_time = time.time()
        # 리스폰 대기 중이면 움직임 및 상태 업데이트를 건너뛰기
        if current_time - self.respawn_time < self.respawn_delay:
            return

        # 플레이어와 고스트 간의 거리 계산 (맨해튼 거리)
        distance_to_player = abs(self.x - player_pos[0]) + abs(self.y - player_pos[1])

        # 리스폰 대기 시간은 끝났지만 post_respawn_chase_duration 시간 동안은 강제로 chase 상태 유지
        # 이 시간 동안은 플레이어 파워업 상태와 관계없이 chase 상태입니다.
        if current_time < self.post_respawn_end_time:
             self.state = 'chase'
             current_speed = self.speed # 일반 속도
             # 리스폰 직후에는 플레이어 현재 위치 추격
             target_pos = player_pos 

        else:
            # post_respawn_chase_duration 시간이 끝난 후에는 플레이어 파워업 상태에 따라 상태 전환 및 움직임 결정
            # NOTE: player 객체가 None이 아닐 때만 player 상태를 확인합니다.
            if player and player.is_powered_up():
                # 플레이어가 파워업 상태이면 모든 고스트는 frightened 상태가 됩니다.
                self.state = 'frightened'
                current_speed = self.speed / self.frightened_speed_multiplier # frightened 상태시 더 느리게
                # 파워펠릿 상태일 때는 플레이어로부터 멀어지는 방향으로 이동 (가장 먼 인접 타일 선택)
                valid_adjacent_tiles = game_map.get_valid_adjacent_tiles(self.x, self.y)
                best_move = None
                max_dist = -1
                current_dist = abs(self.x - player_pos[0]) + abs(self.y - player_pos[1])
                max_dist = current_dist

                for next_tile in valid_adjacent_tiles:
                     next_x, next_y = next_tile
                     dist_from_player = abs(next_x - player_pos[0]) + abs(next_y - player_pos[1])
                     if dist_from_player > max_dist:
                          max_dist = dist_from_player
                          best_move = (next_x, next_y)
                if best_move:
                     self.path = [best_move] # 도망 방향으로 1칸 이동
                else:
                     self.path = [] # 이동 가능한 방향이 없으면 멈춤

            else:
                 # 플레이어가 파워업 상태가 아니거나 player 객체가 없으면 frightened 상태에서 벗어납니다.
                 if self.state == 'frightened':
                     self.state = 'chase' # frightened 상태였다면 chase로 복귀

                 self.state = 'chase' # 플레이어 파워업 상태가 아니면 chase 상태
                 current_speed = self.speed # 일반 속도
                 
                 # ----- 고스트 타입별 기본 타겟 설정 로직 (일반 chase 상태일 때) -----
                 # 각 고스트 타입의 get_chase_target 메소드를 호출하여 기본 타겟을 가져옵니다.
                 target_pos = self.get_chase_target(player_pos, game_map, other_ghosts, player)
                 # -------------------------------------------------------

                 # 거리 기반 학습 예측 활용 또는 기본 타겟 추격
                 # 학습 단계 0부터, 8타일 이내 가까운 거리에서 학습 예측 사용
                 distance_to_player = abs(self.x - player_pos[0]) + abs(self.y - player_pos[1]) # 플레이어와 고스트 간의 거리 계산
                 if self.learning and self.learning.learning_phase >= 0 and distance_to_player < 8:
                      # 가까우면 학습 예측 위치를 최종 타겟으로 사용
                      pred = self.learning.get_prediction((self.x, self.y), [g for g in other_ghosts if g != self])
                      if pred != (self.x, self.y) and game_map.is_valid_move(pred[0], pred[1]):
                           final_target = pred
                           # TODO: 고스트 타입별로 예측 위치 활용 방식을 다르게 적용
                           pass # 현재는 예측 위치를 바로 final_target으로 사용
                      else:
                           # 예측 실패 또는 유효하지 않은 예측 시 기본 타겟 사용
                           final_target = target_pos # get_chase_target 결과 사용
                 else: # 멀리 있을 때 또는 학습 단계 낮을 때: 기본 타겟 추격
                      final_target = target_pos # get_chase_target 결과 사용

                 # 최종 타겟으로 A* 경로 탐색
                 # 최종 타겟이 현재 위치와 같으면 A* 호출 방지 (경로 항상 비어있음)
                 if final_target != (self.x, self.y):
                     # a_star 함수 호출 결과를 self.path에 할당
                     # 혹시 a_star가 예상치 못한 값을 반환할 경우를 대비하여 할당 전 검사 또는 할당 후 검사 필요
                     # 현재 a_star는 빈 리스트 [] 또는 타일 튜플의 리스트 [(x1, y1), (x2, y2), ...]를 반환한다고 가정
                     calculated_path = a_star((self.x, self.y), final_target, game_map.current_map)
                     # 계산된 경로가 유효한 리스트인지 확인
                     if isinstance(calculated_path, list):
                          self.path = calculated_path
                     else:
                          # 예상치 못한 타입이 할당된 경우 경로를 비웁니다.
                          print(f"Warning: a_star returned unexpected type {type(calculated_path)} for target {final_target}. Path cleared.")
                          self.path = []
                 else:
                      self.path = []

        # 이동 처리: 결정된 path의 첫 번째 칸으로 이동
        # post_respawn_chase 상태에서도 이 이동 로직을 사용합니다.
        if current_time - self.last_move_time >= current_speed: # 조정된 속도 적용
            # self.path가 리스트이고 비어있지 않은지 다시 확인
            if isinstance(self.path, list) and self.path:
                next_tile = self.path[0]
                # 다음 타일에 다른 고스트가 있는지 확인하여 겹침 방지 및 실시간 회피
                can_move_to_next_tile = True
                for other in other_ghosts:
                    # 이동하려는 타일에 이미 다른 고스트가 서 있거나
                    # 다른 고스트의 다음 목표 타일이 나와 같다면 이동하지 않음 (단순화된 회피)
                    if other != self and (
                        (other.x, other.y) == next_tile or 
                        (other.path and len(other.path) > 0 and other.path[0] == next_tile)
                       ):
                        can_move_to_next_tile = False
                        break

                if can_move_to_next_tile:
                    self.x, self.y = self.path.pop(0) # 경로의 다음 칸으로 이동
                    # TODO: path 길이가 1 이상일 때 부드러운 이동 처리 (픽셀 단위 이동)
                # else: 다음 타일에 다른 고스트가 있거나 다음 목표 타일이 같으면 이동하지 않고 멈춤 (실시간 회피)
                else:
                    # 원래 목표 타일로 이동할 수 없을 경우 다른 유효한 인접 타일로 이동 시도
                    valid_alternatives = game_map.get_valid_adjacent_tiles(self.x, self.y)
                    
                    # 원래 목표 타일 제외
                    if next_tile in valid_alternatives:
                         valid_alternatives.remove(next_tile)

                    # 다른 고스트가 현재 서 있는 타일 제외
                    current_ghost_positions = [(g.x, g.y) for g in other_ghosts if g != self]
                    valid_alternatives = [tile for tile in valid_alternatives if tile not in current_ghost_positions]
                    
                    # 대안 경로가 있다면 그 중 하나로 이동
                    if valid_alternatives:
                        # 간단하게 첫 번째 유효한 대안 타일로 이동
                        # TODO: A* 경로와 일치하는 대안 타일을 우선 선택하는 등 로직 개선 가능
                        chosen_alternative = valid_alternatives[0]
                        self.x, self.y = chosen_alternative
                        # 대안 경로로 이동했으므로 현재 경로(self.path)는 재계산이 필요할 수 있으나,
                        # 다음 업데이트 주기에서 새로운 경로를 찾을 것이므로 여기서는 그대로 둡니다.
                        # self.path = [] # 또는 경로를 비우는 것도 고려 가능
                    # else: 대안 경로도 없으면 현재 위치에 머뭄 (이전과 동일하게 멈춤)
            # else: pathfinding 실패 또는 이동 가능한 방향 없으면 현재 위치 유지 (멈춤)
            self.last_move_time = current_time

    def render(self, screen):
        center_x = self.x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.y * TILE_SIZE + TILE_SIZE // 2
        # 리스폰 대기 중이거나 frightened 상태일 때 이미지를 다르게 표시
        # 리스폰 대기 중에는 투명하게 또는 다르게 표시 가능
        if time.time() - self.respawn_time < self.respawn_delay:
             # 리스폰 중에는 안 보이게 처리 (또는 다른 이미지/알파 값 적용)
             return

        if self.state == 'frightened':
            img = self.ghost_imgs['frightened']
        else:
            img = self.ghost_imgs.get(self.color, self.ghost_imgs[RED])
        rect = img.get_rect(center=(center_x, center_y))
        screen.blit(img, rect)

    def reset(self):
        self.x, self.y = self.init_x, self.init_y
        self.state = "chase" # 리셋되면 기본 chase 상태
        self.path = []
        self.last_move_time = time.time()
        self.respawn_time = time.time() # 리스폰 시간 기록 (리셋 시 바로 리스폰 대기 시작)
        self.post_respawn_end_time = self.respawn_time + self.respawn_delay + self.post_respawn_chase_duration # 리스폰 대기 + 추가 chase 시간 설정
        # Behavior Tree는 사용하지 않으므로 관련 코드 제거 또는 주석 처리
        self.behavior_tree = None # Behavior Tree 사용 안 함

    def get_chase_target(self, player_pos, game_map, other_ghosts, player=None):
        """일반 chase 상태일 때 고스트 타입별 기본 타겟 위치를 결정합니다."""
        # 기본적으로 플레이어 현재 위치를 타겟으로 합니다.
        return player_pos

    def get_pos(self):
        """고스트의 현재 타일 위치를 반환합니다."""
        return (self.x, self.y)

class AggressiveGhost(Ghost):
    def get_chase_target(self, player_pos, game_map, other_ghosts, player=None):
        # AggressiveGhost: 플레이어 현재 위치를 기본 타겟으로 합니다.
        return player_pos

class AmbushGhost(Ghost):
    def get_chase_target(self, player_pos, game_map, other_ghosts, player=None):
        # AmbushGhost: 플레이어 진행 방향 2칸 앞 (단순화). 플레이어 방향 정보가 필요합니다.
        # 플레이어 객체에서 방향 정보를 가져온다고 가정합니다.
        # 실제 구현에서는 Player 클래스에 get_direction() 등의 메소드가 필요합니다.

        # 플레이어 방향 정보를 얻기 어렵거나 플레이어 객체가 None이면 플레이어 현재 위치 반환
        if not player or not hasattr(player, 'direction'):
             return player_pos
             
        dx, dy = DIRECTIONS.get(player.direction, (0, 0)) # 플레이어 방향의 dx, dy
        # 플레이어 현재 위치에서 2칸 앞 타일 계산
        target_x = player_pos[0] + dx * 2
        target_y = player_pos[1] + dy * 2

        # 계산된 타겟 위치가 맵 범위 내에 있고 벽이 아닌 유효한 타일인지 확인
        if 0 <= target_y < game_map.height and 0 <= target_x < game_map.width and not game_map.is_wall(target_x, target_y):
             return (target_x, target_y)

        # 유효하지 않으면 플레이어 현재 위치 반환
        return player_pos

class CooperativeGhost(Ghost):
    def get_chase_target(self, player_pos, game_map, other_ghosts, player=None):
        # CooperativeGhost: 다른 고스트들과 협력하여 플레이어를 포위 (구현 복잡)
        # 간단히, 모든 고스트들의 현재 위치 평균 + 플레이어 위치를 고려한 지점 (예시)
        # 또는 플레이어와 가장 먼 고스트의 위치를 타겟으로 하여 플레이어를 몰아가는 느낌 구현

        # 임시: 플레이어 위치 기준 오프셋 + 다른 고스트 위치 고려 (매우 간단화)
        # 다른 고스트들의 위치 평균을 계산 (자신 제외)
        avg_x, avg_y, count = 0, 0, 0
        for other in other_ghosts:
            if other != self:
                avg_x += other.x
                avg_y += other.y
                count += 1

        if count > 0:
            avg_x /= count
            avg_y /= count

            # 플레이어 위치와 다른 고스트 평균 위치를 고려한 타겟 (단순 예시: 평균과 플레이어 위치의 중간 + 오프셋)
            target_x = int((player_pos[0] + avg_x) / 2.0) + 1 # 예시 오프셋
            target_y = int((player_pos[1] + avg_y) / 2.0) + 1 # 예시 오프셋
        else:
            # 다른 고스트가 없으면 플레이어 위치 기준 오프셋
            target_x = player_pos[0] - 2 # 예시 오프셋
            target_y = player_pos[1] - 2 # 예시 오프셋

        # 계산된 타겟 위치가 맵 범위 내에 있고 벽이 아닌 유효한 타일인지 확인
        if 0 <= target_y < game_map.height and 0 <= target_x < game_map.width and not game_map.is_wall(target_x, target_y):
             return (target_x, target_y)

        # 유효하지 않으면 플레이어 현재 위치 반환
        return player_pos

class PredictiveGhost(Ghost):
    def get_chase_target(self, player_pos, game_map, other_ghosts, player=None):
        # PredictiveGhost: 학습 예측 로직은 Ghost.update에서 이미 처리되므로,
        # 여기서는 기본 추격 타겟으로 플레이어 현재 위치를 반환합니다.
        # update 함수 내에서 이 기본 타겟과 학습 예측 결과를 조합하여 최종 타겟을 결정합니다.
        return player_pos

def create_ghosts(learning_system, map_manager):
    # map_manager에서 고스트 스폰 위치를 가져옴
    spawn_positions = map_manager.get_spawn_positions().get('ghosts', [])
    # 스폰 위치가 4개 미만이면 기본값 추가 (혹시 맵 파일에 스폰 위치가 부족할 경우 대비)
    while len(spawn_positions) < 4:
         # 적절한 기본 스폰 위치 추가 (예시: 맵 중앙 부근)
         # 기본 맵 중앙 (21x20 맵 기준) 10, 10 근처에 배치
         base_x, base_y = 10, 10
         # 이미 있는 스폰 위치와 겹치지 않도록 조정
         new_pos = (base_x + 2 * (len(spawn_positions) % 2), base_y + 2 * (len(spawn_positions) // 2))
         if new_pos not in spawn_positions:
              spawn_positions.append(new_pos)
              print(f"Warning: Not enough ghost spawn points in map. Added default spawn point: {new_pos}") # 로그 추가
         elif len(spawn_positions) < 10: # 무한 루프 방지를 위해 최대 10개 기본 위치 시도
              # 이미 있으면 다른 위치 시도
              new_pos = (base_x + 2 * (len(spawn_positions) % 3), base_y + 2 * (len(spawn_positions) // 3) + 1)
              if new_pos not in spawn_positions:
                   spawn_positions.append(new_pos)
                   print(f"Warning: Not enough ghost spawn points in map. Added alternative default spawn point: {new_pos}") # 로그 추가

    ghosts = [
        AggressiveGhost(*spawn_positions[0], RED, learning_system),
        AmbushGhost(*spawn_positions[1], PINK, learning_system),
        CooperativeGhost(*spawn_positions[2], CYAN, learning_system),
        PredictiveGhost(*spawn_positions[3], ORANGE, learning_system),
    ]
    # Behavior Tree는 사용하지 않으므로 관련 코드 제거 또는 주석 처리
    # try:
    #     pass # Behavior Tree 사용 안 함
    # except ImportError:
    #     pass

    return ghosts
