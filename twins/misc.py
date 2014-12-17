# coding: utf-8
import time


def get_nendo ():
    """今は何年度？"""
    y, m = map(int, time.strftime("%Y %m").split())
    return y if m >= 4 else y - 1
