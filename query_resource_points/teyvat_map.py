# 提瓦特地图类


import os
import json
from urllib import request
from PIL import Image

FILE_PATH = os.path.dirname(__file__)

map_url = "https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/map/info?map_id=2&app_sn=ys_obc"
header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'


class Teyvat_map():

    def __init__(self):

        self.image = None
        self.map_path = os.path.join(FILE_PATH,"icon","teyvat_map.jpg")
        self.detail = self.get_detail()

        self.size = self.detail["total_size"]
        self.origin = self.detail["origin"]

        if not os.path.exists(self.map_path):
            self.splice_map()

        self.load_map()


    def get_detail(self):
        # 获取地图的detail
        schedule = request.Request(map_url)
        schedule.add_header('User-Agent', header)
        with request.urlopen(schedule) as f:
            rew_data = f.read().decode('utf-8')
            detail_str = json.loads(rew_data)["data"]["info"]["detail"]
            detail = json.loads(detail_str)
            return detail


    def download_jpg(self,url):
        # 下载地图jpg文件，返回Image对象
        schedule = request.Request(url)
        schedule.add_header('User-Agent', header)
        with request.urlopen(schedule) as f:
            return Image.open(f)


    def splice_map(self):
        # 将下载的地图文件拼接保存
        slices = self.detail["slices"]

        map_bg = Image.new("RGB",self.size)

        im1 = self.download_jpg(slices[0][0]["url"])
        im2 = self.download_jpg(slices[0][1]["url"])
        im3 = self.download_jpg(slices[1][0]["url"])
        im4 = self.download_jpg(slices[1][1]["url"])

        map_bg.paste(im1,(0,0))
        map_bg.paste(im2,(4096,0))
        map_bg.paste(im3,(0,4096))
        map_bg.paste(im4,(4096,4096))

        with open(self.map_path,"wb") as map_jpg:
            map_bg.save(map_jpg)


    def load_map(self):
        # 载入本地的地图文件
        self.image = Image.open(self.map_path)


    def reload_map(self):
        # 重新获取地图文件
        self.detail = self.get_detail()
        self.size = self.detail["total_size"]
        self.origin = self.detail["origin"]
        self.splice_map()
        self.load_map()


