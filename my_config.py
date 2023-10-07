import os.path

save_dir = '../savedir'
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

BRUSH_INT = 50
COVER_JSON = True  # 在直接读取已标注的json文件的功能中，是否覆盖修改前的json文件。
