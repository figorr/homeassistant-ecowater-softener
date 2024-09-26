"""Ecowater Component"""
import asyncio
import logging

from homeassistant import config_entries, core

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Obtener datos de la entrada
    username = entry.data.get("username")
    password = entry.data.get("password")
    serialnumber = entry.data.get("serialnumber")
    dateformat = entry.data.get("dateformat")

    # Instanciar el number entity
    number_entity = EcowaterUpdateInterval(hass, serialnumber, DEFAULT_UPDATE_INTERVAL)

    # Crear el coordinador
    coordinator = EcowaterDataCoordinator(hass, username, password, serialnumber, dateformat, number_entity)

    # Asegúrate de que el coordinador se inicie adecuadamente
    await coordinator.async_config_entry_first_refresh()

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number"])

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
            ]
        )
    )
    # Remove options_update_listener.
    hass.data[DOMAIN][entry.entry_id]["unsub_options_update_listener"]()

    # Remove config entry from domain.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
