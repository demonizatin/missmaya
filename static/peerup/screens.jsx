// All PeerUp screens. Imports MayaAvatar.

// Re-themed: white + light purple
const PALETTE = {
  cream: '#FFFFFF',          // pure white surface
  creamSoft: '#F5F1FB',      // softest lavender wash
  terracotta: '#A78BDE',     // light purple primary
  terracottaDeep: '#7A5DC9', // deeper purple for press / accents
  ink: '#1E183A',            // deep violet-ink for text
  inkSoft: '#3A2F5C',
  muted: '#8A82A6',
  duskBg: '#13101F',
  duskCard: '#1E1934',
  duskInk: '#F4EFFB',
  // extras
  lavenderTint: '#EFE7FB',
  lavenderEdge: '#D8C8F2',
};

const SERIF = '"Fraunces", "Source Serif Pro", Georgia, serif';
const SANS = '"Inter", -apple-system, system-ui, sans-serif';

// ─────────────────────────────────────────────────────────────
// 1. SPLASH
// ─────────────────────────────────────────────────────────────
function SplashScreen() {
  return (
    <div style={{
      width: '100%', height: '100%', position: 'relative', overflow: 'hidden',
      background: `radial-gradient(ellipse at 50% 35%, #FFFFFF 0%, ${PALETTE.lavenderTint} 35%, ${PALETTE.terracotta} 100%)`,
    }}>
      {/* Animated soft warm glow */}
      <div style={{
        position: 'absolute', inset: '-20%',
        background: 'radial-gradient(circle at 30% 70%, rgba(216,200,242,0.55) 0%, transparent 40%), radial-gradient(circle at 70% 30%, rgba(255,255,255,0.6) 0%, transparent 35%)',
        animation: 'splashGlow 4s ease-in-out infinite alternate',
      }} />
      <div style={{
        position: 'absolute', inset: 0, display: 'flex',
        alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
      }}>
        <div style={{
          fontFamily: SERIF, fontSize: 56, fontWeight: 400,
          color: PALETTE.ink, letterSpacing: -1.5,
          fontStyle: 'italic', fontVariationSettings: '"SOFT" 100, "WONK" 1',
          textShadow: '0 2px 20px rgba(122,93,201,0.18)',
        }}>PeerUp</div>
        <div style={{
          fontFamily: SANS, fontSize: 13, fontWeight: 400,
          color: 'rgba(58,47,92,0.65)', letterSpacing: 4,
          textTransform: 'uppercase', marginTop: 14,
        }}>practice, gently</div>
      </div>
      <style>{`@keyframes splashGlow { 0%{transform:scale(1) rotate(0deg)} 100%{transform:scale(1.15) rotate(8deg)} }`}</style>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 2. WELCOME — one-tap start
// ─────────────────────────────────────────────────────────────
function WelcomeScreen({ onStart }) {
  const [pressing, setPressing] = React.useState(false);
  return (
    <div style={{
      width: '100%', height: '100%', position: 'relative',
      background: PALETTE.cream, overflow: 'hidden',
      display: 'flex', flexDirection: 'column',
    }}>
      {/* Tiny preview of Maya peeking — circle in upper third */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: 60 }}>
        <div style={{
          width: 220, height: 220, borderRadius: '50%', overflow: 'hidden',
          boxShadow: '0 30px 60px rgba(122,93,201,0.22), 0 0 0 8px rgba(239,231,251,0.7)',
        }}>
          <MayaAvatar state="idle" />
        </div>
      </div>

      <div style={{ padding: '0 32px 12px' }}>
        <div style={{
          fontFamily: SERIF, fontSize: 38, fontWeight: 400,
          color: PALETTE.ink, lineHeight: 1.1, letterSpacing: -1,
          textWrap: 'pretty',
        }}>
          Hi! I'm Maya.<br/>
          <span style={{ fontStyle: 'italic', color: PALETTE.terracottaDeep }}>Let's chat.</span>
        </div>
        <div style={{
          fontFamily: SANS, fontSize: 15, color: PALETTE.muted,
          marginTop: 14, lineHeight: 1.5, maxWidth: 280,
        }}>
          Five minutes, on your chai break. No tests. Just talking.
        </div>
      </div>

      {/* Big circular CTA */}
      <div style={{ display: 'flex', justifyContent: 'center', padding: '24px 0 18px' }}>
        <button
          onClick={onStart}
          onPointerDown={() => setPressing(true)}
          onPointerUp={() => setPressing(false)}
          onPointerLeave={() => setPressing(false)}
          style={{
            width: 116, height: 116, borderRadius: '50%', border: 'none',
            background: `radial-gradient(circle at 30% 30%, #C9B5EE 0%, ${PALETTE.terracotta} 50%, ${PALETTE.terracottaDeep} 100%)`,
            color: PALETTE.cream, fontFamily: SERIF, fontSize: 18,
            fontStyle: 'italic', fontWeight: 400, cursor: 'pointer',
            transform: pressing ? 'scale(0.94)' : 'scale(1)',
            transition: 'transform 200ms cubic-bezier(.2,.8,.2,1)',
            boxShadow: pressing
              ? '0 4px 12px rgba(122,93,201,0.4), inset 0 0 0 3px rgba(255,255,255,0.2)'
              : '0 12px 32px rgba(122,93,201,0.45), 0 4px 8px rgba(122,93,201,0.25), inset 0 0 0 3px rgba(255,255,255,0.25)',
          }}>
          Start
        </button>
      </div>

      <div style={{
        textAlign: 'center', padding: '0 40px 36px',
        fontFamily: SERIF, fontSize: 13, fontStyle: 'italic',
        color: PALETTE.muted,
      }}>
        I'll remember you for next time.
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 3. ONBOARDING — Maya asks her own question (full-screen avatar)
// ─────────────────────────────────────────────────────────────
function OnboardingScreen({ onComplete }) {
  const [step, setStep] = React.useState(0);
  const [mayaState, setMayaState] = React.useState('speaking');
  const [showCaption, setShowCaption] = React.useState(true);

  const turns = [
    "Hi! What should I call you?",
    "Lovely. And where are you from?",
    "What brings you here today?",
  ];

  // Auto-cycle Maya speaking → listening → next
  React.useEffect(() => {
    setMayaState('speaking');
    const t1 = setTimeout(() => setMayaState('listening'), 2400);
    return () => clearTimeout(t1);
  }, [step]);

  const next = () => {
    if (step < turns.length - 1) setStep(s => s + 1);
    else onComplete();
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#1A1230' }}>
      <div style={{ position: 'absolute', inset: 0 }}>
        <MayaAvatar state={mayaState} />
      </div>

      {/* soft top gradient for status bar legibility */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 120,
        background: 'linear-gradient(to bottom, rgba(0,0,0,0.45), transparent)',
        pointerEvents: 'none',
      }} />

      {/* Caption — film-subtitle style */}
      {showCaption && (
        <div key={step} style={{
          position: 'absolute', left: 28, right: 28, bottom: 200,
          fontFamily: SERIF, fontSize: 26, lineHeight: 1.3,
          color: PALETTE.cream, letterSpacing: -0.5, fontWeight: 400,
          textShadow: '0 2px 16px rgba(0,0,0,0.6)',
          textWrap: 'pretty', textAlign: 'left',
          animation: 'captionFade 600ms ease-out',
        }}>
          {turns[step]}
        </div>
      )}

      {/* Mic indicator */}
      <div style={{
        position: 'absolute', bottom: 90, left: 0, right: 0,
        display: 'flex', justifyContent: 'center',
      }}>
        <button onClick={next} style={{
          background: 'rgba(255,255,255,0.12)',
          backdropFilter: 'blur(20px) saturate(180%)',
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          border: '1px solid rgba(255,255,255,0.18)',
          borderRadius: 999, padding: '14px 26px',
          color: PALETTE.cream, fontFamily: SANS, fontSize: 14,
          fontWeight: 500, letterSpacing: 0.2, cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <MicPulse small/>
          {step < turns.length - 1 ? 'Tap when you reply' : "Tap to begin"}
        </button>
      </div>

      <style>{`@keyframes captionFade { from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:translateY(0)} }`}</style>
    </div>
  );
}

function MicPulse({ small = false, level = 0.6 }) {
  const s = small ? 14 : 20;
  return (
    <div style={{ width: s, height: s, position: 'relative' }}>
      <div style={{
        position: 'absolute', inset: 0, borderRadius: '50%',
        background: 'radial-gradient(circle, #C9B5EE 0%, #7A5DC9 70%)',
        animation: 'micPulse 1.4s ease-in-out infinite',
      }} />
      <style>{`@keyframes micPulse { 0%,100%{transform:scale(0.85);opacity:0.7} 50%{transform:scale(1.1);opacity:1} }`}</style>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 4. LIVE CALL — the room
// ─────────────────────────────────────────────────────────────
// ─────────────────────────────────────────────────────────────
// Real chat backend integration for the call screen
// ─────────────────────────────────────────────────────────────

// Event-gated save policy: same regex set as the main chat — only call
// /end_session if the turn pair contains memorable content.
const MEMORY_SIGNALS_DESIGN = [
  /\btomorrow\b/i, /\byesterday\b/i, /\b(next|last)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/i,
  /\b(in|on|by|until|after)\s+\d/i,
  /\b\d+(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
  /\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d+/i,
  /\b(20\d{2})\b/,
  /\b(exam|wedding|trip|interview|meeting|appointment|birthday|bday|anniversary|conference|deadline|presentation|graduation|moving|surgery)\b/i,
  /\bi\s+(am|'m|was|work|live|moved|switched|grew|studied|joined|finished|started|broke|got|have)\s+/i,
  /\bmy\s+(name|brother|sister|mom|dad|mother|father|wife|husband|partner|girlfriend|boyfriend|son|daughter|kid|child|friend|manager|boss|colleague|family|home|city|hometown|job|work|company|school|college)\b/i,
  /\b(call me|i go by|nickname)\b/i,
  /\b(want to|plan to|going to|hoping to|trying to|aiming for|preparing for)\b/i,
  /\b(got promoted|got the job|won|lost|passed|failed|completed|finished|published|launched)\b/i,
];
function detectMemorableContentDesign(text) {
  if (!text || typeof text !== "string") return false;
  return MEMORY_SIGNALS_DESIGN.some(re => re.test(text));
}

// Strip JSON/code-fence/quote artifacts from streamed AI replies.
function extractMessageDesign(raw) {
  if (!raw) return "";
  let s = String(raw);
  let stripped = s.replace(/^```(?:json)?\s*/i, "").replace(/\s*```\s*$/, "").trim();
  try {
    const p = JSON.parse(stripped);
    if (p && typeof p === "object" && typeof p.message === "string") return p.message;
  } catch (_) {}
  const m = stripped.match(/"message"\s*:\s*"((?:\\.|[^"\\])*)"?/);
  if (m) {
    return m[1].replace(/\\"/g, '"').replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\\\/g, "\\");
  }
  return stripped.replace(/^[`"'\s]+/, "").replace(/[`"'\s]+$/, "").trim();
}

// Persistent session id for this design call (mirrors main chat behavior).
const DESIGN_SESSION_ID =
  (window.crypto && crypto.randomUUID && crypto.randomUUID()) ||
  ("design-sess-" + Date.now() + "-" + Math.random().toString(36).slice(2, 10));

function CallScreen({ dark, captions, onNav, ambient }) {
  // Real chat wiring — no fake timers. mayaState transitions on actual audio
  // play/end events. Event-gated /end_session save runs after each AI reply.
  const [mayaState, setMayaState] = React.useState('idle');
  const [endHolding, setEndHolding] = React.useState(false);
  const [endProgress, setEndProgress] = React.useState(0);
  const [helpHold, setHelpHold] = React.useState(false);
  const [helpResult, setHelpResult] = React.useState(null);
  const [inputValue, setInputValue] = React.useState('');
  const [isReplying, setIsReplying] = React.useState(false);
  const [history, setHistory] = React.useState([]);
  const endTimer = React.useRef(null);
  const audioQueueRef = React.useRef([]);
  const audioPlayingRef = React.useRef(false);

  // Hard-coded profile for the design demo. Could be passed via props later.
  const PROFILE = {
    user_name: "Priyansh",
    profession: "Software engineer",
    mother_tongue: "Hindi",
    interests: "Cricket, Bollywood movies, Startups",
  };

  function pumpQueue() {
    if (audioPlayingRef.current) return;
    while (audioQueueRef.current.length && (audioQueueRef.current[0].aborted)) {
      audioQueueRef.current.shift();
    }
    if (!audioQueueRef.current.length) return;
    const head = audioQueueRef.current[0];
    if (!head.ready) return;
    audioQueueRef.current.shift();
    audioPlayingRef.current = true;
    const audio = new Audio(head.blobUrl);
    audio.onplay = () => {
      // First audio chunk from THIS reply landed → Maya is now speaking
      setMayaState('speaking');
    };
    audio.onended = () => {
      URL.revokeObjectURL(head.blobUrl);
      audioPlayingRef.current = false;
      pumpQueue();
      // If the queue is empty AND we've finished receiving the reply, idle out
      if (audioQueueRef.current.length === 0) {
        setMayaState('idle');
      }
    };
    audio.onerror = () => {
      URL.revokeObjectURL(head.blobUrl);
      audioPlayingRef.current = false;
      pumpQueue();
    };
    audio.play().catch(() => { audioPlayingRef.current = false; });
  }

  async function fetchAndQueueTts(text) {
    const item = { ready: false, aborted: false, blobUrl: null, text };
    audioQueueRef.current.push(item);
    try {
      const r = await fetch("/tts", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text, engine: "piper" }),
      });
      if (!r.ok) throw new Error("tts " + r.status);
      const blob = await r.blob();
      item.blobUrl = URL.createObjectURL(blob);
      item.ready = true;
      pumpQueue();
    } catch (e) {
      item.aborted = true;
      // Fallback: speech synthesis (best effort)
      if ("speechSynthesis" in window) {
        const u = new SpeechSynthesisUtterance(text);
        u.onstart = () => setMayaState('speaking');
        u.onend = () => { if (audioQueueRef.current.length === 0) setMayaState('idle'); };
        speechSynthesis.speak(u);
      }
      pumpQueue();
    }
  }

  function speakNewSentencesIncremental(fullText, alreadySpokenChars) {
    const unspoken = fullText.slice(alreadySpokenChars);
    const re = /[^.!?]+[.!?]+(?:\s|$)/g;
    let m, lastEnd = 0;
    while ((m = re.exec(unspoken)) !== null) {
      const sentence = m[0].trim();
      if (sentence) fetchAndQueueTts(sentence);
      lastEnd = m.index + m[0].length;
    }
    return alreadySpokenChars + lastEnd;
  }

  async function maybeSaveMemory(historyForSave) {
    // Only call /end_session if the latest pair has memorable content.
    if (historyForSave.length < 2) return;
    const lastUser = historyForSave[historyForSave.length - 2]?.content || "";
    const lastAi = historyForSave[historyForSave.length - 1]?.content || "";
    if (!detectMemorableContentDesign(lastUser + " " + lastAi)) return;
    try {
      await fetch("/end_session", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ user_name: PROFILE.user_name, history: historyForSave }),
      });
    } catch (_) {}
  }

  const sendMessage = async () => {
    const text = inputValue.trim();
    if (!text || isReplying) return;
    setInputValue('');
    setIsReplying(true);
    setMayaState('listening');

    const reqBody = {
      ...PROFILE,
      session_id: DESIGN_SESSION_ID,
      history: [...history],
      user_message: text,
      backend: "auto",
    };
    let resp;
    try {
      resp = await fetch("/chat", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify(reqBody),
      });
    } catch (e) {
      setIsReplying(false);
      setMayaState('idle');
      return;
    }

    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = "", rawAccum = "", spokenChars = 0, fullText = "", finalReply = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split("\n\n");
      buf = lines.pop();
      for (const ln of lines) {
        if (!ln.startsWith("data: ")) continue;
        try {
          const ev = JSON.parse(ln.slice(6));
          if (ev.type === "delta") {
            rawAccum += ev.text;
            const partial = extractMessageDesign(rawAccum);
            if (partial) {
              spokenChars = speakNewSentencesIncremental(partial, spokenChars);
            }
          } else if (ev.type === "done") {
            fullText = ev.full;
            finalReply = extractMessageDesign(fullText);
            // Speak any tail not yet sent
            if (finalReply.length > spokenChars) {
              const tail = finalReply.slice(spokenChars).trim();
              if (tail) fetchAndQueueTts(tail);
            }
          }
        } catch (_) {}
      }
    }

    const newHistory = [
      ...history,
      { role: "user", content: text },
      { role: "assistant", content: fullText || finalReply },
    ];
    setHistory(newHistory);
    setIsReplying(false);

    // Event-gated save — fires only on memorable content
    maybeSaveMemory(newHistory);
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Long-press to hang up
  const startEnd = (e) => {
    e.stopPropagation();
    setEndHolding(true);
    const start = performance.now();
    endTimer.current = setInterval(() => {
      const p = Math.min(1, (performance.now() - start) / 1000);
      setEndProgress(p);
      if (p >= 1) {
        clearInterval(endTimer.current);
        setEndHolding(false);
        onNav('welcome');
      }
    }, 16);
  };
  const stopEnd = (e) => {
    e?.stopPropagation();
    clearInterval(endTimer.current);
    setEndHolding(false);
    setEndProgress(0);
  };

  // Hindi helper
  const startHelp = (e) => {
    e.stopPropagation();
    setHelpHold(true);
    setTimeout(() => {
      if (helpHoldRef.current) {
        setHelpResult({ hi: 'samjhauta', en: 'compromise' });
      }
    }, 800);
  };
  const helpHoldRef = React.useRef(false);
  React.useEffect(() => { helpHoldRef.current = helpHold; }, [helpHold]);
  const stopHelp = (e) => { e?.stopPropagation(); setHelpHold(false); };

  const ink = dark ? PALETTE.duskInk : PALETTE.cream;

  return (
    <div style={{
      width: '100%', height: '100%', position: 'relative',
      background: dark ? '#0E0A1C' : '#1A1230',
      overflow: 'hidden', userSelect: 'none',
    }}>
      {/* Maya — top 70%. Video plays only when mayaState === 'speaking' */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '72%',
        transition: 'filter 220ms',
      }}>
        <MayaAvatar state={mayaState} />
      </div>

      {/* Bottom panel — cream/dusk with text input */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: '32%',
        background: dark ? '#1E1934' : PALETTE.cream,
        borderTopLeftRadius: 32, borderTopRightRadius: 32,
        display: 'flex', flexDirection: 'column',
        boxShadow: '0 -20px 40px rgba(0,0,0,0.3)',
      }}>
        {/* Text input replaces the mic bar */}
        <div style={{ padding: '20px 24px 8px', display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={isReplying}
            placeholder={isReplying ? "Maya is replying…" : "Type a message…"}
            style={{
              flex: 1, padding: '12px 16px', borderRadius: 22,
              border: dark ? '1px solid rgba(244,239,251,0.15)' : '1px solid rgba(122,93,201,0.18)',
              background: dark ? 'rgba(244,239,251,0.06)' : '#fff',
              color: dark ? PALETTE.duskInk : PALETTE.ink,
              fontFamily: SANS, fontSize: 15, outline: 'none',
              opacity: isReplying ? 0.6 : 1,
            }}
          />
          <button
            onClick={sendMessage}
            disabled={isReplying || !inputValue.trim()}
            style={{
              width: 44, height: 44, borderRadius: '50%', border: 'none',
              background: (isReplying || !inputValue.trim()) ? PALETTE.muted : PALETTE.terracottaDeep,
              cursor: (isReplying || !inputValue.trim()) ? 'default' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(122,93,201,0.35)',
              transition: 'all 150ms',
            }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M3 12 L21 4 L17 21 L13 13 Z" stroke={PALETTE.cream} strokeWidth="2" strokeLinejoin="round" fill="none" />
            </svg>
          </button>
        </div>

        {/* Two icons — end + Hindi helper (CC removed since captions are gone) */}
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-around',
          padding: '0 32px 38px',
        }}>
          <div style={{ width: 52 }} />  {/* spacer to keep end button centered */}

          {/* End call — long press */}
          <div
            onPointerDown={startEnd} onPointerUp={stopEnd} onPointerLeave={stopEnd}
            style={{
              width: 64, height: 64, borderRadius: '50%', position: 'relative',
              background: PALETTE.terracottaDeep, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(122,93,201,0.5)',
              transform: endHolding ? 'scale(0.95)' : 'scale(1)',
              transition: 'transform 120ms',
            }}>
            <svg style={{ position: 'absolute', inset: -4 }} viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="34" stroke={PALETTE.terracotta} strokeWidth="3" fill="none" opacity="0.3" />
              <circle cx="36" cy="36" r="34" stroke={PALETTE.cream} strokeWidth="3" fill="none"
                strokeDasharray={`${2*Math.PI*34}`}
                strokeDashoffset={`${2*Math.PI*34*(1-endProgress)}`}
                strokeLinecap="round"
                transform="rotate(-90 36 36)"
                style={{ transition: 'stroke-dashoffset 80ms linear' }} />
            </svg>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <path d="M5 17 Q 14 9 23 17 L 21 21 Q 18 19 17 17 L 17 14 Q 14 13 11 14 L 11 17 Q 10 19 7 21 Z"
                fill={PALETTE.cream} transform="rotate(135 14 14)" />
            </svg>
          </div>

          <div onPointerDown={startHelp} onPointerUp={stopHelp} onPointerLeave={stopHelp}>
            <CallIcon dark={dark} active={helpHold} label="हिं" onClick={(e) => e.stopPropagation()} />
          </div>
        </div>
      </div>

      {/* Top-right tray icons (memory, practice, progress, settings) */}
      <TopTray onNav={onNav} dark={dark} />

      {/* Hindi helper popover */}
      {helpResult && (
        <div onClick={(e) => { e.stopPropagation(); setHelpResult(null); }}
          style={{
            position: 'absolute', inset: 0, background: 'rgba(30,24,58,0.45)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backdropFilter: 'blur(8px)', zIndex: 20,
          }}>
          <div style={{
            background: PALETTE.cream, padding: '28px 32px', borderRadius: 24,
            margin: '0 32px', textAlign: 'center', maxWidth: 280,
          }}>
            <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 13, color: PALETTE.muted }}>You said</div>
            <div style={{ fontFamily: SERIF, fontSize: 28, color: PALETTE.ink, marginTop: 4 }}>
              {helpResult.hi}
            </div>
            <div style={{ height: 1, background: 'rgba(0,0,0,0.08)', margin: '14px 0' }} />
            <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 13, color: PALETTE.muted }}>In English</div>
            <div style={{ fontFamily: SERIF, fontSize: 24, color: PALETTE.terracottaDeep, marginTop: 4 }}>
              {helpResult.en}
            </div>
          </div>
        </div>
      )}

      <style>{`@keyframes fadeIn { from{opacity:0} to{opacity:1} }`}</style>
    </div>
  );
}

