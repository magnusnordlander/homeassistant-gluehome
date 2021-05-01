import logging
import threading

from pygluehome.api import GlueHomeApi
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import *

_LOGGER = logging.getLogger(__name__)


class GlueHomeHub:
    """GlueHome Hub"""

    def __init__(self, hass: HomeAssistant, domain_config):
        """Initialize the GlueHome lock."""

        self.config = domain_config
        self._lock = threading.Lock()
        self.hass = hass

        session = async_get_clientsession(hass)

        api_key = domain_config.get(CONF_API_KEY)

        self.gluehome_api = GlueHomeApi(session, api_key)

        self.lock_generator = self.gluehome_api.all_locks()

        _LOGGER.debug("Hub initialized")

    def disconnect(self):
        pass

    @property
    def name(self):
        """ Return the name of the hub."""
        return "GlueHome Hub"