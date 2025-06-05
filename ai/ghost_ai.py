from ai.pathfinding import a_star
from ai.ghost_types import create_ghosts

class GhostManager:
    def __init__(self, learning_system, map_manager):
        self.learning_system = learning_system
        self.map_manager = map_manager
        self.ghosts = create_ghosts(learning_system, map_manager)

    def update(self, player_pos, map_manager, other_ghosts, player=None):
        for ghost in self.ghosts:
            ghost.update(player_pos, map_manager, other_ghosts, player)

    def render(self, screen):
        for ghost in self.ghosts:
            ghost.render(screen)

    def reset(self):
        for ghost in self.ghosts:
            ghost.reset()