function MicBar({ level, dark, active }) {
  const bars = 28;
  return (
    <div style={{
      height: 38, display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 4,
    }}>
      {Array.from({ length: bars }).map((_, i) => {
        const center = bars / 2;
        const dist = Math.abs(i - center) / center;
        const wave = active ? (Math.sin(Date.now()/120 + i*0.6) * 0.5 + 0.5) : 0.2;
        const h = active ? 6 + (level * (1 - dist*0.7)) * wave * 30 : 4;
        return (
          <div key={i} style={{
            width: 3, height: h, borderRadius: 2,
            background: active
              ? `linear-gradient(to top, ${PALETTE.terracottaDeep}, ${PALETTE.terracotta}, #D8C8F2)`
              : (dark ? 'rgba(244,239,251,0.18)' : 'rgba(30,24,58,0.12)'),
            transition: 'height 80ms ease-out',
          }} />
        );
      })}
    </div>
  );
}

function CallIcon({ active, label, dark, onClick }) {
  return (
    <button onClick={onClick} style={{
      width: 52, height: 52, borderRadius: '50%', border: 'none',
      background: active
        ? PALETTE.terracotta
        : (dark ? 'rgba(255,255,255,0.08)' : 'rgba(122,93,201,0.08)'),
      color: active ? PALETTE.cream : (dark ? PALETTE.duskInk : PALETTE.ink),
      fontFamily: SANS, fontSize: 13, fontWeight: 600, cursor: 'pointer',
      letterSpacing: 0.5,
      transition: 'all 200ms',
    }}>{label}</button>
  );
}

