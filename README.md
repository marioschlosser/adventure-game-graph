# Adventure Game Graph Generator
Creates a puzzle and room graph for a text adventure game.

The game graph gets created randomly based on various configurable parameters.
- The graph consists of rooms and puzzles. It is an acyclic directed graph.
- Each node in the graph is either a puzzle, or a room. A puzzle is a text adventure action like "pick up apple" or "unlock door with key". A room is a text adventure room.
- Edges in the graph denote the flow of solving the game. Consider an edge pointing from node A to node B: If both nodes A and B are puzzles, this means that puzzle A needs to get solved before puzzle B becomes available. If node A is a room and node B is a puzzle, this means that puzzle B is located in room A. If node A is a puzzle and node B is a room, this means that solving puzzle A unlocks room B. Nodes A and B cannot both be rooms.
- The graph is created such that all puzzles need to get solved (i.e., all nodes need to get traversed) in order to reach the final node, where the game ends. Because the graph is acyclic, there can be no logical deadlocks (i.e., a puzzle cannot be on its own critical solution path).
- The player initially has access to a configurable number of rooms.
- Right now, the player can move freely between all unlocked rooms. (Need to add a map generator that imposes constraints on which rooms are reachable from where.)
