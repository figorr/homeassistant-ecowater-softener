"""Ecowater Component"""
import asyncio
import logging

from homeassistant import config_entries, core
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    
    # Verificar y obtener el valor inicial del input_number
    state = hass.states.get("input_number.ecowater_update_interval")
    update_interval_value = 30  # Valor por defecto

    if state is not None:
        try:
            update_interval_value = float(state.state)
        except ValueError:
            _LOGGER.warning("El valor de input_number.ecowater_update_interval no es válido, usando 30 como valor por defecto.")
            update_interval_value = 30  # Valor por defecto si hay un error

    # Guarda el valor de update_interval para su uso posterior
    hass_data['update_interval_value'] = update_interval_value
    
    # Registrando el listener para actualizar la configuración cuando las opciones se actualicen.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Almacena una referencia a la función de desuscripción para limpiar si se descarga una entrada.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Configura las plataformas definidas en const.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, platform) for platform in PLATFORMS]
        )
    )
    # Eliminar el listener de opciones.
    hass.data[DOMAIN][entry.entry_id]["unsub_options_update_listener"]()

    # Eliminar la entrada de configuración del dominio.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