function TopTray({ onNav, dark }) {
  const items = [
    { id: 'memory', icon: '◐', label: 'Memory' },
    { id: 'practice', icon: '◇', label: 'Practice' },
    { id: 'progress', icon: '◇', label: 'Progress' },
    { id: 'settings', icon: '◌', label: 'Settings' },
  ];
  const [open, setOpen] = React.useState(false);

  return (
    <div style={{ position: 'absolute', top: 60, right: 16, zIndex: 12 }} onClick={(e) => e.stopPropagation()}>
      <div style={{
        display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end',
      }}>
        <button
          onClick={() => setOpen(o => !o)}
          style={{
            width: 40, height: 40, borderRadius: '50%', border: 'none',
            background: 'rgba(255,255,255,0.18)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: PALETTE.cream, fontSize: 18,
          }}>
          {open ? '✕' : '⋯'}
        </button>
        {open && items.map((it, i) => (
          <button key={it.id} onClick={() => { setOpen(false); onNav(it.id); }}
            style={{
              padding: '8px 14px 8px 12px', height: 36, borderRadius: 18, border: 'none',
              background: 'rgba(255,255,255,0.18)',
              backdropFilter: 'blur(20px) saturate(180%)',
              WebkitBackdropFilter: 'blur(20px) saturate(180%)',
              color: PALETTE.cream, fontFamily: SANS, fontSize: 13, fontWeight: 500,
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
              animation: `trayIn 200ms ${i*40}ms both ease-out`,
            }}>
            <span style={{ fontSize: 14 }}>{it.icon}</span>{it.label}
          </button>
        ))}
      </div>
      <style>{`@keyframes trayIn { from{opacity:0; transform:translateX(8px)} to{opacity:1; transform:translateX(0)} }`}</style>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MEMORY — "What we've talked about"
// ─────────────────────────────────────────────────────────────
function MemoryScreen({ onBack }) {
  const [memories, setMemories] = React.useState([
    "I know you're Sunil. You work in hardware sales in Indore.",
    "Your dream is a B2B sales role in Bangalore.",
    "You broke your leg playing cricket at 16, and your knee still aches when it rains.",
    "Last time we practiced introducing yourself for that Tuesday client call.",
    "You like your tea strong, two sugars. You told me on Monday.",
  ]);
  const [confirmIdx, setConfirmIdx] = React.useState(null);

  return (
    <ScreenShell onBack={onBack}>
      <div style={{ padding: '20px 28px 8px' }}>
        <div style={{ fontFamily: SANS, fontSize: 11, letterSpacing: 2,
          textTransform: 'uppercase', color: PALETTE.muted, fontWeight: 500 }}>
          Maya remembers
        </div>
        <div style={{
          fontFamily: SERIF, fontSize: 32, color: PALETTE.ink,
          marginTop: 8, lineHeight: 1.15, letterSpacing: -0.5, fontWeight: 400,
        }}>
          What we've talked <span style={{ fontStyle: 'italic' }}>about.</span>
        </div>
      </div>

      <div style={{ padding: '16px 24px 60px' }}>
        {memories.map((m, i) => (
          <div key={i} style={{
            background: 'rgba(255,255,255,0.55)',
            borderRadius: 18, padding: '18px 20px',
            marginBottom: 12, position: 'relative',
            boxShadow: '0 1px 0 rgba(30,24,58,0.04)',
            display: 'flex', gap: 14, alignItems: 'flex-start',
          }}>
            <div style={{
              width: 22, height: 22, borderRadius: '50%',
              background: `linear-gradient(135deg, ${PALETTE.terracotta}, ${PALETTE.terracottaDeep})`,
              flexShrink: 0, marginTop: 2,
              boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.3)',
            }} />
            <div style={{
              fontFamily: SERIF, fontSize: 17, lineHeight: 1.45,
              color: PALETTE.inkSoft, flex: 1, fontWeight: 400,
              textWrap: 'pretty',
            }}>{m}</div>
            <button onClick={() => setConfirmIdx(i)} style={{
              background: 'transparent', border: 'none', cursor: 'pointer',
              color: PALETTE.muted, fontSize: 18, padding: 0, lineHeight: 1,
            }}>✕</button>
          </div>
        ))}

        <div style={{
          fontFamily: SERIF, fontStyle: 'italic', fontSize: 14,
          color: PALETTE.muted, textAlign: 'center', marginTop: 32,
          padding: '0 32px', lineHeight: 1.5,
        }}>
          Tap ✕ on anything you'd rather I forget.<br/>
          Nothing leaves this phone.
        </div>
      </div>

      {confirmIdx !== null && (
        <div onClick={() => setConfirmIdx(null)} style={{
          position: 'absolute', inset: 0, background: 'rgba(30,24,58,0.45)',
          backdropFilter: 'blur(8px)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 30,
        }}>
          <div onClick={(e) => e.stopPropagation()} style={{
            background: PALETTE.cream, padding: '24px 24px 16px', borderRadius: 22,
            margin: '0 32px', maxWidth: 300,
          }}>
            <div style={{ fontFamily: SERIF, fontSize: 19, color: PALETTE.ink, lineHeight: 1.35 }}>
              Forget this?
            </div>
            <div style={{ fontFamily: SANS, fontSize: 13, color: PALETTE.muted, marginTop: 6, lineHeight: 1.5 }}>
              I'll erase it from our memory. I won't bring it up again.
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 18 }}>
              <button onClick={() => setConfirmIdx(null)} style={{
                flex: 1, padding: '12px', borderRadius: 12, border: 'none',
                background: 'rgba(122,93,201,0.10)', color: PALETTE.ink,
                fontFamily: SANS, fontSize: 14, fontWeight: 500, cursor: 'pointer',
              }}>Keep it</button>
              <button onClick={() => {
                setMemories(m => m.filter((_, i) => i !== confirmIdx));
                setConfirmIdx(null);
              }} style={{
                flex: 1, padding: '12px', borderRadius: 12, border: 'none',
                background: PALETTE.terracottaDeep, color: PALETTE.cream,
                fontFamily: SANS, fontSize: 14, fontWeight: 500, cursor: 'pointer',
              }}>Forget</button>
            </div>
          </div>
        </div>
      )}
    </ScreenShell>
  );
}

