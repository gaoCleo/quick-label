from segment.segment_ai import SegmentAnythingAI


sg = SegmentAnythingAI(checkpoint_path='./segment/segment_anything/sam_vit_h_4b8939.pth', device='cuda')
sg.set_img('./test_img.jpg')
res = sg.detect_by_boxes(boxes=[[49.296470642089844, 34.962093353271484, 187.845703125, 136.22267150878906]])
print(res)