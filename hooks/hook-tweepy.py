# Author: amirulmenjeni <amirulmenjeni@github.com>
#
# Tweepy hook for PyInstaller.

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('tweepy')
