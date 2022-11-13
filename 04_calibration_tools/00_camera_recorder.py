import time
import cv2
import local_coms



z = local_coms.LOCAL_COMS_NODE()

camera_id = 0
record_status = False
show_preview = True
scale_show = 0.5
file_list = []


print("> Initializing camera")
camera = cv2.VideoCapture(camera_id)

print("> Setting parameters")
codec = 0x47504A4D # MJPG
camera.set(cv2.CAP_PROP_FPS, 30.0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FOURCC, codec)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
print("> Parameters are set")

first_frame_captured = False


if show_preview:
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)

while True:    
    text, rx_ok = z.get_text()
    if rx_ok:
        print(text)
        
        match text:
            case "record":
                z.send_text("recording")
                record_status = True
                file_list = []
            
            case "stop":
                msg = ','.join(file_list)
                z.send_text("stopped,"+msg)
                record_status = False
        
            case "exit":
                z.send_text("exit")
                break

            case "show":
                z.send_text("show")
                cv2.namedWindow("image", cv2.WINDOW_NORMAL)
                show_preview = True

            case "hide":
                z.send_text("hide")
                show_preview = False
                cv2.destroyAllWindows()        
            
            case default:
                z.send_text("unknown")


    camera.grab()
    t = time.time_ns()            
    retval, im = camera.retrieve(0)
    
    if not first_frame_captured:
        first_frame_captured = True
        print("> Camera is live")
        print()
        
    if show_preview:
        local_im = cv2.resize(im, None, fx=scale_show, fy=scale_show, interpolation=cv2.INTER_CUBIC)
        cv2.imshow("image", local_im)
        k = cv2.waitKey(1) & 0xff

    if record_status:
        file_list.append(str(t))
        filename = "results\\"+str(t)+".jpg"
        cv2.imwrite(filename, im)


print()
print("> Camera is closing")
camera.release()
cv2.destroyAllWindows()
print("> Exit")
