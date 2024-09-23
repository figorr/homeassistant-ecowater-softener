from homeassistant.components.button import ButtonEntity

class EcowaterSaveUpdateIntervalButton(ButtonEntity):
    
    _attr_name = "Ecowater Save Update Interval"
    _attr_icon = "mdi:content-save"

    def __init__(self):
        self._attr_unique_id = "ecowater_save_update_interval"
        self.entity_id = "input_button.ecowater_save_update_interval"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Aquí puedes agregar el código que se ejecutará cuando el botón sea presionado.
        self.hass.states.async_set("input_button.ecowater_save_update_interval", "pressed")
