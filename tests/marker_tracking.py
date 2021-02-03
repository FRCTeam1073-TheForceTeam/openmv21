# Multi Color Blob Tracking Example
#
# This example shows off multi color blob tracking using the OpenMV Cam.

import sensor, image, time, math

img_src = "stream"

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green things. You may wish to tune them...
thresholds = [(8, 31, 13, 44, 11, 127)] # generic_blue_thresholds
# You may pass up to 16 thresholds above. However, it's not really possible to segment any
# scene with 16 thresholds before color thresholds start to overlap heavily.

if (img_src == "stream"):
    img_reader = image.ImageReader("/stream_marker_feb2b.bin")
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
    clock.tick()
    if (img_src == "stream"):
        img = img_reader.next_frame(copy_to_fb=True, loop=True, pause=False)
    else:
        img = sensor.snapshot()

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        if (blob.h() / blob.w()) > (10/4) and (blob.h() / blob.w()) < (12/4):
            blobs.append(blob);

    targets = []

    for b in blobs:
        print("Blob Elongation: ",blob.elongation()," Blob Rotation: ",blob.rotation_deg())
        # These values depend on the blob not being circular - otherwise they will be shaky.
        if blob.elongation() > 0.75:
            #img.draw_edges(blob.min_corners(), color=(255,0,0))
            blob_maj_axis = blob.major_axis_line()
            img.draw_line(blob_maj_axis, color=(0,255,0))
            #img.draw_line(blob.minor_axis_line(), color=(0,0,255))

            if ((blob.rotation_deg()>75) and (blob.rotation_deg()<105)):
                print ("Target Detected")
                targets.append([blob.cx(), blob.cy()])
                img.draw_cross(blob.cx(), blob.cy())
        # These values are stable all the time.
        #img.draw_rectangle(blob.rect())
        # Note - the blob rotation is unique to 0-180 only.
        #img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
    print("Targets: ",targets)
    time.sleep(0.5);
    #print(clock.fps())
