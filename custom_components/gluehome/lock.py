"""Support for GlueHome locks."""
import logging
from datetime import timedelta

from pygluehome.lock import (
    GlueHomeLock as LibGlueHomeLock,
    GlueHomeLockConnectionStatus,
    GlueHomeLockEventType
)
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    hub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    async for lock in hub.lock_generator:
        new_devices.append(GlueHomeLock(hass, lock))

    if new_devices:
        async_add_devices(new_devices)


class GlueHomeLock(LockEntity):
    """Glue Locks"""

    def __init__(self, hass: HomeAssistant, lock: LibGlueHomeLock):
        """Initialize the Glue Lock."""
        self._hass = hass
        self.device = lock
        if self.device.last_lock_event is not None:
            self._last_event_fired = self.device.last_lock_event.datetime
        else:
            self._last_event_fired = None
        _LOGGER.debug(repr(self.device))

        if self.device.description is not None:
            self._name = "{}".format(self.device.description)
        else:
            # In case there is no name defined, use the device id
            self._name = "{}".format(self.device.lock_id)

        self.att_data = {}

    async def async_added_to_hass(self) -> None:
        pass

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True

    async def async_update(self):
        await self.device.refresh()
        self._maybe_fire_event()
        _LOGGER.debug(repr(self.device))

    @property
    def unique_id(self) -> str:
        """Return an unique ID."""
        return self.device.lock_id

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self) -> str:
        """Get the state of the device."""
        if not self.available:
            return STATE_UNAVAILABLE

        if self.device.last_lock_event is None:
            return STATE_UNKNOWN

        return {
            GlueHomeLockEventType.local_lock: STATE_LOCKED,
            GlueHomeLockEventType.manual_lock: STATE_LOCKED,
            GlueHomeLockEventType.remote_lock: STATE_LOCKED,
            GlueHomeLockEventType.press_and_go: STATE_LOCKED,
            GlueHomeLockEventType.local_unlock: STATE_UNLOCKED,
            GlueHomeLockEventType.remote_unlock: STATE_UNLOCKED,
            GlueHomeLockEventType.manual_unlock: STATE_UNLOCKED,
        }[self.device.last_lock_event.event_type]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.device.connection_status == GlueHomeLockConnectionStatus.connected

    @property
    def battery_level(self):
        """Return the battery level of the lock."""
        return self.device.battery_status

    async def async_lock(self):
        """Lock the lock."""
        await self.device.lock()
        self._maybe_fire_event()
        self.schedule_update_ha_state()

    async def async_unlock(self):
        """Unlock the lock."""
        await self.device.unlock()
        self._maybe_fire_event()
        self.schedule_update_ha_state()

    def _maybe_fire_event(self):
        if self.device.last_lock_event is None:
            return

        if self._last_event_fired is not None and self.device.last_lock_event.datetime <= self._last_event_fired:
            return

        event_data = {
            "device_id": self.entity_id,
            "type": str(self.device.last_lock_event.event_type),
            "datetime": self.device.last_lock_event.datetime
        }
        self._hass.bus.async_fire("gluehome_event", event_data)
        self._last_event_fired = self.device.last_lock_event.datetime

    @property
    def device_state_attributes(self) -> dict:
        """Return the state attributes."""
        attributes = {}
        attributes[ATTR_DEVICE_ID] = self.device.lock_id
        attributes[ATTR_SERIAL_NO] = self.device.serial_number
        attributes[ATTR_FIRMWARE_VERSION] = self.device.firmware_version
        attributes[ATTR_BATTERY_LEVEL] = str(self.battery_level) + "%"
        return attributes
