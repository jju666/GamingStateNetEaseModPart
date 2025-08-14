# -*- coding: utf-8 -*-
import time

from GamingState import GamingState


class TimedGamingState(GamingState):
    def __init__(self, parent, duration):
        GamingState.__init__(self, parent)
        self.duration = duration
        self.time_end = 0
        self.callbacks_timeout = list()
        self.with_enter(self._timed_on_enter)
        self.with_tick(self._timed_on_tick)

    def reset_duration(self, duration):
        """
        @description 设置持续时间
        :param duration: float 持续时间（秒）
        """
        self.duration = duration
        if self.is_state_running():
            self.reset_timer()

    def reset_timer(self):
        """
        @description 重置计时器
        """
        self.get_part().LogDebug("reset_timer {} + {}".format(str(time.time()), str(self.duration)))
        self.time_end = time.time() + self.duration

    def with_time_out(self, callback):
        """
        @description 设置超时回调
        :param callback: callable 回调函数
        """
        self.callbacks_timeout.append(callback)

    # 内部的状态机回调

    def _timed_on_enter(self):
        self.reset_timer()

    def _timed_on_tick(self):
        # 修复：添加更可靠的超时检测，防止浮点数精度问题
        current_time = time.time()
        if current_time >= self.time_end:
            self.get_part().LogDebug("TimedGamingState超时触发: 当前时间={}, 结束时间={}, 差值={}".format(
                current_time, self.time_end, current_time - self.time_end))
            self._time_out()

    def _time_out(self):
        self.get_part().LogDebug("TimedGamingState._time_out 开始执行")
        # 修复：添加超时回调执行保护
        for i, callback in enumerate(self.callbacks_timeout):
            try:
                callback(self)
            except Exception as e:
                self.get_part().LogError("TimedGamingState超时回调执行失败 [{}]: {}".format(i, str(e)))
        
        # 修复：添加状态切换日志和错误处理
        if self.parent is not None:
            self.get_part().LogDebug("TimedGamingState准备切换到下一个状态")
            try:
                self.parent.next_sub_state()
            except Exception as e:
                self.get_part().LogError("TimedGamingState状态切换失败: {}".format(str(e)))
        else:
            self.get_part().LogDebug("TimedGamingState没有父状态，无法切换")

    # 额外的接口

    def get_seconds_left(self):
        """
        @description 获取剩余时间
        :return: 剩余时间（秒）
        :rtype: float
        """
        return self.time_end - time.time()

    def get_seconds_passed(self):
        """
        @description 获取已经过去的时间
        :return: 已经过去的时间（秒）
        :rtype: float
        """
        return self.duration - self.get_seconds_left()

    def get_formatted_time_left(self):
        """
        @description 获取格式化的剩余时间
        :return: 格式化的剩余时间
        :rtype: str
        """
        seconds = self.get_seconds_left()
        hours = int(seconds / 3600)
        seconds %= 3600
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        if hours > 0:
            return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        else:
            return "{:02d}:{:02d}".format(minutes, seconds)

    def get_formatted_time_left_mill(self):
        """
        @description 获取格式化的剩余时间
        :return: 格式化的剩余时间
        :rtype: str
        """
        seconds = self.get_seconds_left()
        hours = int(seconds / 3600)
        seconds %= 3600
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        if hours > 0:
            return "{:02d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, milliseconds)
        else:
            return "{:02d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)

    def get_time_end(self):
        """
        @description 获取结束时间
        :return: 结束时间戳（秒）
        :rtype: float
        """
        return self.time_end