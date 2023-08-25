import os
import time
import argparse
import imutils
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver
 
from utils.yolo_classes import get_cls_dict
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from utils.yolo_with_plugins import TrtYOLO
from PIL import Image

import pycuda.driver as cuda
import tensorrt as trt
import numpy as np


WINDOW_NAME = 'TrtYOLODemo'
chars = ["0", "1", "2", "3", "4", 
         "5", "6", "7", "8", "9", 
         "A", "B", "C", "D", "E", 
         "F", "G", "H", "I", "J", 
         "K", "L", "M", "N", "O", "P", 
         "Q", "R", "S", "T", "U", 
         "V", "W", "X", "Y", "Z", ""]


def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def crop_bboxes(img, bbox):
    bb = bbox[0]
    x_min, y_min, x_max, y_max = bb[0], bb[1], bb[2], bb[3]
    crop = img[y_min:y_max, x_min:x_max]
    return crop


class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()
    
def allocate_buffers(engine, batch_size=-1):
    inputs = []
    outputs = []
    bindings = []
    stream = cuda.Stream()
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * batch_size
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        # Allocate host and device buffers
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        # Append the device buffer to device bindings.
        bindings.append(int(device_mem))
        # Append to the appropriate list.
        if engine.binding_is_input(binding):
            inputs.append(HostDeviceMem(host_mem, device_mem))
            print(f"input: shape:{engine.get_binding_shape(binding)} dtype:{engine.get_binding_dtype(binding)}")
        else:
            outputs.append(HostDeviceMem(host_mem, device_mem))
            print(f"output: shape:{engine.get_binding_shape(binding)} dtype:{engine.get_binding_dtype(binding)}")
    return inputs, outputs, bindings, stream

def load_engine(trt_runtime, engine_path):
    with open(engine_path, "rb") as f:
        engine_data = f.read()
    engine = trt_runtime.deserialize_cuda_engine(engine_data)
    return engine

def do_inference(context, bindings, inputs, outputs, stream, batch_size=1):
    # Transfer input data to the GPU.
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
    # Run inference.
    context.execute_async(
        batch_size=batch_size, bindings=bindings, stream_handle=stream.handle
    )
    # Transfer predictions back from the GPU.
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
    # Synchronize the stream
    stream.synchronize()
    # Return only the host outputs.
    return [out.host for out in outputs]

def loop_and_detect(cam, conf_th, vis):
    os.environ["CUDA_VISIBLE_DEVICES"] = "1" 

    trt_yolo = TrtYOLO('custom-yolov4-tiny-detector', 1, 'store_false')

    TRT_LOGGER = trt.Logger(trt.Logger.WARNING) 
    trt_engine_path = "lprnet_model.engine"     
    trt_runtime = trt.Runtime(TRT_LOGGER) 
    trt_engine = load_engine(trt_runtime, trt_engine_path) 
    # Execution context is needed for inference 
    context = trt_engine.create_execution_context() 
    # This allocates memory for network inputs/outputs on both CPU and GPU 
    inputs, outputs, bindings, stream = allocate_buffers(trt_engine) 
    
    writer = cv2.VideoWriter(filename="lplate.mp4",  
                             fourcc=cv2.VideoWriter_fourcc(*'mp4v'),  
                             fps=21, frameSize=(1280, 720)) 

    n = 0 
    fps = 0.0 
    placa = "" 
    tic = time.time() 

    while True: 
        grab, img_orig = cam.read() 
        if img_orig is None: 
            break 
        boxes, confs, clss = trt_yolo.detect(img_orig, conf_th) 
        img_rgb = cv2.cvtColor(img_orig, cv2.COLOR_BGR2RGB) 
 

        if len(boxes) > 0: 
            cropped = crop_bboxes(img_rgb, boxes) 
            image = [cropped] 
            image = np.array([(cv2.resize(img_rgb, (96, 48))) / 255.0  
                                      for img_rgb in image], dtype=np.float32) 
            image= image.transpose(0, 3, 1, 2)        
            np.copyto(inputs[0].host, image.ravel()) 
            input_shape = (1, 3, 48, 96) 
            context.set_binding_shape(0, input_shape) 
            output = do_inference(context,  
                                  bindings=bindings,  
                                  inputs=inputs,  
                                  outputs=outputs,  
                                  stream=stream) 


            last_char = "" 
            placa = "" 
            i = 0 

            for x in output[0]: 
                if CHARS[x] == last_char: 
                    continue 
                else: 
                    last_char = CHARS[x] 
                    placa += CHARS[x] 
                if len(placa) == 7: 
                    cv2.putText(img_rgb, placa, (10, 90),  
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 4) 
                i += 1 


        img_rgb = vis.draw_bboxes(img_rgb, boxes, confs, clss) 
        img_rgb = show_fps(img_rgb, fps) 
        writer.write(img_rgb) 

        key = cv2.waitKey(1) 
        if key == 27:  # ESC key: quit program 
            break 
        elif key == ord('F') or key == ord('f'):  # Toggle fullscreen 
            full_scrn = not full_scrn 
            set_display(WINDOW_NAME, full_scrn) 

        toc = time.time() 
        curr_fps = 1.0 / (toc - tic) 
        fps = curr_fps if fps == 0.0 else (fps*0.95 + curr_fps*0.05) 
        tic = toc 
        n += 1 
 
    for x in range(1, 21): 
        cam.read() 
    cam.shutdown() 
    writer.release() 
    cv2.destroyAllWindows() 

cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)

cls_dict = get_cls_dict(1)
vis = BBoxVisualization(cls_dict)

loop_and_detect(cap, conf_th=0.3, vis=vis)

