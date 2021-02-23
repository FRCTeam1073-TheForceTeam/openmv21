import image, pyb, time

clock = time.clock()

img_reader = image.ImageIO("/test_stream.bin", "r")

while(True):
    clock.tick()
    img = img_reader.read(copy_to_fb=True, loop=True, pause=True)
    img.draw_line((0, 0, img.width(), img.height()), color = (255, 0, 0), thickness = 10)
    img.draw_rectangle(104,79,119,96)
    time.sleep(1);
img_write.close
