import SwiftUI

// Bridging to C engine
// We'll add the bridging header in the Xcode project step.
final class SimViewModel: ObservableObject {
    @Published var tick: UInt32 = 0
    @Published var rng: UInt32 = 0

    private var world = bh_world_t()

    init() {
        bh_init(&world, 1337)
        sync()
    }

    func step() {
        bh_step(&world)
        sync()
    }

    private func sync() {
        let s = bh_state(&world)!.pointee
        tick = s.tick
        rng  = s.rng
    }
}

struct ContentView: View {
    @StateObject private var vm = SimViewModel()
    var body: some View {
        VStack(spacing: 16) {
            Text("BALLHARD iOS").font(.title2)
            Text("tick: \(vm.tick)")
            Text("rng: \(vm.rng)")
            Button("STEP (truth)") { vm.step() }
        }
        .padding()
    }
}
