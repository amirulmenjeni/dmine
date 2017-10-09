#print('hooking:', __file__)
import os
import re
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('praw')
