"""Ecowater Component"""
import asyncio
import logging

from homeassistant import config_entries, core
from .coordinator import EcowaterDataCoordinator  # Asegúrate de importar tu clase de coordinador
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    
    # Crea e inicializa el coordinador
    coordinator = EcowaterDataCoordinator(
        hass, 
        entry.data['username'], 
        entry.data['password'], 
        entry.data['serialnumber'], 
        entry.data['dateformat']
    )
    
    # Realiza la primera actualización del coordinador
    await coordinator.async_config_entry_first_refresh()

    # Almacena el coordinador en hass.data para que esté disponible para las otras plataformas
    hass_data["coordinator"] = coordinator

    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Forward the setup to the sensor, number, and button platforms.
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "button"])
    
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
            *[
                hass.config_entries.async_forward_entry_unload(entry, "sensor"),
                hass.config_entries.async_forward_entry_unload(entry, "number"),
                hass.config_entries.async_forward_entry_unload(entry, "button"),
            ]
        )
    )
    # Remove options_update_listener.
    hass.data[DOMAIN][entry.entry_id]["unsub_options_update_listener"]()

    # Remove config entry from domain.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
