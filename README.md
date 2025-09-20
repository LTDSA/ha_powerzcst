# PowerZCST Integration for Home Assistant

PowerZCST Integration is an integrated component of Home Assistant. It allows you to check electricity status in Home Assistant.

## Installation

### Method 1: HACS

One-click installation from HACS:

[![Open your Home Assistant instance and open the PowerZCST integration inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=LTDSA&repository=ha_powerzcst&category=integration)

### Method 2: Manually installation via [Samba](https://github.com/home-assistant/addons/tree/master/samba) / [FTPS](https://github.com/hassio-addons/addon-ftp)

Download and copy `custom_components/powerzcst` folder to `config/custom_components` folder in your Home Assistant.

## Configuration

### Login

Settings > Devices & services > ADD INTEGRATION > Search `PowerZCST`  > Sign in with PowerZCST account

### Add Devices

After logging in successfully, the device will be automatically import to Home Assistant.

### Multiple User Login

After a PowerZCST account login and its user configuration are completed, you can continue to add other PowerZCST accounts in the configured PowerZCST Integration page.

Method: Settings > Devices & services > Configured > PowerZCST > ADD ITEM > Sign in with PowerZCST account

[![Open your Home Assistant instance and show PowerZCST integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=powerzcst)