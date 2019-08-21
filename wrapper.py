#!/usr/bin/env python
'''
Author : yanke
Date   : 2019-08-16
'''


class Icon(object):
    def __init__(self, icon_type, target_icon_name, source_icon_name, match_icon_dir):
        self.icon_type = icon_type
        self.source_icon_name = source_icon_name
        self.target_icon_name = target_icon_name
        self.match_icon_dir = match_icon_dir

        pass


class Name_family:
    def __init__(self, builder):
        self.appname = builder.appname
        self.splash_pic_name = builder.splash_pic_name
        self.app_icon = builder.app_icon

    class Builder:
        def appname(self, appname):
            self.appname = appname
            return self

        def splash_picname(self, splash_pic_name):
            self.splash_pic_name = splash_pic_name
            return self

        def app_icon(self, app_icon):
            self.app_icon = app_icon
            return self

        def build(self):
            return Name_family(self)
