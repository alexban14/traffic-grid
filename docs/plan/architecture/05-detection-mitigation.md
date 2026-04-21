# 05 — Detection Mitigation & Behavioral Modeling

---

## Strategy: Advanced Fingerprint Obfuscation

Social platforms use sophisticated JavaScript-based fingerprinting to identify bots. TrafficGrid mitigates this at multiple layers.

### Browser Hardware Masking

| Dimension | Mitigation Technique |
|-----------|----------------------|
| **User Agent** | Dynamic rotation of real-world UA strings using `ua-generator`. |
| **Canvas/WebGL** | Injecting noise into `toDataURL()` and `getParameter()` outputs. |
| **AudioContext** | Adding subtle oscillators to audio fingerprints to prevent hardware identification. |
| **Fonts** | Randomizing the list of available system fonts reported via JS. |
| **WebRTC** | Disabling or masking the local IP leakage via `rtc_configuration`. |

---

## Behavioral Humanization

Standard automation moves in straight lines and clicks instantly. TrafficGrid implements "Human Jitter."

### Variable Interaction Engine

- **Curved Mouse Movement**: Using Bezier curves instead of direct coordinate jumping.
- **Natural Scrolling**: Simulating "momentum scrolling" where speed decays over time.
- **Typing Cadence**: Variable delay between keystrokes (mimicking human WPM variance).
- **Watch-Time Variance**: If a video is 60s, TrafficGrid will watch between 45s and 65s (looping or partial) to avoid suspicious 100% fixed patterns.

---

## Pattern Randomization (pgvector)

To prevent platforms from identifying "chains" of actions (e.g., Worker A always follows Worker B), we use vector embeddings.

1. **Session Embedding**: Capture successful human browsing sessions.
2. **Path Generation**: Workers query pgvector for "similar but unique" interaction paths.
3. **Execution**: The automation engine executes the retrieved path, ensuring that no two workers ever perform the exact same sequence of micro-actions.

---

## Trust Score Management

The system maintains a "Trust Score" for every Account Profile.

- **Warm-up Phase**: New accounts perform 3-5 days of low-risk activities (liking trending content, scrolling without posting).
- **Cool-down Phase**: After a high-risk action (e.g., multiple posts), the account is moved to a "hibernation" state for 24 hours.
- **Platform Integrity**: If a "Captcha" is triggered, the system automatically escalates to a human solver or a dedicated physical device session.
