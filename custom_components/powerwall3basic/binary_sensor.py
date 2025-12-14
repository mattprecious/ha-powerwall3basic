from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import (
    PowerwallConfigEntry,
    PowerwallData,
    PowerwallDataCoordinator,
    PowerwallSensorData,
)
from .entity import PowerwallEntity


@dataclass(frozen=True, kw_only=True)
class PowerwallBinarySensorDescription(BinarySensorEntityDescription):
    is_on: Callable[[PowerwallSensorData], bool | None]


BINARY_SENSORS: tuple[PowerwallBinarySensorDescription, ...] = (
    PowerwallBinarySensorDescription(
        name="Grid Connected",
        key="grid_connected",
        translation_key="grid_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        is_on=lambda data: data.grid_connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PowerwallConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = config_entry.runtime_data
    async_add_entities(
        PowerwallBinarySensorWithDescription(
            data=data,
            entity_description=desc,
        )
        for desc in BINARY_SENSORS
    )


class PowerwallBinarySensorWithDescription(
    CoordinatorEntity[PowerwallDataCoordinator], PowerwallEntity, BinarySensorEntity
):
    """Base binary sensor to be used with description."""

    entity_description: PowerwallBinarySensorDescription

    def __init__(
        self,
        data: PowerwallData,
        entity_description: PowerwallBinarySensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(data.coordinator)
        PowerwallEntity.__init__(self, data)
        self.entity_description = entity_description
        self._attr_unique_id = f"{data.device_id}_{entity_description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return value of sensor."""
        return self.entity_description.is_on(self.coordinator.data)
