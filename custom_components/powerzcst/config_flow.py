"""Config flow for PowerZCST integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import CONF_ENDPOINT, CONF_PASSWORD, CONF_USERNAME, DEFAULT_ENDPOINT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    import aiohttp
    
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]
    endpoint = data.get(CONF_ENDPOINT, DEFAULT_ENDPOINT)
    
    login_url = f"{endpoint}/login/?username={username}&password={password}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(login_url) as response:
                if response.status != 200:
                    raise CannotConnect
                
                login_data = await response.json()
                
                # 检查接口返回值的 code 字段
                if login_data.get("code") != 200:
                    # 如果 code 不为 200，使用 msg 字段作为错误信息
                    error_msg = login_data.get("msg", "未知错误")
                    raise ApiError(error_msg)
                
                # 登录成功
                return {"title": f"PowerZCST: {username}"}
                
        except aiohttp.ClientError:
            raise CannotConnect


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PowerZCST."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        error_msg = None
        
        if user_input is not None:
            try:
                # 检查是否已存在相同账号的配置
                username = user_input[CONF_USERNAME]
                for entry in self._async_current_entries():
                    if entry.data.get(CONF_USERNAME) == username:
                        errors["base"] = "already_exists"
                        break
                
                # 如果没有相同账号的配置，继续验证
                if not errors:
                    info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ApiError as err:
                # 使用 API 返回的错误信息
                errors["base"] = "api_error"
                error_msg = err.error_msg
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                if not errors:
                    return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={"error_msg": error_msg} if error_msg else None
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class ApiError(HomeAssistantError):
    """Error to indicate there is an API error."""
    
    def __init__(self, error_msg: str):
        """Initialize with error message."""
        super().__init__()
        self.error_msg = error_msg