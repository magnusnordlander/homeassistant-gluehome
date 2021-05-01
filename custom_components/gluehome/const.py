from homeassistant.components.lock import (
    PLATFORM_SCHEMA,
    STATE_LOCKED,
    STATE_UNLOCKED,
    LockEntity,
)

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
    ATTR_DEVICE_ID,
    CONF_API_KEY,
)
ATTR_SERIAL_NO = "serial"
ATTR_FIRMWARE_VERSION = "firmware"

DOMAIN = "gluehome"
INTEGRATION_VERSION = "main"
ISSUE_URL = "https://github.com/magnusnordlander/homeassistant-gluehome/issues"

STARTUP = f"""
-------------------------------------------------------------------
{DOMAIN}
Version: {INTEGRATION_VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

GLUELOCK_DEVICES = f"{DOMAIN}_devices"