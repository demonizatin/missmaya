// Maya avatar — video plays ONLY when state === "speaking".
// idle/listening = paused (static frame), speaking = playing.
// This matches the spec: the video gates on real AI speech, not on idle time.
function MayaAvatar({ state = 'idle', size = '100%', dimmed = false }) {
  const ref = React.useRef(null);
  const setupDone = React.useRef(false);

  // One-time setup: muted, inline, loop attributes. Don't autoplay here —
  // the second effect controls play/pause based on state.
  React.useEffect(() => {
    const v = ref.current;
    if (!v || setupDone.current) return;
    v.muted = true;
    v.playsInline = true;
    v.loop = true;
    v.setAttribute('muted', '');
    v.setAttribute('playsinline', '');
    setupDone.current = true;
  }, []);

  // State-driven play/pause — the video element only loops while speaking.
  // When idle/listening, pause and reset to first frame for a clean static look.
  React.useEffect(() => {
    const v = ref.current;
    if (!v) return;
    if (state === 'speaking') {
      const p = v.play();
      if (p && p.catch) p.catch(() => {
        // Autoplay was blocked — retry on the next user gesture.
        const retry = () => { v.play().catch(() => {}); window.removeEventListener('pointerdown', retry); };
        window.addEventListener('pointerdown', retry, { passive: true, once: true });
      });
    } else {
      v.pause();
      // Reset to first frame so the static look is consistent (not stuck mid-frame)
      try { v.currentTime = 0; } catch (e) {}
    }
  }, [state]);

  // Listening = subtle desaturate, idle = normal, speaking = slight warmth
  const filter =
    state === 'listening' ? 'saturate(0.9) brightness(0.97)' :
    state === 'speaking'  ? 'saturate(1.05)' :
    'saturate(1) brightness(1)';

  return (
    <div style={{
      width: size, height: size, position: 'relative',
      overflow: 'hidden', borderRadius: 'inherit',
      background: 'linear-gradient(180deg, #E8DFFB 0%, #C9B8F0 100%)',
    }}>
      <video
        ref={ref}
        src="/static/peerup/maya.mp4"
        muted loop playsInline preload="auto"
        style={{
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          objectFit: 'cover', objectPosition: 'center',
          transition: 'filter 240ms',
          filter,
        }}
      />

      {/* Soft lavender overlay to tie video into theme */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at 50% 30%, transparent 40%, rgba(120,90,180,0.18) 100%)',
        pointerEvents: 'none', mixBlendMode: 'multiply',
      }} />

      {/* Listening cue — subtle bottom glow */}
      {state === 'listening' && (
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at 50% 100%, rgba(167,139,222,0.35) 0%, transparent 50%)',
          pointerEvents: 'none', animation: 'listenPulse 2s ease-in-out infinite',
        }} />
      )}

      {/* Dimmed when user holds floor */}
      {dimmed && (
        <div style={{
          position: 'absolute', inset: 0,
          background: 'rgba(255,255,255,0.28)', backdropFilter: 'blur(0.5px)',
          pointerEvents: 'none',
        }} />
      )}

      <style>{`
        @keyframes listenPulse { 0%,100%{opacity:0.6} 50%{opacity:1} }
      `}</style>
    </div>
  );
}

window.MayaAvatar = MayaAvatar;
