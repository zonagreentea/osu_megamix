"""osu!megamix directed shortest-path router."""
import heapq
import math

class FlowRouter:
    def __init__(self):
        self.graph = {}

    def connect(self, source, target, cost=1):
        if not isinstance(cost, (int, float)):
            raise ValueError("Invalid cost")
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("Cost must be finite and nonnegative")
        self.graph.setdefault(source, {})[target] = cost
        self.graph.setdefault(target, {})

    def route(self, start, destination):
        if start not in self.graph:
            raise ValueError("Unknown starting scene")
        if destination not in self.graph:
            raise ValueError("Unknown destination")

        queue = [(0, 0, start)]
        distances = {start: 0}
        previous = {}
        sequence = 0

        while queue:
            cost, _, current = heapq.heappop(queue)
            if cost > distances[current]:
                continue
            if current == destination:
                path = [current]
                while path[-1] != start:
                    path.append(previous[path[-1]])
                return list(reversed(path)), cost

            for neighbor, weight in self.graph[current].items():
                new_cost = cost + weight
                if new_cost < distances.get(neighbor, math.inf):
                    distances[neighbor] = new_cost
                    previous[neighbor] = current
                    sequence += 1
                    heapq.heappush(
                        queue, (new_cost, sequence, neighbor)
                    )

        raise ValueError("Destination unreachable")

def default_router():
    router = FlowRouter()
    connections = [
        ("home", "play", 1),
        ("play", "mode", 1),
        ("mode", "game", 2),
        ("home", "lobby", 2),
        ("lobby", "game", 3),
        ("game", "watch", 2),
        ("home", "watch", 3),
        ("game", "home", 2),
        ("watch", "home", 1),
        ("lobby", "home", 1),
        ("mode", "home", 1),
        ("play", "home", 1),
        ("watch", "game", 2),
    ]
    for start, end, cost in connections:
        router.connect(start, end, cost)
    return router
