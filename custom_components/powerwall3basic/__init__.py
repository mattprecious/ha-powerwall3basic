"""The Tesla Powerwall 3 (Basic) integration."""

from __future__ import annotations

from homeassistant.const import Platform, CONF_HOST, CONF_PASSWORD, CONF_ID
from homeassistant.core import HomeAssistant

from .coordinator import PowerwallConfigEntry, PowerwallData, PowerwallDataCoordinator
from .api import PowerwallApi

_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: PowerwallConfigEntry) -> bool:
    """Set up Tesla Powerwall 3 (Basic) from a config entry."""

    api = PowerwallApi(hass, entry.data[CONF_HOST], entry.data[CONF_PASSWORD])
    coordinator = PowerwallDataCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    data = PowerwallData(entry.data[CONF_ID], coordinator)
    entry.runtime_data = data

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PowerwallConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
