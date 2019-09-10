In the latest Raspbian Buster with the Linux kernel > 4.19.57 stereoscopic support
is broken. Please DO NOT do upgrade of the system untill appropriate fix from the
Raspberry Pi Foundation.
We'll update this document after any improvements.

== Installing OpenCV on raspbian Buster without breaking stereoscopic mode: ==

1. Download Raspbian Buster and write omage to ypur micro SD card.
We've used "Raspbian Buster with desktop, 2019-07-10"

2. Set up python 3 as a default:

`nano ~/.bashrc`

add this row at the end of file:

`alias python='/usr/bin/python3'`

save file (Esc X X, "yes")

activate new settings:

`source ~/.bashrc`

Check if settings are implemented correctly.

`python`

You should see "Python 3.7.3" in the first row.

If you see "Python 2.7.x" - please repeat previous steps.

3. Install OpenCV 3.4.3 with PiWheels:

`sudo pip3 install opencv-python`

`sudo pip3 install opencv-contrib-python`

In our case we have 3.4.3.18 version installed.

4. Install additional libs:

```
sudo pip3 install opencv-python 
sudo apt-get install libhdf5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev 
sudo apt-get install libqtgui4 
sudo apt-get install libqt4-test
```

5. To check if everything Ok try to run our first test script:
python 1_test.py

You should see preview image. Press 'Q' for exit.

6. Check raspistill 3D mode:

`raspistill -3d sbs -o 1.jpg`

You should see 5 seconds preview, and stereoscopic image "1.jpg" should be saved after 
running this code.

Stay tuned! And good luck with your OpenCV experiments! :-)