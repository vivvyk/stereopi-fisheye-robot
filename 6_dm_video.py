# Copyright (C) 2019 Eugene a.k.a. Realizator, stereopi.com, virt2real team
#
# This file is part of StereoPi tutorial scripts.
#
# StereoPi tutorial is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# StereoPi tutorial is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with StereoPi tutorial.  
# If not, see <http://www.gnu.org/licenses/>.
#
#          <><><> SPECIAL THANKS: <><><>
#
# Thanks to Adrian and http://pyimagesearch.com, as a lot of
# code in this tutorial was taken from his lessons.
#  
# Thanks to RPi-tankbot project: https://github.com/Kheiden/RPi-tankbot
#
# Thanks to rakali project: https://github.com/sthysel/rakali


from picamera import PiCamera
import time
import cv2
import numpy as np
import json
import os
import imutils
from datetime import datetime

print ("You can press Q to quit this script!")
time.sleep (5)

# Depth map default preset
SWS = 5
PFS = 5
PFC = 29
MDS = -30
NOD = 160
TTH = 100
UR = 10
SR = 14
SPWS = 100

# Use the whole image or a stripe for depth map?
useStripe = False
dm_colors_autotune = True
disp_max = -100000
disp_min = 10000

# Camera settimgs
cam_width = 1280
cam_height = 480

# Final image capture settings
scale_ratio = 0.5

# Camera resolution height must be dividable by 16, and width by 32
cam_width = int((cam_width+31)/32)*32
cam_height = int((cam_height+15)/16)*16
print ("Used camera resolution: "+str(cam_width)+" x "+str(cam_height))

# Buffer for captured image settings
img_width = int (cam_width * scale_ratio)
img_height = int (cam_height * scale_ratio)
capture = np.zeros((img_height, img_width, 4), dtype=np.uint8)
print ("Scaled image resolution: "+str(img_width)+" x "+str(img_height))

cam_framerate = 20

# Initialize the camera
camera = PiCamera(stereo_mode='side-by-side',stereo_decimate=False)
camera.resolution=(cam_width, cam_height)
camera.framerate = cam_framerate
#camera.hflip = True

# Initialize interface windows
cv2.namedWindow("Image")
cv2.moveWindow("Image", 50,100)
cv2.namedWindow("left")
cv2.moveWindow("left", 450,100)
cv2.namedWindow("right")
cv2.moveWindow("right", 850,100)


disparity = np.zeros((img_width, img_height), np.uint8)
sbm = cv2.StereoBM_create(numDisparities=0, blockSize=21)


def stereo_depth_map(rectified_pair):
    global disp_max
    global disp_min
    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    if (dm_colors_autotune):
        disp_max = max(local_max,disp_max)
        disp_min = min(local_min,disp_min)
        local_max = disp_max
        local_min = disp_min
        print(disp_max, disp_min)
    disparity_grayscale = (disparity-local_min)*(65535.0/(local_max-local_min))
    #disparity_grayscale = (disparity+208)*(65535.0/1000.0) # test for jumping colors prevention 
    disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0/65535.0))
    disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
    cv2.imshow("Image", disparity_color)
    key = cv2.waitKey(1) & 0xFF   
    if key == ord("q"):
        dm_writer.release()
        left_writer.release()
        right_writer.release()
        quit();
    return disparity_color

def load_map_settings( fName ):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings
    print('Loading parameters from file...')
    f=open(fName, 'r')
    data = json.load(f)
    SWS=data['SADWindowSize']
    PFS=data['preFilterSize']
    PFC=data['preFilterCap']
    MDS=data['minDisparity']
    NOD=data['numberOfDisparities']
    TTH=data['textureThreshold']
    UR=data['uniquenessRatio']
    SR=data['speckleRange']
    SPWS=data['speckleWindowSize']    
    #sbm.setSADWindowSize(SWS)
    sbm.setPreFilterType(1)
    sbm.setPreFilterSize(PFS)
    sbm.setPreFilterCap(PFC)
    sbm.setMinDisparity(MDS)
    sbm.setNumDisparities(NOD)
    sbm.setTextureThreshold(TTH)
    sbm.setUniquenessRatio(UR)
    sbm.setSpeckleRange(SR)
    sbm.setSpeckleWindowSize(SPWS)
    f.close()
    print ('Parameters loaded from file '+fName)


load_map_settings ("3dmap_set.txt")
try:
    npzfile = np.load('./calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
except:
    print("Camera calibration data not found in cache, file ", './calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
    exit(0)
    
imageSize = tuple(npzfile['imageSize'])
leftMapX = npzfile['leftMapX']
leftMapY = npzfile['leftMapY']
rightMapX = npzfile['rightMapX']
rightMapY = npzfile['rightMapY']

output = 'vids'

dm_path = os.path.join(output, "dm.avi")
left_path = os.path.join(output, "left.avi")
right_path = os.path.join(output, "right.avi")
fourcc = cv2.VideoWriter_fourcc(*"H264")
dm_writer = None
left_writer = None
right_writer = None

# capture frames from the camera
for frame in camera.capture_continuous(capture, format="bgra", use_video_port=True, resize=(img_width,img_height)):
    t1 = datetime.now()
    pair_img = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
    imgLeft = pair_img [0:img_height,0:int(img_width/2)] #Y+H and X+W
    imgRight = pair_img [0:img_height,int(img_width/2):img_width] #Y+H and X+W
    imgL = cv2.remap(imgLeft, leftMapX, leftMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    imgR = cv2.remap(imgRight, rightMapX, rightMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    
    if (useStripe):
        imgRcut = imgR [80:160,0:int(img_width/2)]
        imgLcut = imgL [80:160,0:int(img_width/2)]
    else:
        imgRcut = imgR
        imgLcut = imgL
        
    rectified_pair = (imgLcut, imgRcut)
    disparity = stereo_depth_map(rectified_pair)
    # show the frame
    cv2.imshow("left", imgLcut)
    cv2.imshow("right", imgRcut)    

    t2 = datetime.now()
    print ("DM build time: " + str(t2-t1))
    
    imgL300 = imutils.resize(imgLcut, width=300)
    imgR300 = imutils.resize(imgRcut, width=300)
    disparity300 = imutils.resize(disparity, width=300)

    if dm_writer is None:
        (h, w) = disparity300.shape[:2]
        dm_writer = cv2.VideoWriter(dm_path, fourcc, cam_framerate, (w, h), True)
        (h, w) = imgL300.shape[:2]
        left_writer = cv2.VideoWriter(left_path, fourcc, cam_framerate, (w, h), False)
        (h, w) = imgR300.shape[:2]
        right_writer = cv2.VideoWriter(right_path, fourcc, cam_framerate, (w, h), False)
    dm_writer.write(disparity300)
    left_writer.write(imgL300)
    right_writer.write(imgR300)
