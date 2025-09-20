"""Constants for the PowerZCST integration."""

DOMAIN = "powerzcst"
DEFAULT_ENDPOINT = "https://api.zcst.ltdsa.cn"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_ENDPOINT = "endpoint"

ATTR_REMAIN = "remain"
ATTR_BALANCE = "balance"
ATTR_AVERAGE_USAGE = "average_usage"
ATTR_EXPECTED_REMAIN = "expected_remain"
ATTR_DAILY_USAGE = "daily_usage"
ATTR_STATUS = "status"

SENSOR_TYPES = {
    ATTR_REMAIN: {
        "name": "Remaining Power",
        "name_zh": "剩余电量",
        "unit": "kWh",
        "icon": "mdi:lightning-bolt",
    },
    ATTR_BALANCE: {
        "name": "Balance",
        "name_zh": "账户余额",
        "unit": "CNY",
        "icon": "mdi:wallet",
    },
    ATTR_AVERAGE_USAGE: {
        "name": "Average Usage",
        "name_zh": "平均用电量",
        "unit": "kWh",
        "icon": "mdi:chart-line",
    },
    ATTR_EXPECTED_REMAIN: {
        "name": "Expected Remaining Days",
        "name_zh": "预计可用天数",
        "unit": "days",
        "icon": "mdi:calendar-clock",
    },
    ATTR_DAILY_USAGE: {
        "name": "Daily Usage",
        "name_zh": "日电量",
        "unit": "kWh",
        "icon": "mdi:lightning-bolt",
    },
    ATTR_STATUS: {
        "name": "Device Status",
        "name_zh": "设备状态",
        "unit": None,
        "icon": "mdi:lan-connect",
    }
}