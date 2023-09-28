from object_detector.detector import ObjectDetector

od = ObjectDetector()
res = od.detect('./test_img.jpg', text_prompt='pest')
print(res)