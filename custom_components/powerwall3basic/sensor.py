from __future__ import annotations

import homeassistant.const
from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PowerwallConfigEntry
from .coordinator import PowerwallData, PowerwallDataCoordinator, PowerwallSensorData
from .const import DOMAIN
from .entity import PowerwallEntity
from .api import PowerwallApi


@dataclass(frozen=True, kw_only=True)
class PowerwallSensorDescription(SensorEntityDescription):
    value_fn: Callable[[PowerwallSensorData], float | None]


SENSORS: tuple[PowerwallSensorDescription, ...] = (
    PowerwallSensorDescription(
        name="Battery Power",
        key="battery_power",
        translation_key="battery_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.battery.power,
    ),
    PowerwallSensorDescription(
        name="Battery Discharged",
        key="battery_discharged",
        translation_key="battery_discharged",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.battery.energy_exported,
    ),
    PowerwallSensorDescription(
        name="Battery Charged",
        key="battery_charged",
        translation_key="battery_charged",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.battery.energy_imported,
    ),
    PowerwallSensorDescription(
        name="Grid Power",
        key="grid_power",
        translation_key="grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.grid.power,
    ),
    PowerwallSensorDescription(
        name="Grid Exported",
        key="grid_exported",
        translation_key="grid_exported",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.grid.energy_exported,
    ),
    PowerwallSensorDescription(
        name="Grid Imported",
        key="grid_imported",
        translation_key="grid_imported",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.grid.energy_imported,
    ),
    PowerwallSensorDescription(
        name="Home Power",
        key="home_power",
        translation_key="home_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.load.power,
    ),
    PowerwallSensorDescription(
        name="Home Usage",
        key="home_usage",
        translation_key="home_usage",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.load.energy_imported,
    ),
    PowerwallSensorDescription(
        name="Solar Power",
        key="solar_power",
        translation_key="solar_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.solar.power,
    ),
    PowerwallSensorDescription(
        name="Solar Generated",
        key="solar_generated",
        translation_key="solar_generated",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.solar.energy_exported,
    ),
    PowerwallSensorDescription(
        name="Battery Level",
        key="battery_level",
        translation_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.battery_level,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PowerwallConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = config_entry.runtime_data
    async_add_entities(
        PowerwallSensorWithDescription(
            data=data,
            entity_description=desc,
        )
        for desc in SENSORS
    )


class PowerwallSensorWithDescription(
    CoordinatorEntity[PowerwallDataCoordinator], PowerwallEntity, SensorEntity
):
    """Base sensor to be used with description."""

    entity_description: PowerwallSensorDescription
    data: PowerwallData
    _attr_has_entity_name = True

    def __init__(
        self,
        data: PowerwallData,
        entity_description: PowerwallSensorDescription,
    ) -> None:
        super().__init__(data.coordinator)
        PowerwallEntity.__init__(self, data)
        self.entity_description = entity_description
        self.data = data
        self._attr_unique_id = f"{data.device_id}_{entity_description.key}"

    @property
    def native_value(self) -> StateType:
        """Return value of sensor."""
        return self.entity_description.value_fn(self.data.coordinator.data)