// ─────────────────────────────────────────────────────────────
// PRACTICE — three scenarios
// ─────────────────────────────────────────────────────────────
function PracticeScreen({ onBack, onStartScenario }) {
  const scenarios = [
    { title: "Decline a meeting politely", time: "2 min", hint: "with a colleague who outranks you" },
    { title: "Ask your boss for feedback", time: "3 min", hint: "without sounding insecure" },
    { title: "Order coffee in English", time: "1 min", hint: "café small-talk included" },
  ];
  return (
    <ScreenShell onBack={onBack}>
      <div style={{ padding: '20px 28px 8px' }}>
        <div style={{ fontFamily: SANS, fontSize: 11, letterSpacing: 2,
          textTransform: 'uppercase', color: PALETTE.muted, fontWeight: 500 }}>Today</div>
        <div style={{
          fontFamily: SERIF, fontSize: 32, color: PALETTE.ink,
          marginTop: 8, lineHeight: 1.15, letterSpacing: -0.5,
        }}>
          A few things we could <span style={{ fontStyle: 'italic' }}>practice.</span>
        </div>
      </div>

      <div style={{ padding: '20px 24px 60px' }}>
        {scenarios.map((s, i) => (
          <button key={i} onClick={() => onStartScenario(s)} style={{
            display: 'block', width: '100%', textAlign: 'left',
            background: i === 0 ? PALETTE.terracotta : 'rgba(255,255,255,0.6)',
            color: i === 0 ? PALETTE.cream : PALETTE.ink,
            border: 'none', borderRadius: 22, padding: '24px 22px 22px',
            marginBottom: 14, cursor: 'pointer', position: 'relative',
            boxShadow: i === 0
              ? '0 12px 28px rgba(122,93,201,0.35), inset 0 1px 0 rgba(255,255,255,0.25)'
              : '0 1px 0 rgba(30,24,58,0.04)',
            overflow: 'hidden',
          }}>
            <div style={{
              fontFamily: SANS, fontSize: 11, letterSpacing: 1.5,
              textTransform: 'uppercase', opacity: 0.7, fontWeight: 500,
            }}>{s.time} · role-play</div>
            <div style={{
              fontFamily: SERIF, fontSize: 24, marginTop: 6,
              lineHeight: 1.25, letterSpacing: -0.4, fontWeight: 400,
              fontStyle: i === 0 ? 'italic' : 'normal',
            }}>"{s.title}"</div>
            <div style={{
              fontFamily: SERIF, fontSize: 14, fontStyle: 'italic',
              opacity: 0.75, marginTop: 8,
            }}>{s.hint}</div>
            {/* warm spine */}
            {i === 0 && <div style={{
              position: 'absolute', top: 14, right: 14,
              fontFamily: SERIF, fontSize: 11, fontStyle: 'italic',
              background: 'rgba(255,255,255,0.2)', padding: '4px 10px', borderRadius: 99,
            }}>suggested</div>}
          </button>
        ))}

        <div style={{
          fontFamily: SERIF, fontStyle: 'italic', fontSize: 14,
          color: PALETTE.muted, textAlign: 'center', marginTop: 24,
          padding: '0 24px', lineHeight: 1.5,
        }}>
          Or just open the call and we can chat about whatever's on your mind.
        </div>
      </div>
    </ScreenShell>
  );
}

