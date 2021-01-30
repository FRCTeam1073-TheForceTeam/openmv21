# Find Circles Example
#
# This example shows off how to find circles in the image using the Hough
# Transform. https://en.wikipedia.org/wiki/Circle_Hough_Transform
#
# Note that the find_circles() method will only find circles which are completely
# inside of the image. Circles which go outside of the image/roi are ignored...

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()
hist = [45, 99, -40, -18, 25, 50]

while(True):
    img = sensor.snapshot().lens_corr(1.8)

    # Circle objects have four values: x, y, r (radius), and magnitude. The
    # magnitude is the strength of the detection of the circle. Higher is
    # better...

    # `threshold` controls how many circles are found. Increase its value
    # to decrease the number of circles detected...

    # `x_margin`, `y_margin`, and `r_margin` control the merging of similar
    # circles in the x, y, and r (radius) directions.

    for blob in img.find_blobs([hist], pixels_threshold=500, area_threshold=500, merge=True, ):
        print (blob)
        #img.draw_rectangle(blob.x(), blob.y(), blob.w(), blob.h())
        blob_roi = (blob.x()-5, blob.y()-5, blob.w()+10, blob.h()+10)
        minr = int((blob.w()-5)/2)
        maxr = int((blob.w()+5)/2)
        for circle in img.find_circles(roi = blob_roi, threshold = 2000, x_margin = 10, y_margin = 10,
                r_margin = 10, r_min = minr, r_max = maxr, r_step = 2, merge=True):
                #if ((circle.r()*2 - 10) < blob.w() < (circle.r()*2 + 10)):
                img.draw_circle(circle.x(), circle.y(), circle.r(), color = (255, 0, 0))
                print(circle)

#circlecount = circlecount + 1
#print (circlecount)
#if circlecount < 20:
#if (blob.pixels() + circle.magnitude())/2 > blob.pixels() + 50:
#attempting to average them and keep within a range, may have to make into a % error situation
    #img.draw_circle(circle.x(), circle.y(), circle.r(), color = (255, 0, 0))
    #print(circle)

    # r_min, r_max, and r_step control what radiuses of circles are tested.
    # Shrinking the number of tested circle radiuses yields a big performance boost.

