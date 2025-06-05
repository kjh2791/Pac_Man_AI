# behavior_tree.py - 행동 트리 기반 AI 시스템

class Node:
    """행동 트리의 기본 노드 클래스"""
    def run(self, *args, **kwargs):
        raise NotImplementedError

class Selector(Node):
    """자식 노드 중 하나라도 성공하면 성공 (OR)"""
    def __init__(self, children):
        self.children = children
    def run(self, *args, **kwargs):
        for child in self.children:
            if child.run(*args, **kwargs):
                return True
        return False

class Sequence(Node):
    """자식 노드 모두 성공해야 성공 (AND)"""
    def __init__(self, children):
        self.children = children
    def run(self, *args, **kwargs):
        for child in self.children:
            if not child.run(*args, **kwargs):
                return False
        return True

class Condition(Node):
    """조건 노드 (예: 플레이어가 가까운가?)"""
    def __init__(self, func):
        self.func = func
    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Action(Node):
    """행동 노드 (예: 추적, 도망 등)"""
    def __init__(self, func):
        self.func = func
    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

# 예시: 고스트 AI 행동 트리 생성 함수
def create_ghost_behavior_tree(ghost):
    # 조건: 플레이어가 가까우면 추적, 아니면 순찰
    def is_player_nearby(*args, **kwargs):
        player_pos = kwargs.get('player_pos')
        ghost_pos = (ghost.x, ghost.y)
        # 맨해튼 거리 5 이하
        return abs(player_pos[0] - ghost_pos[0]) + abs(player_pos[1] - ghost_pos[1]) <= 5
    
    def chase_player(*args, **kwargs):
        ghost.state = 'chase'
        return True
    
    def patrol(*args, **kwargs):
        ghost.state = 'scatter'
        return True
    
    return Selector([
        Sequence([
            Condition(is_player_nearby),
            Action(chase_player)
        ]),
        Action(patrol)
    ])

# 실제 사용 예시:
# ghost.behavior_tree = create_ghost_behavior_tree(ghost)
# ghost.behavior_tree.run(player_pos=player_pos)
