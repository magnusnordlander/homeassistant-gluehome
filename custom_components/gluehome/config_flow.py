"""Config flow for GlueHome integration."""
import logging
import voluptuous as vol
import random
import string
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from .const import *
from pygluehome.api import issue_api_key
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

# Generate a random device ID on each bootup
GLUELOCK_API_DEVICEID = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GlueHome."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        self.data = {}
        errors = {}
        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                self.data[CONF_API_KEY] = await issue_api_key(session, user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            except Exception as e:
                _LOGGER.exception("Unexpected exception")
                _LOGGER.debug(repr(e))
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=self.data
                )

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
