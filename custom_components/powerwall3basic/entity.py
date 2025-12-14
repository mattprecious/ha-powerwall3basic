"""APsystems base entity."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .coordinator import PowerwallData
from .const import DOMAIN
from .api import PowerwallApi


class PowerwallEntity(Entity):
    def __init__(
        self,
        data: PowerwallData,
    ) -> None:
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.device_id)},
            name="Powerwall",
        )
