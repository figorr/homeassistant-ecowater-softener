from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DEFAULT_UPDATE_INTERVAL, MIN_UPDATE_INTERVAL, MAX_UPDATE_INTERVAL

class EcowaterUpdateInterval(NumberEntity):
    
    _attr_name = "Ecowater Update Interval"
    _attr_icon = "mdi:update"
    _attr_native_value = DEFAULT_UPDATE_INTERVAL  # Valor inicial por defecto de const.py
    _attr_editable = True
    _attr_mode = 'slider'
    _attr_native_min_value = MIN_UPDATE_INTERVAL  # Valor mínimo de const.py
    _attr_native_max_value = MAX_UPDATE_INTERVAL  # Valor máximo de const.py
    _attr_native_step = 1  # Paso
    _attr_native_unit_of_measurement = "min"  # Unidad de medida

    def __init__(self):
        self._attr_unique_id = "ecowater_update_interval"
        self.entity_id = "number.ecowater_update_interval"  # Cambiado a "number"

    @property
    def native_value(self):      
        return self._attr_native_value

    async def async_set_native_value(self, value):        
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def native_min_value(self):        
        return self._attr_native_min_value

    @property
    def native_max_value(self):
        return self._attr_native_max_value

    @property
    def native_step(self):
        return self._attr_native_step

    @property
    def mode(self):        
        return self._attr_mode

    @property
    def native_unit_of_measurement(self):
        return self._attr_native_unit_of_measurement

async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Ecowater number entity."""
    async_add_entities([EcowaterUpdateInterval()])
