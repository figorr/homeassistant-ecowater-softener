from homeassistant.components.number import NumberEntity

class EcowaterUpdateInterval(NumberEntity):
    
    _attr_name = "Ecowater Update Interval"
    _attr_icon = "mdi:update"
    _attr_native_value = 30  # Valor inicial
    _attr_editable = True
    _attr_mode = 'slider'
    _attr_native_min_value = 1  # Valor mínimo
    _attr_native_max_value = 120  # Valor máximo
    _attr_native_step = 1  # Paso
    _attr_native_unit_of_measurement = "min"  # Unidad de medida

    def __init__(self):
        self._attr_unique_id = "ecowater_update_interval"
        self.entity_id = "input_number.ecowater_update_interval"

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
