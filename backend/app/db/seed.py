"""
Database seeder — creates realistic identities and placeholder proxies.

Run manually:  python -m app.db.seed
Auto-run:      called from entrypoint.sh after migrations
"""

import random
import logging
from sqlmodel import Session, select
from app.db.session import engine
from app.models.identity import Identity, Proxy
from app.services.behavioral_dna import BehavioralDNA

logger = logging.getLogger(__name__)

# Realistic Romanian first + last name combos
RO_FIRST_NAMES = [
    "andrei", "maria", "alex", "elena", "mihai", "ana", "stefan",
    "ioana", "cristian", "raluca", "gabriel", "diana", "vlad",
    "adriana", "tudor", "alina", "radu", "bianca", "cosmin", "laura",
    "dan", "simona", "bogdan", "catalina", "florin", "madalina",
    "ionut", "alexandra", "dragos", "denisa",
]

RO_LAST_NAMES = [
    "pop", "ionescu", "popa", "stan", "rusu", "dumitru", "marin",
    "stoica", "gheorghe", "matei", "ciobanu", "moldovan", "lazar",
    "nistor", "barbu", "dobre", "neagu", "vasile", "serban", "rada",
]

# Username patterns real people use (no obvious bot patterns)
USERNAME_PATTERNS = [
    "{first}{last}{yr}",
    "{first}.{last}",
    "{first}_{last}{num}",
    "{first}{last}",
    "{first}.{last}{yr}",
    "{first}_{num}{last}",
    "the.{first}.{last}",
    "{first}{last}_ro",
    "{first}.{num}",
    "{last}.{first}{yr}",
]

# Real-world user agents (Chrome, Firefox, Safari, mobile)
USER_AGENTS = [
    # Desktop Chrome (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Desktop Chrome (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Desktop Chrome (Linux)
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Mobile Android
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.80 Mobile Safari/537.36",
    # Mobile iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.80 Mobile/15E148 Safari/604.1",
]

SCREEN_RESOLUTIONS = [
    "1920x1080", "2560x1440", "1366x768", "1536x864",
    "1440x900", "1280x720", "3840x2160", "390x844",  # mobile
    "412x915", "360x800", "414x896",  # mobile
]


def _generate_username() -> str:
    first = random.choice(RO_FIRST_NAMES)
    last = random.choice(RO_LAST_NAMES)
    yr = str(random.randint(90, 9))  # 90-09 (birth year suffix)
    if int(yr) < 10:
        yr = f"0{yr}"
    num = str(random.randint(1, 999))
    pattern = random.choice(USERNAME_PATTERNS)
    return pattern.format(first=first, last=last, yr=yr, num=num)


def seed_identities(session: Session, count: int = 20, platform: str = "tiktok"):
    """Create realistic bot identities. Skips if enough already exist."""
    existing = session.exec(
        select(Identity).where(Identity.platform == platform)
    ).all()

    needed = count - len(existing)
    if needed <= 0:
        logger.info(f"Already have {len(existing)} {platform} identities, skipping seed")
        return

    logger.info(f"Seeding {needed} new {platform} identities...")
    created = 0
    attempts = 0

    while created < needed and attempts < needed * 3:
        attempts += 1
        username = _generate_username()

        # Check uniqueness
        exists = session.exec(
            select(Identity).where(Identity.username == username)
        ).first()
        if exists:
            continue

        identity = Identity(
            username=username,
            platform=platform,
            status="active",
            user_agent=random.choice(USER_AGENTS),
            screen_resolution=random.choice(SCREEN_RESOLUTIONS),
            trust_score=random.randint(40, 80),
            behavioral_dna=BehavioralDNA.generate_behavior_vector(),
        )
        session.add(identity)
        created += 1

    session.commit()
    logger.info(f"Created {created} new {platform} identities")


def seed_proxies(session: Session):
    """Create placeholder proxy entries. Skips if any exist."""
    existing = session.exec(select(Proxy)).all()
    if existing:
        logger.info(f"Already have {len(existing)} proxies, skipping seed")
        return

    logger.info("Seeding placeholder proxies...")
    proxies = [
        Proxy(ip_address="192.168.1.100", port=8080, protocol="socks5", provider="Digi RO", is_active=False),
        Proxy(ip_address="192.168.1.101", port=8080, protocol="socks5", provider="Orange RO", is_active=False),
    ]
    for p in proxies:
        session.add(p)
    session.commit()
    logger.info("Seeded 2 placeholder proxies (inactive)")


def run_seed():
    """Run all seeders."""
    with Session(engine) as session:
        seed_identities(session, count=20, platform="tiktok")
        seed_identities(session, count=10, platform="youtube")
        seed_proxies(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_seed()
