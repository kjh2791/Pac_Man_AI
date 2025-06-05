import pygame
from game.game_engine import GameEngine

def main():
    """게임 메인 실행 함수"""
    try:
        # pygame 초기화
        pygame.init()
        pygame.mixer.init()
        
        # 게임 엔진 생성 및 실행
        engine = GameEngine()
        engine.game_loop()
        
    except Exception as e:
        print(f"게임 실행 중 오류 발생: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()