# Pac_Man_AI
This project is an implementation of an AI Pac-Man game. It is characterized by combining elements of artificial intelligence and a learning system with traditional Pac-Man gameplay.
Key Components and Features:
Pac-Man (Player): The character controlled by the player. Moves through the maze, eating pellets and power pellets.
Ghosts: Enemy characters that chase Pac-Man. There are multiple types of ghosts, each with a different basic chasing strategy.
Map: Manages the maze structure where Pac-Man and ghosts move, as well as the locations of items like pellets and power pellets.
Pellets and Power Pellets: When eaten by Pac-Man, they grant points or temporarily neutralize ghosts (frightened state), allowing Pac-Man to eat them.
Player Learning System: One of the core AI elements of this project.
It records the player's movement trajectory, cornering frequency, timing of specific actions (e.g., eating pellets), etc.
Based on this data, it learns the player's movement patterns and predicts the next movement location.
It is designed to adjust the learning phase based on the player's cumulative move count, which can alter the complexity or utilization method of the prediction.
Ghost AI: Ghosts do not simply follow a fixed path or blindly chase the player; they can utilize the results of the player
learning system's predictions.
Specifically, some ghosts near the player may attempt to move more strategically by using the 'player's next predicted location' from the player learning system as their chase target.
This means that as the game progresses and the player's learning data accumulates, the ghosts' movements can become more reactive to the player's actions or exhibit prediction-based movements.
Pathfinding: Ghosts use pathfinding techniques like the A* algorithm to find the optimal path from their current location to their target location. This process can include logic to avoid other ghosts or walls.
Project Goal:
This project aims to provide an interactive experience where the game's difficulty dynamically changes based on the player's skill level and the development of the learning system, rather than just a fixed AI. By introducing AI ghosts that utilize player behavior learning and prediction, the system learns the player's patterns as they play and incorporates that learning into the ghosts' behavior, creating a more challenging game environment.
