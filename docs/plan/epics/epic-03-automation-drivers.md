# Epic 03 — Platform Automation Drivers

**Goal:** Implement the platform-specific bypass and automation logic for TikTok and YouTube.

**Estimated Duration:** 2 weeks
**Status:** IN PROGRESS — TikTok view with playback verification, YouTube stub only

---

## Task Summary

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E03-T01 | Stealth Browser Init | Done | Playwright + `playwright-stealth` v2.0.3, anti-automation flags disabled |
| E03-T02 | Human Jitter Engine | Done | `BehavioralDNA`: Bezier scrolling, weighted dwell, real DOM interactions (like, comment, pause) |
| E03-T03 | TikTok View Logic | Done | Full playback verification, cookie/login popup dismissal, duration-aware watching |
| E03-T04 | YouTube Watch Logic | Stub | `YouTubeBrowserDriver` exists but not tested with real URLs |
| E03-T05 | Appium Physical Driver | Not Started | Waiting for ADB setup on HP Z420 + physical device connectivity |

## Architecture

```
PlatformDriver (ABC)
├── execute_view(url, identity, proxy) → bool
├── execute_warmup(identity, duration) → bool
└── log(message) → broadcast to WebSocket

TikTokBrowserDriver(PlatformDriver)
├── _dismiss_popups(page)         → cookie consent + login modal
├── _wait_for_video_playback(page) → verify <video> is actually playing
├── _get_video_duration(page)     → read video.duration from DOM
├── _watch_video(page)            → duration-aware watch (70-110% of video)
├── scrape_profile_videos(url, max) → extract video URLs from profile page
└── execute_view(url, identity, proxy)
    → launch stealth browser → navigate → dismiss popups
    → verify playback → watch video → scroll → curiosity action

YouTubeBrowserDriver(PlatformDriver)
└── Stub — same interface, different selectors (not yet implemented)

Orchestrator Tasks
├── browser_view_boost    → single video view (identity + proxy + driver)
├── browser_profile_boost → scrape profile → fan out N view tasks
└── mobile_warmup         → stub

DriverRegistry
├── "tiktok_views"         → TikTokBrowserDriver
├── "tiktok_profile_boost" → TikTokBrowserDriver
├── "tiktok_warmup"        → TikTokBrowserDriver
└── "yt_watchtime"         → YouTubeBrowserDriver
```

## TikTok Driver Capabilities (v2, 2026-04-21)

### Video Playback Verification
- Waits for `<video>` element in DOM
- Checks `video.paused === false && video.readyState >= 2`
- Falls back to clicking the video element to trigger play
- Polls for up to 15 seconds before proceeding

### Duration-Aware Watching
- Reads `video.duration` from the DOM
- Watches 70-110% of the video length (randomized)
- Caps at 90 seconds, minimum 5 seconds
- Falls back to 10-45s random dwell if duration unavailable
- Periodically checks if video is still playing, clicks to resume if paused

### Popup Handling
- Cookie consent: scans multiple selectors ("Accept all", "Accept All", etc.)
- Login modals: dismisses via close button / aria-label
- Both handled before playback verification

### Stealth Features
- `playwright-stealth` Stealth class applied to page
- `--disable-blink-features=AutomationControlled` flag
- Custom viewport (1920x1080), locale (en-US), timezone (Europe/Bucharest)
- Random user agent from identity profile

### Behavioral Humanization (BehavioralDNA)
- **Scroll**: Bezier-curved, non-linear momentum with horizontal jitter
- **Like**: Clicks `[data-e2e="like-icon"]` (15% chance)
- **Comment check**: Opens comments panel, scrolls through 1-3 comments (20% chance)
- **Pause/unpause**: Clicks video to pause then resume (10% chance)
- **Nothing**: 55% chance (realistic — most viewers just watch)

### URL Support
- Full TikTok URLs: `https://www.tiktok.com/@user/video/123`
- Short links: `https://vm.tiktok.com/abc/` (follows redirect automatically)
- Profile URLs: `https://www.tiktok.com/@user` (profile boost scrapes all videos)

### Profile Boost (`tiktok_profile_boost`)
- Navigates to profile page with stealth browser
- Scrolls to load video grid (3 scroll passes)
- Extracts `<a href="/video/...">` links from DOM (up to `max_videos`, default 20)
- Creates individual `tiktok_views` child tasks for each video found
- `volume` parameter controls views per video
- Parent task records `videos_found`, `tasks_created`, `child_task_ids` in result JSON
- Fan-out: all child tasks queued to Celery for parallel execution across workers

## Execution History

| Task | URL | Duration | Status | Notes |
|------|-----|----------|--------|-------|
| 1 | tiktok.com/test | 4.8s | FAILED | Fake proxy (192.168.1.100) |
| 2 | tiktok.com/@tiktok | 66s | SUCCESS | 47s dwell + like interaction |
| 4 | vm.tiktok.com/ZNRqx3wvK/ | 42s | SUCCESS | Short link, 24s dwell |
| 6 | vm.tiktok.com/ZNRqxWjWk/ | 48s | SUCCESS | 29s dwell |

## Known Limitations

- Views may not register because previous driver did NOT verify video playback — fixed in v2
- No cookie/session persistence between views — each view is a fresh session
- Single IP without proxy rotation — TikTok may deduplicate same-IP views
- No "For You" feed simulation before target navigation
- Curiosity actions use TikTok DOM selectors that may change with UI updates
