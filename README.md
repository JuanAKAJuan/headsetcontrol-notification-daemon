# headsetcontrol-notification-daemon

### Install Dependencies
- Arch
   ```bash
   sudo pacman -S python-psutil
   ```
https://github.com/Sapd/HeadsetControl

### Setup
```bash
sudo cp headset-notify.py /usr/local/bin/
sudo chmod 755 /usr/local/bin/headset-notify.py
sudo cp headset-notify.service /etc/systemd/system/
```

- Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable headset-notify.service
sudo systemctl start headset-notify.service
```

- Check the status
```bash
sudo systemctl status headset-notify.service
```
