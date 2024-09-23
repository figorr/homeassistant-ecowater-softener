from datetime import datetime, timedelta
import re
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_state_change

from ecowater_softener import Ecowater

from .const import (
    STATUS,
    DAYS_UNTIL_OUT_OF_SALT,
    OUT_OF_SALT_ON,
    SALT_LEVEL_PERCENTAGE,
    WATER_USAGE_TODAY,
    WATER_USAGE_DAILY_AVERAGE,
    WATER_AVAILABLE,
    WATER_UNITS,
    RECHARGE_ENABLED,
    RECHARGE_SCHEDULED,
    LAST_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

class EcowaterDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ecowater data."""

    def __init__(self, hass, username, password, serialnumber, dateformat):
        """Initialize Ecowater coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ecowater " + serialnumber,
            update_interval=timedelta(minutes=30),  # Default value
        )
        self._username = username
        self._password = password
        self._serialnumber = serialnumber
        self._dateformat = dateformat
        self._last_update = None

        # Subscribe to changes in the input_button
        async_track_state_change(
            hass,
            "input_button.ecowater_save_interval",
            self._handle_save_interval
        )

    async def _handle_save_interval(self, entity_id, old_state, new_state):
        """Handle the input_button press to save the update interval."""
        try:
            # Get the value from input_number
            input_interval = self.hass.states.get("input_number.ecowater_update_interval")
            if input_interval is not None:
                new_interval = int(float(input_interval.state))
                self.update_interval = timedelta(minutes=new_interval)
                _LOGGER.info(f"Update interval set to {new_interval} minutes.")
            else:
                # Fallback to default value if input_number is not available
                self.update_interval = timedelta(minutes=30)
                _LOGGER.error("Failed to get input_number.ecowater_update_interval state. Reverting to default 30 minutes interval.")
            
            # Force an update to apply the new interval immediately
            await self.async_request_refresh()
            
        except ValueError:
            # Fallback to default value if there's an invalid input
            self.update_interval = timedelta(minutes=30)
            _LOGGER.error("Invalid value for input_number.ecowater_update_interval. Reverting to default 30 minutes interval.")

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            data = {}

            ecowaterDevice = Ecowater(self._username, self._password, self._serialnumber)
            data_json = await self.hass.async_add_executor_job(lambda: ecowaterDevice._get())

            nextRecharge_re = r"device-info-nextRecharge'\)\.html\('(?P<nextRecharge>.*)'"

            data[STATUS] = 'Online' if data_json['online'] else 'Offline'
            
            # Handle the "Offline" status
            if data[STATUS] == 'Offline':
                _LOGGER.warning("The Ecowater device is Offline. Connection date and data won't be updated.")
                # Keep the last successful update if the device is Offline
                if self._last_update:
                    data[LAST_UPDATE] = self._last_update
                else:
                    data[LAST_UPDATE] = "Failed Connection"  # If it's the first time and the device is Offline
                return data

            data[DAYS_UNTIL_OUT_OF_SALT] = data_json['out_of_salt_days']

            # Checks if date is 'today' or 'tomorrow'
            if str(data_json['out_of_salt']).lower() == 'today':
                data[OUT_OF_SALT_ON] = datetime.today().strftime('%Y-%m-%d')
            elif str(data_json['out_of_salt']).lower() == 'tomorrow':
                data[OUT_OF_SALT_ON] = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif str(data_json['out_of_salt']).lower() == 'yesterday':
                data[OUT_OF_SALT_ON] = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            elif self._dateformat == "dd/mm/yyyy":
                data[OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%d/%m/%Y').strftime('%d-%m-%Y')
            elif self._dateformat == "mm/dd/yyyy":
                data[OUT_OF_SALT_ON] = datetime.strptime(data_json['out_of_salt'], '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                data[OUT_OF_SALT_ON] = ''
                _LOGGER.exception("Error: Date format not set")

            data[SALT_LEVEL_PERCENTAGE] = data_json['salt_level_percent']
            data[WATER_USAGE_TODAY] = data_json['water_today']
            data[WATER_USAGE_DAILY_AVERAGE] = data_json['water_avg']
            data[WATER_AVAILABLE] = data_json['water_avail']
            data[WATER_UNITS] = str(data_json['water_units'])
            data[RECHARGE_ENABLED] = data_json['rechargeEnabled']
            data[RECHARGE_SCHEDULED] = re.search(nextRecharge_re, data_json['recharge']).group('nextRecharge') != 'Not Scheduled'

            # Update the last time when data is received from the API, according to date format.
            now = datetime.now()
            if self._dateformat == "dd/mm/yyyy":
                self._last_update = now.strftime('%d-%m-%Y - %H:%M')
            elif self._dateformat == "mm/dd/yyyy":
                self._last_update = now.strftime('%m-%d-%Y - %H:%M')
            else:
                self._last_update = now.strftime('%d-%m-%Y - %H:%M')
                _LOGGER.exception("Error: Date format not set for last update")

            data[LAST_UPDATE] = self._last_update
            
            return data

        except Exception as e:
            # Checks if the error is because you reached the limit of API Calls
            if "429" in str(e) or "Too Many Requests" in str(e):
                _LOGGER.error("You reached the limit of API Calls. The connection has been temporary blocked.")
            else:
                _LOGGER.error(f"Error communicating with API: {e}")

            # In case of error, It keeps the last successful connection date or sets "Failed Connection" if it is the first time
            if self._last_update:
                data[LAST_UPDATE] = self._last_update
            else:
                data[LAST_UPDATE] = "Failed Connection"
                
            raise UpdateFailed(f"Error communicating with API: {e}")
