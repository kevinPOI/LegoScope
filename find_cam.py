import cv2

def find_cam(display = False):
    openCvVidCapIds = []

    for i in range(10):
        try:
            cap = cv2.VideoCapture(i)
            if cap is not None and cap.isOpened():
                openCvVidCapIds.append(i)
                ret, og_frame = cap.read()
                # og_frame = cv2.imread("sample.jpg")
                if display:
                    cv2.imshow(f"camera {i}", og_frame)
            # end if
        except:
            pass
        # end try
    # end for

    print(str(openCvVidCapIds))
    if display:
        cv2.waitKey(0)
    return openCvVidCapIds

if __name__ == "__main__":  
    find_cam(display=True)