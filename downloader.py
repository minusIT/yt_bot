from pytube import YouTube
from time import mktime, strptime
from math import floor
import asyncio
import srt
import re

class Downloader(object):
	"""titles downloader"""
	def __init__(self):
		self.yt_exp = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'

	def set_url(self, url: str):
		result = re.search(self.yt_exp, url)
		self.url = url
		return result != None

	def convert_time(self, time, default_mask = "%H:%M:%S"):
		return int(mktime(strptime(time,default_mask)))

	def set_time(self, time_att, time_set):
		if time_att == 'start':
			self.start_time = self.convert_time(time_set) - self.convert_time("0:00:00")
		elif time_att == 'end':
			self.end_time = self.convert_time(time_set) - self.convert_time("0:00:00")
			if self.end_time <= self.start_time:
				raise ValueError("Error time value")

	async def get_titles(self):
		yt = YouTube(self.url)
		if ('ru' in yt.captions):
			captions = yt.captions['ru'].generate_srt_captions()
			self.captions = list(srt.parse(captions))
			await self.__calc_interval(self.start_time, self.end_time)
			text = ""
			for i in range(self.start_point, self.end_point):
				text += (self.captions[i].content + " ")
			return text
		else:
			return "no rus subs in video"

	async def __calc_interval(self, start: int, end: int):
		t_start = asyncio.create_task(self.__get_start(start))
		t_end = asyncio.create_task(self.__get_end(end))
		await asyncio.gather(t_start, t_end)

	async def __get_start(self, time: int):
		l = 0
		r = len(self.captions)
		while l < r:
			mid = floor((l + r) / 2)
			start = int(self.captions[mid].start.seconds)
			if start < time:
				l = mid + 1
			elif start > time:
				r = mid - 1
			else:
				self.start_point = mid
				return
		self.start_point = mid - 1

	async def __get_end(self, time: int):
		l = 0;
		r = len(self.captions)
		while l < r:
			mid = floor((l + r) / 2)
			end = int(self.captions[mid].end.seconds)
			if end < time:
				l = mid + 1
			elif end > time:
				r = mid - 1
			else:
				self.end_point = mid
				return
		self.end_point = mid + 1
