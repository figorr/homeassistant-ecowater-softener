from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timezone
from .const import DOMAIN, UPDATE_INTERVAL_SENSOR
from homeassistant import core  # Añadir esta línea

class EcowaterSaveUpdateIntervalButton(ButtonEntity):
    
    _attr_name = "Ecowater Save Update Interval"
    _attr_icon = "mdi:content-save"

    def __init__(self, coordinator):
        self._attr_unique_id = "ecowater_save_update_interval"
        self.entity_id = "input_button.ecowater_save_update_interval"
        self.coordinator = coordinator

    async def async_press(self) -> None:
        """Handle the button press."""
        # Establece el estado con la marca de tiempo actual en formato ISO 8601
        current_time = datetime.now(timezone.utc).isoformat()
        self.hass.states.async_set("input_button.ecowater_save_update_interval", current_time)

        # Obtén el valor del número de intervalo de actualización
        update_interval_value = self.hass.states.get("number.ecowater_update_interval")
        
        if update_interval_value:
            # Asegúrate de que update_data sea un método asincrónico
            await self.coordinator.update_data(UPDATE_INTERVAL_SENSOR, update_interval_value.state)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Ecowater button entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([EcowaterSaveUpdateIntervalButton(coordinator)])
