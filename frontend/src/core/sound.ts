let audioContext: AudioContext | null = null;

const TASK_COMPLETION_SOUND_KEY = "sound.taskCompletion.enabled";

function isTaskCompletionSoundEnabled(): boolean {
    if (typeof window === "undefined") {
        return true;
    }

    try {
        const stored = window.localStorage.getItem(TASK_COMPLETION_SOUND_KEY);
        if (stored === null) {
            return true;
        }
        return stored !== "false";
    } catch {
        // If localStorage is unavailable (e.g., privacy mode), fall back to enabled.
        return true;
    }
}

function getAudioContext(): AudioContext | null {
    if (typeof window === 'undefined') {
        return null;
    }

    if (!audioContext) {
        const AudioContextConstructor =
            window.AudioContext ||
            (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
        if (!AudioContextConstructor) {
            return null;
        }
        audioContext = new AudioContextConstructor();
    }

    return audioContext;
}

async function resumeContext(context: AudioContext) {
    if (context.state === 'suspended') {
        try {
            await context.resume();
        } catch {
            // Ignore resume failures; sound playback is not critical.
        }
    }
}

export async function playTaskCompletedSound() {
    if (!isTaskCompletionSoundEnabled()) {
        return;
    }

    const context = getAudioContext();
    if (!context) {
        return;
    }

    await resumeContext(context);

    const now = context.currentTime;

    // Soft, gentle gain envelope - like a breeze
    const masterGain = context.createGain();
    masterGain.gain.setValueAtTime(0, now);
    masterGain.gain.linearRampToValueAtTime(0.08, now + 0.08);  // Gentle fade in
    masterGain.gain.exponentialRampToValueAtTime(0.01, now + 1.2);  // Long, soft fade out
    masterGain.connect(context.destination);

    // Root note - C major chord (C-E-G) creates uplifting, positive feeling
    const root = context.createOscillator();
    root.type = 'sine';
    root.frequency.setValueAtTime(523.25, now);  // C5
    root.connect(masterGain);
    root.start(now);
    root.stop(now + 1.2);

    // Third - adds warmth
    const third = context.createOscillator();
    third.type = 'sine';
    third.frequency.setValueAtTime(659.25, now + 0.05);  // E5 (slight delay for richness)
    third.connect(masterGain);
    third.start(now + 0.05);
    third.stop(now + 1.2);

    // Fifth - completes the chord
    const fifth = context.createOscillator();
    fifth.type = 'sine';
    fifth.frequency.setValueAtTime(783.99, now + 0.1);  // G5 (slight delay)
    fifth.connect(masterGain);
    fifth.start(now + 0.1);
    fifth.stop(now + 1.2);

    // High shimmer - like sunlight through leaves
    const shimmer = context.createOscillator();
    shimmer.type = 'sine';
    shimmer.frequency.setValueAtTime(1568, now + 0.15);  // C6 (octave above root)

    // Shimmer has its own gentle envelope
    const shimmerGain = context.createGain();
    shimmerGain.gain.setValueAtTime(0, now + 0.15);
    shimmerGain.gain.linearRampToValueAtTime(0.03, now + 0.25);
    shimmerGain.gain.exponentialRampToValueAtTime(0.001, now + 1.0);

    shimmer.connect(shimmerGain);
    shimmerGain.connect(context.destination);
    shimmer.start(now + 0.15);
    shimmer.stop(now + 1.0);

    const cleanUp = () => {
        root.disconnect();
        third.disconnect();
        fifth.disconnect();
        shimmer.disconnect();
        shimmerGain.disconnect();
        masterGain.disconnect();
    };

    // Clean up after the longest oscillator finishes
    root.addEventListener('ended', cleanUp, { once: true });
}
