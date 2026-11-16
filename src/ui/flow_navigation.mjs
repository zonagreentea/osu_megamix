
export class FlowNavigation {
  constructor(routes, initial = "home") {
    this.routes = routes;
    this.current = initial;
    this.listeners = new Set();
  }

  onChange(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  shortestPath(start, end) {
    if (!this.routes[start] || !this.routes[end])
      throw new Error("Unknown destination");

    const distances = new Map([[start, 0]]);
    const previous = new Map();
    const visited = new Set();

    while (true) {
      let current = null;
      let best = Infinity;

      for (const [node, cost] of distances) {
        if (!visited.has(node) && cost < best) {
          current = node;
          best = cost;
        }
      }

      if (current === null) break;
      if (current === end) break;
      visited.add(current);

      for (const [next, cost] of Object.entries(this.routes[current])) {
        if (!this.routes[next] ||
            !Number.isFinite(cost) || cost < 0)
          throw new Error("Invalid graph edge");

        const candidate = best + cost;
        if (candidate < (distances.get(next) ?? Infinity)) {
          distances.set(next, candidate);
          previous.set(next, current);
        }
      }
    }

    if (!distances.has(end))
      throw new Error("Destination unreachable");

    const path = [end];
    while (path[0] !== start)
      path.unshift(previous.get(path[0]));

    return { path, cost: distances.get(end) };
  }

  async enter(destination, lifecycle = {}) {
    const result = this.shortestPath(this.current, destination);
    if (destination === this.current) return result;

    // Run all lifecycle checks before committing navigation.
    if (lifecycle.canLeave &&
        !(await lifecycle.canLeave(this.current)))
      throw new Error("Exit rejected");

    if (lifecycle.canEnter &&
        !(await lifecycle.canEnter(destination)))
      throw new Error("Entry rejected");

    const previous = this.current;
    this.current = destination;

    for (const listener of this.listeners)
      listener({ previous, current: destination, ...result });

    return result;
  }
}
