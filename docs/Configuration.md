# Installing and configuring Raspbian on Raspberry pi

**Model: ** Raspberry pi B

**OS: ** [Raspbian Jessie](https://downloads.raspberrypi.org/raspbian/images/raspbian-2016-05-31/)

## Installing on SD card

After download raspbian image:

```bash
$ lsblk # show us our disks.
$ sudo dd bs=1M if=2016-05-27-raspbian-jessie.img of=/dev/sdb # copy raspbian to sd card (sdb).
$ sudo dd bs=1M if=/dev/sdb2 of=/dev/sdc # copy raspbian system partition to USB flash drive.
```

Edit **cmdline.txt** on SD **/boot** partition and modify **root** variable:

```bash
smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/sda1 rootfstype=ext4 elevator=noop rootwait # /dev/sda1 point to our USB drive
```

This way our OS run faster than using only a SD card, however **/boot** is needed on SD to boot our system so we need SD card and USB anyway.

## Configuring network access



## Source info
[Usb install](http://picodotdev.github.io/blog-bitix/2014/01/iniciar-la-raspberry-pi-desde-un-disco-o-memoria-usb/)
