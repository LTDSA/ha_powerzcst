"""Sensor platform for PowerZCST integration."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict

import aiohttp

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_AVERAGE_USAGE,
    ATTR_BALANCE,
    ATTR_EXPECTED_REMAIN,
    ATTR_REMAIN,
    ATTR_DAILY_USAGE,
    CONF_ENDPOINT,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_ENDPOINT,
    DOMAIN,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up PowerZCST sensor based on a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    endpoint = entry.data.get(CONF_ENDPOINT, DEFAULT_ENDPOINT)

    coordinator = PowerZCSTDataUpdateCoordinator(
        hass, username=username, password=password, endpoint=endpoint
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for sensor_type in SENSOR_TYPES:
        entities.append(
            PowerZCSTSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                sensor_type=sensor_type,
                username=username,
            )
        )

    async_add_entities(entities)


class PowerZCSTDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PowerZCST data."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        password: str,
        endpoint: str,
    ) -> None:
        """Initialize the data update coordinator."""
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.session = async_get_clientsession(hass)
        self.cookies = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API endpoint."""
        # Login first to get cookies
        login_url = f"{self.endpoint}/login/?username={self.username}&password={self.password}"
        
        try:
            async with self.session.get(login_url) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to login: HTTP status %s", response.status)
                    return self.data if self.data else {}
                
                login_data = await response.json()
                if login_data.get("code") != 200:
                    _LOGGER.error("Login failed: %s", login_data.get("msg", "Unknown error"))
                    return self.data if self.data else {}
                
                # Store cookies for subsequent requests
                self.cookies = response.cookies
                
                # Now fetch the power data
                balance_url = f"{self.endpoint}/electric/balance/?detail=1"
                
                async with self.session.get(balance_url, cookies=self.cookies) as balance_response:
                    if balance_response.status != 200:
                        _LOGGER.error("Failed to get balance data: HTTP status %s", balance_response.status)
                        return self.data if self.data else {}
                    
                    balance_data = await balance_response.json()
                    
                    if balance_data.get("code") != 200:
                        _LOGGER.error("Failed to get balance data: %s", balance_data.get("msg", "Unknown error"))
                        return self.data if self.data else {}
                    
                    data = balance_data.get("data", {})
                    
                    # 获取设备名称和房间名称
                    device_name = data.get("deviceName", "未知型号")
                    room_name = data.get("roomName", f"未知房间")
                     
                    self.device_name = device_name
                    self.room_name = room_name
                     
                    return {
                        ATTR_REMAIN: data.get("remain"),
                        ATTR_BALANCE: data.get("balance"),
                        ATTR_AVERAGE_USAGE: data.get("averageUsage"),
                        ATTR_EXPECTED_REMAIN: data.get("expectedRemain"),
                        ATTR_DAILY_USAGE: data.get("dailyUsage"),
                        "device_name": device_name,
                        "room_name": room_name
                    }
        
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            _LOGGER.error("Error fetching data: %s", error)
            return self.data if self.data else {}


class PowerZCSTSensor(CoordinatorEntity, SensorEntity):
    """Representation of a PowerZCST sensor."""

    def __init__(
        self,
        coordinator: PowerZCSTDataUpdateCoordinator,
        entry_id: str,
        sensor_type: str,
        username: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry_id}_{sensor_type}"
        
        # 使用中文名称
        self._attr_name = f"{SENSOR_TYPES[sensor_type]['name_zh']}"
        
        if SENSOR_TYPES[sensor_type]["unit"] == "kWh":
            self._attr_native_unit_of_measurement = "kWh"
            self._attr_device_class = SensorDeviceClass.ENERGY

            if sensor_type == ATTR_DAILY_USAGE:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            else:
                self._attr_state_class = SensorStateClass.MEASUREMENT
        elif SENSOR_TYPES[sensor_type]["unit"] == "CNY":
            self._attr_native_unit_of_measurement = "CNY"
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif SENSOR_TYPES[sensor_type]["unit"] == "days":
            self._attr_native_unit_of_measurement = UnitOfTime.DAYS
            self._attr_state_class = SensorStateClass.MEASUREMENT
        
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=self.coordinator.data.get("room_name") if self.coordinator.data else f"未知房间",
            manufacturer="PowerZCST",
            model=self.coordinator.data.get("device_name") if self.coordinator.data else "未知型号",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type)