from homeassistant.components.button import ButtonEntity
from datetime import datetime, timezone

class EcowaterSaveUpdateIntervalButton(ButtonEntity):
    
    _attr_name = "Ecowater Save Update Interval"
    _attr_icon = "mdi:content-save"

    def __init__(self):
        self._attr_unique_id = "ecowater_save_update_interval"
        self.entity_id = "input_button.ecowater_save_update_interval"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Establece el estado con la marca de tiempo actual en formato ISO 8601 utilizando un objeto consciente de la zona horaria
        current_time = datetime.now(timezone.utc).isoformat()
        self.hass.states.async_set("input_button.ecowater_save_update_interval", current_time)
