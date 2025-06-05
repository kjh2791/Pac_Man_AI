import pygame
from game.constants import *
from game.map_manager import MapManager
from game.player import Player
from ai.ghost_ai import GhostManager
from ai.learning import PlayerLearningSystem
import time
from game.collision import CollisionDetector

class GameEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = FPS
        self.paused = False
        self.pause_time = 0

        # 게임 구성요소 초기화
        self.map_manager = MapManager()
        self.learning_system = PlayerLearningSystem()
        self.player = Player(self.map_manager.player_start_x, self.map_manager.player_start_y, self.learning_system)
        self.ghosts = GhostManager(self.learning_system, self.map_manager)
        self.score = 0
        self.map_manager.player = self.player
        self.collision_detector = CollisionDetector(self.map_manager)

    def initialize_new_game(self):
        # 학습 데이터 및 게임 상태 초기화
        self.learning_system.reset_learning_data()
        self.map_manager.reset()
        self.player.reset(self.map_manager.player_start_x, self.map_manager.player_start_y)
        self.ghosts.reset()
        self.map_manager.player = self.player
        self.score = 0
        self.collision_detector = CollisionDetector(self.map_manager)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # 키 입력 처리
            self.player.handle_event(event)

    def update(self):
        if self.paused:
            # 일시정지 중이면 update 건너뜀
            if time.time() - self.pause_time >= 1.0:
                self.paused = False
            else:
                return
        # 플레이어 이동 및 충돌 처리
        self.player.update(self.map_manager, [g.get_pos() for g in self.ghosts.ghosts])
        self.ghosts.update(self.player.get_pos(), self.map_manager, self.ghosts.ghosts, self.player)

        # 고스트와 충돌 체크 (거리 기반)
        player_pixel_pos = (self.player.x * TILE_SIZE + TILE_SIZE // 2, self.player.y * TILE_SIZE + TILE_SIZE // 2)
        collision_radius = TILE_SIZE // 2 # 충돌 반경을 타일 크기의 절반으로 설정

        for ghost in self.ghosts.ghosts:
            # 리스폰 대기 중인 고스트는 충돌 처리하지 않음
            if time.time() - ghost.respawn_time < ghost.respawn_delay:
                continue

            ghost_pixel_pos = (ghost.x * TILE_SIZE + TILE_SIZE // 2, ghost.y * TILE_SIZE + TILE_SIZE // 2)
            
            # 두 엔티티 간의 거리 계산
            distance = self.collision_detector.get_distance(player_pixel_pos, ghost_pixel_pos)

            # 충돌 감지
            if distance < collision_radius:
                # 충돌한 고스트의 현재 상태를 확인
                if hasattr(ghost, 'state') and ghost.state == 'frightened':
                    # 파워펠릿 상태에서 고스트 잡음
                    self.player.score += GHOST_BASE_SCORE # 고스트 잡은 점수 추가
                    print(f"Ghost {ghost.color} eaten. Score: {self.player.score}") # 로그 추가
                    ghost.reset() # 고스트 리스폰
                    # TODO: 고스트 잡는 애니메이션/효과음 추가
                else:
                    # 일반 상태에서 고스트와 충돌 -> 플레이어 사망
                    print(f"Player hit by ghost {ghost.color} (State: {getattr(ghost, 'state', 'N/A')}). Lives: {self.player.lives-1}") # 로그 추가
                    died = self.player.lose_life()
                    self.paused = True
                    self.pause_time = time.time()
                    if died:
                        self.running = False # 게임 오버
                    self.ghosts.reset()  # 플레이어가 죽으면 모든 고스트 리셋
                    return # 플레이어 죽음 처리 후 업데이트 중단

        # 모든 펠릿을 다 먹었는지 확인하고 게임 종료
        if self.map_manager.all_pellets_collected():
            print("All pellets collected! Game Over.") # 로그 추가
            self.running = False # 게임 종료

    def render(self):
        self.screen.fill(BLACK)
        self.map_manager.render(self.screen)
        self.player.render(self.screen)
        self.ghosts.render(self.screen)
        # 점수 표시
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # 학습 단계(Learning Phase) 표시
        if self.learning_system:
            phase_font = pygame.font.SysFont(None, 36)
            phase = self.learning_system.learning_phase
            phase_text = phase_font.render(f"Phase: {phase}", True, WHITE)
            # 점수 텍스트 아래에 표시 (예: Y 좌표 + 40)
            self.screen.blit(phase_text, (10, 10 + score_text.get_height() + 5))

        pygame.display.flip()

    def game_loop(self):
        # 게임 시작 전 1초 대기
        self.render()
        pygame.display.flip()
        time.sleep(1)
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

        # 게임 루프 종료 후 최종 점수 표시 및 학습 데이터 저장
        self.show_final_score()

    def show_final_score(self):
        """게임 종료 시 최종 점수 화면을 표시합니다."""
        self.screen.fill(BLACK) # 화면을 검은색으로 채움
        font = pygame.font.SysFont(None, 72) # 더 큰 글꼴 사용
        # 최종 점수 텍스트 생성
        final_score_text = font.render(f"Final Score: {self.player.score}", True, WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, text_rect)

        # 게임 종료 메시지 추가 (선택 사항)
        end_message_font = pygame.font.SysFont(None, 48)
        end_message_text = end_message_font.render("Game Over! Press ESC to Quit", True, GRAY)
        end_message_rect = end_message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(end_message_text, end_message_rect)

        pygame.display.flip() # 화면 업데이트

        # 사용자가 종료할 때까지 대기
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 게임 종료 전 학습 데이터 저장
                    self.learning_system.save_learning_data('learning_data.json')
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # 게임 종료 전 학습 데이터 저장
                        self.learning_system.save_learning_data('learning_data.json')
                        pygame.quit()
                        quit()

# 게임 실행
if __name__ == "__main__":
    game_engine = GameEngine()
    game_engine.game_loop()
