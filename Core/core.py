# -*- coding:utf-8 -*-

from .functions import *
from .config import Config
from .texts_utils import TextsUtils
from .image_utils import ImageUtils
from .video_utils import VideoUtils


class Core(Config, TextsUtils, ImageUtils, VideoUtils):
    """核心"""

    def __init__(self):
        Config.__init__(self)
        # 默认必要参数
        # self.encoding, self.scwidth, self.scheight = 'shift-jis', 1280, 720
        # self.scale_ratio = 2

    def show_image2x_status(self, image_extension):
        '''
        显示图片处理进度条，根据时间戳判断图片是否被处理
        '''
        target_count = len(file_list(self.tmp_folder, image_extension))
        if target_count == 0:
            now_percent = 1
            print(f'未发现需要放大的{image_extension}图片')
        else:
            now_percent = 0
        start_time = time.time()
        # 百分比小于100%时循环
        while now_percent < 1:
            now_time = time.time()
            # 时间戳判断图片是否被处理
            now_count = len([image_file for image_file in file_list(self.tmp_folder, image_extension) if image_file.stat().st_mtime > start_time])
            now_percent = now_count/target_count
            if now_percent == 0:
                print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：统计中...', end=' \r')
                time.sleep(2)
                continue
            left_time = int((now_time-start_time)/now_percent - (now_time-start_time))
            print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：{seconds_format(left_time)}', end=' \r')
            time.sleep(2)
            if now_percent == 1:
                print()

    def pool_run(self, target, runs: list, *args) -> list:
        """
        @brief      使用进程池多进程加速计算

        @param      target  目标执行函数
        @param      runs    执行可变参数列表
        @param      args    其它固定参数，按执行函数参数顺序输入

        @return     将执行函数的返回值以列表返回
        """
        pool = Pool(self.cpu_cores)
        processer_ls = []
        for i in runs:
            processer = pool.apply_async(target, args=(i, *args))
            processer_ls.append(processer)
        pool.close()
        pool.join()
        return [processer.get() for processer in processer_ls]

    def a2p(self, file_path) -> Path:
        """
        @brief      游戏数据文件夹到补丁文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        target_file = self.patch_folder/file_path.relative_to(self.game_data)
        if not target_file.parent.exists():
            target_file.parent.mkdir(parents=True)
        return target_file

    def a2t(self, file_path) -> Path:
        """
        @brief      游戏数据文件夹到临时文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        target_file = self.tmp_folder/file_path.relative_to(self.game_data)
        if not target_file.parent.exists():
            target_file.parent.mkdir(parents=True)
        return target_file

    def t2p(self, file_path) -> Path:
        """
        @brief      临时文件夹到补丁文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        target_file = self.patch_folder/file_path.relative_to(self.tmp_folder)
        if not target_file.parent.exists():
            target_file.parent.mkdir(parents=True)
        return target_file

    def clear(self):
        """
        @brief      清空临时文件夹
        """
        try:
            shutil.rmtree(self.tmp_folder)
        except:
            print('warning:临时文件夹不存在')
        finally:
            self.tmp_folder.mkdir(parents=True)