// ─────────────────────────────────────────────────────────────
// PROGRESS — calm, non-gamified
// ─────────────────────────────────────────────────────────────
function ProgressScreen({ onBack }) {
  const phrases = [
    { now: "I went to the market", was: "I am going market", date: "Apr 12" },
    { now: "Could we move the meeting to Thursday?", was: "Meeting Thursday possible?", date: "Apr 14" },
    { now: "I'm not sure I follow — could you explain?", was: "Sorry I not understand", date: "Apr 16" },
    { now: "Thanks for sharing that with me", was: "Ok, thanks", date: "Apr 19" },
    { now: "Let me think about it and get back to you", was: "I tell you later", date: "Apr 22" },
  ];

  return (
    <ScreenShell onBack={onBack}>
      <div style={{ padding: '20px 28px 8px' }}>
        <div style={{ fontFamily: SANS, fontSize: 11, letterSpacing: 2,
          textTransform: 'uppercase', color: PALETTE.muted, fontWeight: 500 }}>Quietly, you've changed</div>
        <div style={{
          fontFamily: SERIF, fontSize: 32, color: PALETTE.ink,
          marginTop: 8, lineHeight: 1.15, letterSpacing: -0.5,
        }}>
          Two weeks ago you'd say —<br/>
          <span style={{ fontStyle: 'italic', color: PALETTE.terracottaDeep }}>now you say.</span>
        </div>
      </div>

      <div style={{ padding: '24px 24px 60px' }}>
        {phrases.map((p, i) => (
          <div key={i} style={{
            background: 'rgba(255,255,255,0.55)',
            borderRadius: 18, padding: '18px 20px',
            marginBottom: 12, cursor: 'pointer',
            transition: 'transform 200ms',
          }}>
            <div style={{
              fontFamily: SERIF, fontStyle: 'italic', fontSize: 14,
              color: PALETTE.muted, textDecoration: 'line-through', textDecorationColor: 'rgba(122,111,102,0.5)',
              lineHeight: 1.4,
            }}>{p.was}</div>
            <div style={{
              fontFamily: SERIF, fontSize: 19, color: PALETTE.ink,
              marginTop: 8, lineHeight: 1.4, letterSpacing: -0.2,
              textWrap: 'pretty',
            }}>{p.now}</div>
            <div style={{
              fontFamily: SANS, fontSize: 11, color: PALETTE.muted,
              marginTop: 10, display: 'flex', alignItems: 'center', gap: 8,
              letterSpacing: 0.3,
            }}>
              <span style={{ fontSize: 14 }}>▸</span>
              Tap to hear the moment · {p.date}
            </div>
          </div>
        ))}

        <div style={{
          fontFamily: SERIF, fontStyle: 'italic', fontSize: 14,
          color: PALETTE.muted, textAlign: 'center', marginTop: 28,
          padding: '0 32px', lineHeight: 1.55,
        }}>
          No streaks. No scores. Just you, sounding more like the person you already are.
        </div>
      </div>
    </ScreenShell>
  );
}

