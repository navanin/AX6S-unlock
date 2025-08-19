# Прошивка роутера Redmi AX3200/AX6s ревизии RB01/RB03
Xiaomi AX3200 (модель RB01, глобальная версия) и Redmi AX6S (модель RB03, китайская версия) по сути своей являются одинаковыми устройствами. Единственное отличие - стоковая прошивка, которая по умолчанию является регионально заблокированной.

Этот гайд поможет с прошивкой любого из указанных устройств на открытую ОС OpenWRT.

## Подготовка

Перед началом работ убедитесь, что у вас под рукой есть следующее оборудование и ПО:

- ОС Linux (ВМ подходит точно, контейнеры и WSL надо проверять)
- Установленный python3, git
- Загруженный репозиторий https://github.com/navanin/AX6S-unlock

## Установка

### 0. Перейдите к репозиторию AX6S-unlock

```bash
git clone https://github.com/navanin/AX6S-unlock.git
cd AX6S-unlock
```

### 1. Проверка состояния telnet

Прежде всего необходимо понять, принимает ли на данный момент ваш роутер подключения по Telnet. Для проверки состояния telnet достаточно обратиться к роутеру через curl или веб интерфейс

```bash
curl http://192.168.31.1/cgi-bin/luci/api/xqsystem/fac_info
```

Если Telnet работает переходите к **пункту 3**. 

Если Telnet не работает, следуйте дальнейшим указаниям. 

### 2. Включение Telnet / SSH

Перед проведением каких либо манипуляций, необходимо понять, с какой версией роутера мы работаем - Xiaomi AX3200 (RB01) или Redmi AX6S (RB03). 

Определить это можно по коробке или нижней панели роутера с наклейкой. 

### Шаги для роутера Redmi AX6S (RB03)

Вы можете включить Telnet, прошив стоковую прошивку закрытой беты с названием `miwifi_rb03_firmware_stable_1.2.7_closedbeta.bin` (MD5: 5eedf1632ac97bb5a6bb072c08603ed7). 

Файл лежит в папке AX6s-unlock, но на всякий случай, дополнительная ссылка:

[miwifi_rb03_firmware_stable_1.2.7.bin](https://github.com/YangWang92/AX6S-unlock/raw/master/miwifi_rb03_firmware_stable_1.2.7.bin)

Все прошивается из WEB-интерфейса роутера, на стоковой прошивке, в настройках. 

После прошивки выполните скрипт password.py, для получения пароля от Telnet:

```bash
# <S/N> - Serial Number c наклейки на нижней панели роутера
python3 password.py <S/N>
```

Скрипт отдаст короткую строку - это пароль Telnet для пользователя root. Для подключения используйте команду:

```bash
telnet -l root 192.168.31.1 23
```

Переходите к пункту 3. 

### Шаги для роутера Xiaomi AX3200 (RB01)

Для начала работы и изменения netmode устройства, запустите скрипт netmode_switcher.py:

```bash
python3 netmode_switcher.py
```

После успешного выполнения скрипта, мы переходим к части внедрения эксплойта в роутер. Выполните на ОС Linux следующие команды:

```bash
# Установка зависимостей
apt install cmake git 
# Конфигурация venv
cd xmir-patcher
python3 -m venv venv
source venv/bin/activate
# Запуск эксплойта
bash run.sh
# Пример работы эксплойта:
#(venv) root@ubuntu:/home/navanin/xmir-patcher# bash run.sh 
#
#==========================================================
#
#Xiaomi MiR Patcher  
#
#
# 1 - Set IP-address (current value: 192.168.31.1)
# 2 - Connect to device (install exploit)
# 3 - Read full device info
# 4 - Create full backup
# 5 - Install EN/RU languages
# 6 - Install permanent SSH
# 7 - Install firmware (from directory "firmware")
# 8 - {{{ Other functions }}}
# 9 - [[ Reboot device ]]
# 0 - Exit
#
#Select: 
```

В меню эксплойта выберите пункт 2 и нажмите Enter - начнется установка эксплойта. 


> 💡**Внимание!**
>
>Эксплойт на роутере живет до первой перезагрузки, поэтому не перезагружайте роутер после его установки.
>
>Если все же перезагрузились, запустите установку эксплойта повторно.

После успешной установки эксплойта на роутере станет доступен SSH по адресу 192.168.31.1. Логин и пароль для подключения - “root”. 
Команда для подключения:

```bash
ssh root@192.168.31.1 -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa
```

Переходите к пункту 3. 

### 3. Прошивка роутера на OpenWRT

Выполните следующие команды на роутере, для подготовки устройства к прошивке OpenWrt:

```bash
nvram set ssh_en=1
nvram set uart_en=1
nvram set boot_wait=on
nvram set flag_boot_success=1
nvram set flag_try_sys1_failed=0
nvram set flag_try_sys2_failed=0
nvram commit
```

На ОС Linux, в папке AX6S-unlock убедитесь в существовании файла factory.bin. В папке, в которой вы обнаружили файл factory.bin запустите легковесный HTTP-сервер на Python для передачи прошивки на роутер. 

```bash
python3 -m http.server
# Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

В удаленной сессии на роутере выполните команды для прошивки OpenWrt:

```bash
cd /tmp
wget http://<IP-адрес Linux>:8000/factory.bin
mtd -r write factory.bin firmware
```

После завершения прошивки устройство должно перезагрузиться в OpenWrt. Обратите внимание: после перезагрузки IP устройства сменится на стандартный для OpenWrt `192.168.1.1`.

Если после прошивку устройство все еще загружается в стоковую прошивку, снова откройте удаленную сессию, выполните команды ниже, а затем вернитесь к командам для прошивки и выполните их заново:

```bash
nvram set ssh_en=1
nvram set uart_en=1
nvram set boot_wait=on
nvram set flag_boot_success=1
nvram set flag_try_sys1_failed=0
nvram set flag_try_sys2_failed=0
nvram set "boot_fw1=run boot_rd_img;bootm"
nvram commit
```

### 4. Специфичная настройка AX3200

Большинство моделей RB01, были подвержены обновлениям загрузчика, которое приводит к софт-локу загрузчика, после 5-6 перезагрузок OpenWRT.

После установки OpenWRT, выполните следующие команды на устройстве:

```bash
fw_setenv boot_fw1 "run boot_rd_img;bootm"
fw_setenv flag_try_sys1_failed 8
fw_setenv flag_try_sys2_failed 8
fw_setenv flag_boot_rootfs 0
fw_setenv flag_boot_success 1
fw_setenv flag_last_success 1
```

Чтобы убедиться, что команды применились, перезапустите устройство и запустите команду “fw_printenv” в терминале. Одна из строк должна содержать “flag_try_sys1_failed=8” (или больше 8). Если вы видите эту строку - исправления применились.