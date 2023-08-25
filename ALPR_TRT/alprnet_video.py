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
        # pdb.set_trace()
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

def crop_bboxes(img, bbox):
    x_min, y_min, x_max, y_max = bbox[0], bbox[1], bbox[2], bbox[3]
    crop = img[y_min:y_max, x_min:x_max]
    return crop

def loop_and_detect(video, conf_th, vis):
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
    
    writer = cv2.VideoWriter("lplate.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 21, (1280, 720))
    n_frames = int(cv2.VideoCapture.get(video, int(cv2.CAP_PROP_FRAME_COUNT) ) )
    
    n = 0
    fps = 0.0
    tic = time.time()
    l_plate = ""
    while n < n_frames:
        
        ret, img_orig = video.read()        
        if img_orig is None:
            break
        img_orig = cv2.resize(img_orig,(1280, 720), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        
        boxes, confs, clss = trt_yolo.detect(img_orig, conf_th)
        img_rgb = img_orig
        pos_y = 80
        for box in boxes:
            cropped = crop_bboxes(img_orig, box)
            print(cropped.shape)
            image = [cropped]
            
            image = np.array([(cv2.resize(img_rgb, ( 96 , 48 )))/ 255.0 for img_rgb in image], dtype=np.float32)
            print(image.shape)
            image= image.transpose( 0 , 3 , 1 , 2 )            
            np.copyto(inputs[0].host, image.ravel())
            
            input_shape = (1,3,48,96)
            context.set_binding_shape(0, input_shape)
            output = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)

            last_char = ""
            l_plate = ""
            i = 0
            for x in output[0]:
                if chars[x] == last_char:
                    continue
                else:
                    last_char = chars[x]
                    l_plate += chars[x]
            if len(l_plate) == 7:
                cv2.putText(img_rgb, l_plate, (10, pos_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 4)
                pos_y += 50
                i += 1

            print(l_plate, fps)

        img_rgb = vis.draw_bboxes(img_rgb, boxes, confs, clss)
        img_rgb = show_fps(img_rgb, fps)            

        writer.write(img_rgb)
        key = cv2.waitKey(1)

        toc = time.time()
        curr_fps = 1.0 / (toc - tic)
        fps = curr_fps if fps == 0.0 else (fps*0.95 + curr_fps*0.05)
        tic = toc
        n += 1
    writer.release()

def main():    
    cls_dict = get_cls_dict(1)
    vis = BBoxVisualization(cls_dict)    
    
    video = cv2.VideoCapture("agora_MT.mp4")

    loop_and_detect(video, conf_th=0.3, vis=vis)
    
if __name__ == "__main__":
    main()
