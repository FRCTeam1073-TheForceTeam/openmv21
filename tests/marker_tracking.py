# Multi Color Blob Tracking Example
#
# This example shows off multi color blob tracking using the OpenMV Cam.

import sensor, image, time, math

img_src = "cam"

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green things. You may wish to tune them...
thresholds = [(36, 77, 48, 79, 36, 81)]
# You may pass up to 16 thresholds above. However, it's not really possible to segment any
# scene with 16 thresholds before color thresholds start to overlap heavily.

if (img_src == "stream"):
    img_reader = image.ImageIO("/stream_marker_feb2b.bin","r")
else:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_auto_gain(False) # must be turned off for color tracking
    sensor.set_auto_whitebal(False) # must be turned off for color tracking

clock = time.clock()

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. Don't set "merge=True" becuase that will merge blobs which we don't want here.

blobs = []

while(True):
    blobs = []
    targets = []

    clock.tick()
    if (img_src == "stream"):
        img = img_reader.read(copy_to_fb=True, loop=True, pause=False)
    else:
        img = sensor.snapshot()

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        blobs.append(blob)
        if (blob.h() / blob.w()) > (7/3.5) * 0.9 and (blob.h() / blob.w()) < (7/3.5) * 1.1:
            targets.append(blob);

    length = 0
    area = 0
    area_len = 0

    target = "ugh"

    for t in targets:
        if t.w() * t.h() > area:
            area = t.w() * t.h();
            target = t

    if target != "ugh":
        if target.elongation() > 0.5:
            img.draw_edges(target.min_corners(), color=(255,0,0))
            img.draw_line(target.major_axis_line(), color=(0,255,0))
            img.draw_line(target.minor_axis_line(), color=(0,0,255))
        # These values are stable all the time.
        img.draw_rectangle(target.rect())
        img.draw_cross(target.cx(), target.cy())
        # Note - the blob rotation is unique to 0-180 only.
        img.draw_keypoints([(target.cx(), target.cy(), int(math.degrees(target.rotation())))], size=20)

    #print("Targets: ",targets)
    time.sleep(0.1);
    #print(clock.fps())
