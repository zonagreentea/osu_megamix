/**
 * Universal browser event spine.
 * Every event contains exactly one value and one timestamp.
 */
export class EventHandler {
  constructor(clock = () => performance.now()) {
    this.clock = clock;
    this.pending = [];
  }

  capture(value, time = this.clock()) {
    const event = Object.freeze({ time, value });
    this.pending.push(event);
    return event;
  }

  adjust(event, transform) {
    return Object.freeze({
      time: event.time,
      value: transform(event.value)
    });
  }

  nextBatch() {
    if (this.pending.length === 0) return [];

    let earliest = Infinity;
    for (const event of this.pending) {
      if (event.time < earliest) earliest = event.time;
    }

    const batch = [];
    const remaining = [];

    for (const event of this.pending) {
      if (event.time === earliest) batch.push(event);
      else remaining.push(event);
    }

    this.pending = remaining;
    return batch;
  }

  dispatch(handler) {
    const batch = this.nextBatch();
    if (batch.length === 0) return undefined;
    return handler(batch);
  }
}
