import os

def GetTokens():
    tokens = os.environ.get("TEST_TG_TOKENS")
    if not tokens:
        raise RuntimeError("TEST_TG_TOKENS environment variable is not set or empty")
    return [t for t in tokens.split(",") if t.strip()]

def GetChannel():
    channel = os.environ.get("TEST_TG_CHANNEL")
    if not channel:
        raise RuntimeError("TEST_TG_CHANNEL environment variable is not set or empty")
    return channel
