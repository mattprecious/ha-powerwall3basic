from __future__ import annotations

from dataclasses import dataclass
from pypowerwall import Powerwall

from homeassistant.core import HomeAssistant


@dataclass
class Meters:
    battery: Meter
    grid: Meter
    load: Meter
    solar: Meter


@dataclass
class Meter:
    power: float
    energy_imported: float
    energy_exported: float


class PowerwallApi:
    def __init__(self, hass: HomeAssistant, host: str, password: str) -> None:
        self.hass = hass
        self.powerwall = Powerwall(
            host, password, "tesla@example.com", "America/Toronto"
        )

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        return await self.hass.async_add_executor_job(self.powerwall.connect)

    async def get_meters(self) -> Meters | None:
        meters = await self.hass.async_add_executor_job(
            self.powerwall.poll, "/api/meters/aggregates"
        )

        if isinstance(meters, dict):
            return Meters(
                battery=_to_meter(meters["battery"]),
                grid=_to_meter(meters["site"]),
                load=_to_meter(meters["load"]),
                solar=_to_meter(meters["solar"]),
            )

        return None

    async def get_battery_level(self) -> float | None:
        level = await self.hass.async_add_executor_job(self.powerwall.level, True)
        if level:
            return float(level)

        return None

    async def is_grid_connected(self) -> bool | None:
        status = await self.hass.async_add_executor_job(
            self.powerwall.grid_status, "numeric"
        )

        if status:
            return status == 1

        return None


def _to_meter(data: dict) -> Meter:
    return Meter(
        power=data["instant_power"],
        energy_exported=data["energy_exported"],
        energy_imported=data["energy_imported"],
    )
