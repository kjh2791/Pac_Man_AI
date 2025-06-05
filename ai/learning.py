from collections import deque, defaultdict
import pygame
import time
from game.constants import *
import json # json 모듈 추가
# from game.map_manager import MapManager # 순환 참조 방지

class PlayerLearningSystem:
    def __init__(self):
        self.reset_learning_data() # 초기화 함수 호출

    def reset_learning_data(self):
        """매 게임 시작 시 학습 데이터를 초기 상태로 리셋합니다. 초기 학습 데이터를 포함시킬 수 있습니다."""
        # 저장된 학습 데이터 파일 경로
        save_file = 'learning_data.json'

        # 저장된 데이터 로드 시도
        if self.load_learning_data(save_file):
            print(f"학습 데이터를 '{save_file}'에서 불러왔습니다.")
            # 로드 성공 시 추가 초기화 없이 바로 시작
            # learning_phase 등은 로드된 데이터에 포함됩니다.
            return

        # 로드 실패 또는 파일이 없을 경우 기본 초기화
        print("저장된 학습 데이터 파일을 찾을 수 없거나 로드에 실패하여 기본 학습 데이터로 시작합니다.")
        self.move_count = 0
        # 게임 시작 시 학습 단계 1부터 시작하여 초기 학습 효과를 부여
        self.learning_phase = 1 
        self.move_history = []
        self.corner_count = 0
        self.power_pellet_timing = [] # 파워 펠릿 획득 시점 기록 (타임스탬프 또는 이전 펠릿/파워펠릿 획득까지의 시간)
        self.score_milestones = [] # 특정 점수 도달 시간 기록

        # 학습 단계 변화 기준 (이동 횟수 기준)
        # 이 값은 초기화 시 변경되지 않고 고정됩니다.
        self.LEARNING_PHASE_THRESHOLDS = [0, 5, 15, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000] # 학습 단계 대폭 확장

        # 초기 학습 데이터 추가 (선택 사항)
        # 몇 가지 더미 이동 데이터를 추가하여 초기 예측에 영향을 줍니다.
        # 예시: 오른쪽으로 몇 번 이동하는 패턴 추가
        initial_moves = [
            {'prev_pos': (1, 1), 'current_pos': (2, 1), 'move_data': {'direction': 'RIGHT'}},
            {'prev_pos': (2, 1), 'current_pos': (3, 1), 'move_data': {'direction': 'RIGHT'}},
            {'prev_pos': (3, 1), 'current_pos': (4, 1), 'move_data': {'direction': 'RIGHT', 'is_corner': True}},
            {'prev_pos': (4, 1), 'current_pos': (4, 2), 'move_data': {'direction': 'DOWN'}},
        ]
        self.move_history.extend(initial_moves)
        self.move_count += len(initial_moves) # 초기 이동 횟수 반영
        # 초기 데이터에 따라 learning_phase를 다시 계산할 수도 있지만, 여기서는 1로 고정했습니다.

    def analyze_player_move(self, prev_pos, current_pos, move_data, ghost_positions=None):
        self.move_count += 1
        
        # 플레이어 현재 위치 주변 고스트 밀집도 계산
        nearby_ghost_count = 0
        if ghost_positions:
            for ghost_pos in ghost_positions:
                # 맨해튼 거리로 2타일 반경 내 고스트 카운트
                distance = abs(current_pos[0] - ghost_pos[0]) + abs(current_pos[1] - ghost_pos[1])
                if distance <= 2:
                    nearby_ghost_count += 1

        # 이동 데이터에 고스트 밀집도 정보 추가
        move_record = {
            'prev_pos': prev_pos,
            'current_pos': current_pos,
            'move_data': move_data,
            'nearby_ghosts': nearby_ghost_count # 밀집도 정보 추가
        }

        self.move_history.append(move_record)

        # 코너링 습관 기록
        if move_data.get('is_corner'):
            self.corner_count += 1
        # 점수 우선순위(펠릿, 파워펠릿 등)
        self.score_milestones.append((self.move_count, move_data.get('score', 0)))
        # phase 자동 조정
        for i, threshold in enumerate(self.LEARNING_PHASE_THRESHOLDS):
            if self.move_count >= threshold:
                self.learning_phase = i

    def get_prediction(self, current_pos, ghost_positions):
        # phase에 따라 예측 방식 다르게
        if self.learning_phase == 0:
            # 가장 많이 이동한 방향 (고스트 밀집도 고려)
            moves = []
            move_scores = defaultdict(float)
            for move in self.move_history:
                if move['prev_pos'] == current_pos:
                    next_pos = move['current_pos']
                    # 고스트 밀집도가 2 이상인 경우 해당 이동 패턴에 낮은 점수 부여
                    score_multiplier = 1.0
                    if move.get('nearby_ghosts', 0) >= 2:
                        score_multiplier = 0.2 # 밀집 지역 회피 학습 가중치 낮춤
                    move_scores[next_pos] += 1.0 * score_multiplier # 횟수에 score_multiplier 반영

            if move_scores:
                # 점수가 가장 높은 타일 반환
                return max(move_scores, key=move_scores.get)
            return current_pos
        elif self.learning_phase == 1:
            # 코너링 선호 반영 (고스트 밀집도 고려)
            corner_moves = []
            corner_move_scores = defaultdict(float)
            for move in self.move_history:
                if move['prev_pos'] == current_pos and move['move_data'].get('is_corner'):
                    next_pos = move['current_pos']
                    # 고스트 밀집도가 2 이상인 경우 해당 코너링 패턴에 낮은 점수 부여
                    score_multiplier = 1.0
                    if move.get('nearby_ghosts', 0) >= 2:
                        score_multiplier = 0.2
                    corner_move_scores[next_pos] += 1.0 * score_multiplier

            if corner_move_scores:
                # 점수가 가장 높은 코너링 타일 반환
                return max(corner_move_scores, key=corner_move_scores.get)
            return current_pos
        elif self.learning_phase >= 2:
            # 최근 이동 경로 기반 예측 (패턴 인식) - 여기서는 밀집도 직접 반영은 복잡
            # 간단하게, 최근 이동이 고스트 밀집 지역 회피였다면 그 방향 선호
            if self.move_history:
                last_move = self.move_history[-1]
                if last_move.get('nearby_ghosts', 0) >= 2: # 최근 이동이 밀집 지역 회피였다면
                    # 회피 방향 예측 강화 (단순화: 최근 이동 방향 반대 또는 인접 타일 중 가장 먼 곳)
                    # 여기서는 간단히 마지막 이동 위치 반환 (AI가 A*로 회피 경로 찾도록) - TODO 개선 필요
                    return last_move['current_pos']
                else:
                    # 일반적인 최근 이동 위치 예측
                    return last_move['current_pos']
            return current_pos
        return current_pos

    def save_learning_data(self, filepath):
        """현재 학습 데이터를 지정된 파일에 JSON 형식으로 저장합니다."""
        data = {
            'move_count': self.move_count,
            'learning_phase': self.learning_phase,
            'move_history': self.move_history,
            'corner_count': self.corner_count,
            'power_pellet_timing': self.power_pellet_timing,
            'score_milestones': self.score_milestones,
            # LEARNING_PHASE_THRESHOLDS는 고정 값이므로 저장/로드가 필수는 아니지만 일관성을 위해 포함
            'LEARNING_PHASE_THRESHOLDS': self.LEARNING_PHASE_THRESHOLDS
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"학습 데이터를 '{filepath}'에 성공적으로 저장했습니다.")
            return True
        except Exception as e:
            print(f"학습 데이터 저장 중 오류 발생: {e}")
            return False

    def load_learning_data(self, filepath):
        """지정된 파일에서 학습 데이터를 불러옵니다. 성공 시 True, 실패 시 False 반환."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 불러온 데이터로 객체 상태 업데이트
            self.move_count = data.get('move_count', 0)
            self.learning_phase = data.get('learning_phase', 0)
            self.move_history = data.get('move_history', [])
            self.corner_count = data.get('corner_count', 0)
            self.power_pellet_timing = data.get('power_pellet_timing', [])
            self.score_milestones = data.get('score_milestones', [])
            # THRESHOLDS는 기본값을 유지하거나 로드된 값 사용 (여기서는 로드된 값 사용)
            self.LEARNING_PHASE_THRESHOLDS = data.get('LEARNING_PHASE_THRESHOLDS', [0, 20, 50, 100, 200]) # 기본값은 기존값으로 설정

            # 로드된 데이터 기반으로 learning_phase 재계산 (선택 사항)
            # 현재는 로드된 learning_phase를 그대로 사용합니다.
            # self.update_learning_phase() # 필요하다면 이런 함수 호출

            return True
        except FileNotFoundError:
            # 파일이 없는 것은 정상적인 경우이므로 오류 메시지 출력 안 함
            return False
        except Exception as e:
            print(f"학습 데이터 로드 중 오류 발생: {e}")
            return False

    # learning_phase를 move_count 기반으로 업데이트하는 헬퍼 함수 (필요 시 사용)
    def update_learning_phase(self):
         for i, threshold in enumerate(self.LEARNING_PHASE_THRESHOLDS):
              if self.move_count >= threshold:
                   self.learning_phase = i