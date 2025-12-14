from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta

from .api import Meter, PowerwallApi
from .const import DOMAIN, LOGGER

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


@dataclass
class PowerwallSensorData:
    battery: Meter
    grid: Meter
    load: Meter
    solar: Meter
    battery_level: float
    grid_connected: bool


@dataclass
class PowerwallData:
    device_id: str
    coordinator: PowerwallDataCoordinator


type PowerwallConfigEntry = ConfigEntry[PowerwallData]


class PowerwallDataCoordinator(DataUpdateCoordinator[PowerwallSensorData]):
    config_entry: PowerwallConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: PowerwallConfigEntry,
        api: PowerwallApi,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name="Powerwall Data",
            update_interval=timedelta(seconds=10),
        )
        self.api = api

    async def _async_setup(self) -> None:
        if not await self.api.authenticate():
            raise UpdateFailed from None

    async def _async_update_data(self) -> PowerwallSensorData:
        async with asyncio.TaskGroup() as tg:
            meters_task = tg.create_task(self.api.get_meters())
            battery_task = tg.create_task(self.api.get_battery_level())
            grid_task = tg.create_task(self.api.is_grid_connected())

        meters = meters_task.result()
        battery_level = battery_task.result()
        grid_connected = grid_task.result()

        if meters is None or battery_level is None or grid_connected is None:
            raise UpdateFailed from None

        return PowerwallSensorData(
            battery=meters.battery,
            grid=meters.grid,
            load=meters.load,
            solar=meters.solar,
            battery_level=battery_level,
            grid_connected=grid_connected,
        )