// ─────────────────────────────────────────────────────────────
// SETTINGS
// ─────────────────────────────────────────────────────────────
function SettingsScreen({ onBack, settings, onChange }) {
  return (
    <ScreenShell onBack={onBack}>
      <div style={{ padding: '20px 28px 8px' }}>
        <div style={{
          fontFamily: SERIF, fontSize: 32, color: PALETTE.ink,
          lineHeight: 1.15, letterSpacing: -0.5,
        }}>
          Settings.
        </div>
      </div>

      <div style={{ padding: '20px 24px 60px' }}>
        <SettingsGroup label="Maya's voice">
          <SegRow value={settings.voice} options={['Indian English', 'British', 'American']} onChange={(v) => onChange({ voice: v })} />
        </SettingsGroup>

        <SettingsGroup label="Captions">
          <ToggleRow label="Show captions during call" value={settings.captions} onChange={(v) => onChange({ captions: v })} />
        </SettingsGroup>

        <SettingsGroup label="Ambient sound">
          <SegRow value={settings.ambient} options={['Off', 'Café', 'Evening']} onChange={(v) => onChange({ ambient: v })} />
        </SettingsGroup>

        <SettingsGroup label="Language safety net">
          <div style={{ padding: '8px 4px 0' }}>
            <div style={{
              fontFamily: SERIF, fontStyle: 'italic', fontSize: 13,
              color: PALETTE.muted, marginBottom: 12, lineHeight: 1.45,
            }}>
              Hold the हिं button on the call screen, say a word in your language, get it back in English.
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {['हिंदी', 'தமிழ்', 'తెలుగు', 'मराठी', 'বাংলা'].map(lang => (
                <button key={lang} onClick={() => {
                  const next = settings.langs.includes(lang)
                    ? settings.langs.filter(l => l !== lang)
                    : [...settings.langs, lang];
                  onChange({ langs: next });
                }} style={{
                  padding: '8px 14px', borderRadius: 99, border: 'none',
                  background: settings.langs.includes(lang) ? PALETTE.terracotta : 'rgba(122,93,201,0.10)',
                  color: settings.langs.includes(lang) ? PALETTE.cream : PALETTE.ink,
                  fontFamily: SERIF, fontSize: 16, cursor: 'pointer',
                }}>{lang}</button>
              ))}
            </div>
          </div>
        </SettingsGroup>

        <SettingsGroup label="Appearance">
          <SegRow value={settings.dark ? 'Dusk' : 'Day'} options={['Day', 'Dusk']} onChange={(v) => onChange({ dark: v === 'Dusk' })} />
        </SettingsGroup>

        <div style={{
          fontFamily: SERIF, fontStyle: 'italic', fontSize: 13,
          color: PALETTE.muted, textAlign: 'center', marginTop: 32, lineHeight: 1.55,
        }}>
          Five things only.<br/>The call is everything else.
        </div>
      </div>
    </ScreenShell>
  );
}

