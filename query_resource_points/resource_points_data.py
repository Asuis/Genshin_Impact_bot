# 所有资源点数据

import os
import json
import time
from urllib import request
from PIL import Image,ImageMath

LABEL_URL      = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/map/label/tree?app_sn=ys_obc'
POINT_LIST_URL = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/map/point/list?map_id=2&app_sn=ys_obc'
header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'

FILE_PATH = os.path.dirname(__file__)



class Resource_data():
    def __init__(self):
        # all_resource_type 表示所有资源类型，
        # "1": {
        #         "id": 1,
        #         "name": "传送点",
        #         "icon": "",
        #         "parent_id": 0,
        #         "depth": 1,
        #         "node_type": 1,
        #         "jump_type": 0,
        #         "jump_target_id": 0,
        #         "display_priority": 0,
        #         "children": []
        #     },
        #
        # can_query_type_list保存所有可以查询的资源类型名称和ID，这个字典只有名称和ID
        # all_resource_type里"depth": 2的类型才可以查询，"depth": 1的是1级目录，不能查询
        # "七天神像":"2",
        # "风神瞳":"5"
        #
        # all_resource_point_list保存所有资源点的数据
        # {
        #     "id": 2740,
        #     "label_id": 68,
        #     "x_pos": -1789,
        #     "y_pos": 2628,
        #     "author_name": "✟紫灵心✟",
        #     "ctime": "2020-10-29 10:41:21",
        #     "display_state": 1
        # }

        self.all_resource_type = {}
        self.can_query_type_list = {}
        self.all_resource_point_list = []

        self.god_eye_type = {}

        self.date = "" #记录上次更新数据的日期

        self.up_label_and_point_list()


    def __getitem__(self, key):
        return self.__dict__[key]


    def up_icon_image(self,sublist):
        # 检查是否有图标，没有图标下载保存到本地
        id = sublist["id"]
        icon_path = os.path.join(FILE_PATH, "icon", f"{id}.png")

        if not os.path.exists(icon_path):
            icon_url = sublist["icon"]
            schedule = request.Request(icon_url)
            schedule.add_header('User-Agent', header)
            with request.urlopen(schedule) as f:
                icon = Image.open(f)
                icon = icon.resize((150, 150))

                box_alpha = Image.open(os.path.join(FILE_PATH, "icon", "box_alpha.png")).getchannel("A")
                box = Image.open(os.path.join(FILE_PATH, "icon", "box.png"))

                try:
                    icon_alpha = icon.getchannel("A")
                    icon_alpha = ImageMath.eval("convert(a*b/256, 'L')", a=icon_alpha, b=box_alpha)
                except ValueError:
                    # 米游社的图有时候会没有alpha导致报错，这时候直接使用box_alpha当做alpha就行
                    icon_alpha = box_alpha

                icon2 = Image.new("RGBA", (150, 150), "#00000000")
                icon2.paste(icon, (0, -10))

                bg = Image.new("RGBA", (150, 150), "#00000000")
                bg.paste(icon2, mask=icon_alpha)
                bg.paste(box, mask=box)

                with open(icon_path, "wb") as icon_file:
                    bg.save(icon_file)


    def up_label_and_point_list(self):
        # 更新label列表和资源点列表
        schedule = request.Request(LABEL_URL)
        schedule.add_header('User-Agent', header)
        with request.urlopen(schedule) as f:
            if f.code != 200:  # 检查返回的状态码是否是200
                raise ValueError(f"资源标签列表初始化失败，错误代码{f.code}")
            label_data = json.loads(f.read().decode('utf-8'))

            for label in label_data["data"]["tree"]:
                self.all_resource_type[str(label["id"])] = label

                for sublist in label["children"]:
                    self.all_resource_type[str(sublist["id"])] = sublist
                    self.can_query_type_list[sublist["name"]] = str(sublist["id"])
                    self.up_icon_image(sublist)

                label["children"] = []

                if label["name"] == "神瞳":
                    for eye_type in label["children"]:
                        self.god_eye_type[eye_type["name"]] = eye_type


        schedule = request.Request(POINT_LIST_URL)
        schedule.add_header('User-Agent', header)
        with request.urlopen(schedule) as f:
            if f.code != 200:  # 检查返回的状态码是否是200
                raise ValueError(f"资源点列表初始化失败，错误代码{f.code}")
            test = json.loads(f.read().decode('utf-8'))
            self.all_resource_point_list = test["data"]["point_list"]

        self.date = time.strftime("%d")



