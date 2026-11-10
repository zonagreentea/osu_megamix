export function createAudioController() {
  const AudioCtor = window.AudioContext || window.webkitAudioContext;

  if (!AudioCtor) {
    return { enabled: false, playTone: () => {} };
  }

  const context = new AudioCtor();

  return {
    enabled: true,
    context,
    playTone(frequency = 440, duration = 0.12, wave = 'sine', gainValue = 0.02) {
      try {
        if (context.state === 'suspended') {
          context.resume();
        }

        const oscillator = context.createOscillator();
        const gainNode = context.createGain();

        oscillator.type = wave;
        oscillator.frequency.value = frequency;

        gainNode.gain.value = gainValue;
        gainNode.gain.linearRampToValueAtTime(0.0001, context.currentTime + duration);

        oscillator.connect(gainNode);
        gainNode.connect(context.destination);

        oscillator.start();
        oscillator.stop(context.currentTime + duration);
      } catch (error) {
        // ignore audio failures silently
      }
    }
  };
}
