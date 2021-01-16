[EN](README_en.md) | [CY](README_cy.md)

Self-hosted сервис для отслеживания положения Android-устройства.

Сервису требуется доступ по SSH к устройству с установленным Termux, а также статический ip-адрес телефона.

Статический ip-адрес можно получить с помощью IPsec/L2TP-подключения между сервером и устройством, скрипт для автоматической установки VPN на VPS/EC2 Instance от **_hwdsl2_** можно найти [в этом репозитории ](https://github.com/hwdsl2/setup-ipsec-vpn).

Установка сервиса производится с помощью скрипта [setup.sh](https://github.com/galemys-pyrenaicus/spothecat/releases/download/release/setup.sh).

**NB!** Данный скрипт на данный момент производит изменение конфига Postgresql и сброс пароля пользователя Postgres, доработка для инстансов с уже установленной Postgresql в процессе.
