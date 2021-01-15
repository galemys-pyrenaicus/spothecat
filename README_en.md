[RU](README.md) | [CY](README_cy.md)

Lightweight self-hosted Android device location service.

Service requires SSH access to Android device and it's static ip-address, it could be achieved by e.g. L2TP connection between server and phone.
You could found an IPsec/L2TP autoinstall script for VPS/EC2 Instance in [this repository](https://github.com/hwdsl2/setup-ipsec-vpn) made by **_hwdsl2_**.

Service should be installed by running [setup.sh](setup.sh).
**NB!** At the moment this script changes Postgresql config and resets postgres users password. It would be improved later for running on instanced with Postgresql installed already.