function SettingsGroup({ label, children }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <div style={{
        fontFamily: SANS, fontSize: 11, letterSpacing: 1.8,
        textTransform: 'uppercase', color: PALETTE.muted, fontWeight: 500,
        marginBottom: 10, paddingLeft: 4,
      }}>{label}</div>
      <div style={{ background: 'rgba(255,255,255,0.55)', borderRadius: 16, padding: '6px 14px' }}>
        {children}
      </div>
    </div>
  );
}

function ToggleRow({ label, value, onChange }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '12px 4px',
    }}>
      <div style={{ fontFamily: SERIF, fontSize: 16, color: PALETTE.ink }}>{label}</div>
      <button onClick={() => onChange(!value)} style={{
        width: 48, height: 28, borderRadius: 14, border: 'none', cursor: 'pointer',
        background: value ? PALETTE.terracotta : 'rgba(122,93,201,0.20)',
        position: 'relative', transition: 'background 200ms',
      }}>
        <div style={{
          width: 22, height: 22, borderRadius: '50%', background: '#fff',
          position: 'absolute', top: 3, left: value ? 23 : 3,
          transition: 'left 200ms cubic-bezier(.2,.8,.2,1)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
        }} />
      </button>
    </div>
  );
}

function SegRow({ value, options, onChange }) {
  return (
    <div style={{
      display: 'flex', gap: 4, padding: 4, margin: '8px 0',
      background: 'rgba(122,93,201,0.08)', borderRadius: 12,
    }}>
      {options.map(o => (
        <button key={o} onClick={() => onChange(o)} style={{
          flex: 1, padding: '8px 6px', borderRadius: 8, border: 'none',
          background: value === o ? '#fff' : 'transparent',
          color: PALETTE.ink, fontFamily: SERIF, fontSize: 14, cursor: 'pointer',
          boxShadow: value === o ? '0 1px 2px rgba(0,0,0,0.08)' : 'none',
          fontStyle: value === o ? 'italic' : 'normal',
        }}>{o}</button>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Shell — back chevron + cream backdrop
// ─────────────────────────────────────────────────────────────
function ScreenShell({ onBack, children }) {
  return (
    <div style={{
      width: '100%', height: '100%', position: 'relative',
      background: `linear-gradient(180deg, ${PALETTE.cream} 0%, ${PALETTE.creamSoft} 100%)`,
      overflow: 'auto',
    }}>
      {/* status bar gap */}
      <div style={{ height: 54 }} />
      <button onClick={onBack} style={{
        position: 'absolute', top: 60, left: 18, zIndex: 5,
        width: 40, height: 40, borderRadius: '50%', border: 'none',
        background: 'rgba(255,255,255,0.7)',
        backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      }}>
        <svg width="10" height="16" viewBox="0 0 10 16">
          <path d="M8 2L2 8l6 6" stroke={PALETTE.ink} strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      {children}
    </div>
  );
}

window.PeerUpScreens = {
  SplashScreen, WelcomeScreen, OnboardingScreen, CallScreen,
  MemoryScreen, PracticeScreen, ProgressScreen, SettingsScreen,
  PALETTE, SERIF, SANS,
};
