from dataclasses import dataclass
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo
from .const import DEFAULT_UPDATE_INTERVAL, MIN_UPDATE_INTERVAL, MAX_UPDATE_INTERVAL, DOMAIN

@dataclass
class EcowaterNumberEntityDescription:
    """Class for keeping track of an Ecowater number entity description."""
    key: str
    translation_key: str
    icon: str
    native_min_value: float = MIN_UPDATE_INTERVAL
    native_max_value: float = MAX_UPDATE_INTERVAL
    native_step: float = 1.0


NUMBER_TYPES: tuple[EcowaterNumberEntityDescription, ...] = (
    EcowaterNumberEntityDescription(
        key="UPDATE_INTERVAL",
        translation_key="update_interval",
        icon="mdi:update",
        native_min_value=MIN_UPDATE_INTERVAL,
        native_max_value=MAX_UPDATE_INTERVAL,
        native_step=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    serialnumber = coordinator.data.get("serialnumber")

    if serialnumber:
        async_add_entities([EcowaterUpdateInterval(coordinator, entry, serialnumber)])


class EcowaterUpdateInterval(NumberEntity):
    entity_description: EcowaterNumberEntityDescription

    def __init__(self, coordinator: DataUpdateCoordinator, config_entry: ConfigEntry, serialnumber: str):
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._serialnumber = serialnumber

        # Buscar la descripción de la entidad
        self.entity_description = next(
            (desc for desc in NUMBER_TYPES if desc.key == "update_interval"), None
        )

        self._attr_unique_id = f"ecowater_{serialnumber.lower()}_update_interval"
        self.entity_id = f"number.ecowater_{serialnumber.lower()}_update_interval"
        
        # Establecer el valor inicial
        self._attr_native_value = self.coordinator.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)

        # Establecer atributos basados en la descripción
        if self.entity_description:
            self._attr_name = self.entity_description.translation_key
            self._attr_icon = self.entity_description.icon
            self._attr_native_min_value = self.entity_description.native_min_value
            self._attr_native_max_value = self.entity_description.native_max_value
            self._attr_native_step = self.entity_description.native_step
            self._attr_native_unit_of_measurement = "min"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serialnumber)},
            name=f"Ecowater {self._serialnumber}",
            manufacturer="Ecowater",
        )

    async def async_set_native_value(self, value: float) -> None:
        """Handle setting the value."""
        self._attr_native_value = value
        self.async_write_ha_state()

        # Actualizar el intervalo en el coordinador
        self.coordinator._attr_update_interval = value  # Actualizar el intervalo en minutos
