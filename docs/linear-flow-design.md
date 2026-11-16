# osu!megamix — Linear Divergent Flow

Architecture:
Input -> Intent -> Router -> State -> Scene -> Renderer

Goals:
- One persistent runtime
- Directed, branching navigation
- Lowest-cost valid transition
- No unnecessary intermediate menus
- Immediate state changes
- Resolution-independent presentation
- No external dependencies

Invariants:
- Route costs are nonnegative and finite
- Unreachable destinations fail explicitly
- Navigation never bypasses required lifecycle checks
- A scene is entered only after its prerequisites succeed
- The router does not modify gameplay timing

The initial edge weights are illustrative, not benchmarks.
