DOMAIN = "ecowater_softener"
COORDINATOR = "coordinator"
PLATFORMS = ["sensor", "number", "button"]

# Identificadores de los sensores y otros elementos
STATUS = "status"
DAYS_UNTIL_OUT_OF_SALT = "days_until_out_of_salt"
OUT_OF_SALT_ON = "out_of_salt_on"
SALT_LEVEL_PERCENTAGE = "salt_level_percentage"
WATER_USAGE_TODAY = "water_used_today"
WATER_USAGE_DAILY_AVERAGE = "water_used_per_day_average"
WATER_AVAILABLE = "water_available"
WATER_UNITS = "water_units"
RECHARGE_ENABLED = "recharge_enabled"
RECHARGE_SCHEDULED = "recharge_scheduled"
LAST_UPDATE = "last_update"
UPDATE_INTERVAL_SENSOR = "update_interval"

# Valores predeterminados y límites para el input_number
DEFAULT_UPDATE_INTERVAL = 30  # minutos
MIN_UPDATE_INTERVAL = 1
MAX_UPDATE_INTERVAL = 120
