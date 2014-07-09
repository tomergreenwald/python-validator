#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from configClass import *


class DefaultCodeFr(wx.Frame):
    """
    DefaultColderFr

    Creates a window and all the control necessary to
    change the contents of the text added upon a new tab.

    """

    def __init__(self, parent, id):
        """
        __init__


        Creates the frame and all the controls. Binds their events to
        the neccesary functions.
        """
        wx.Frame.__init__(self, parent, id, 'Default Code', size=(500,
                          410))

        panel = wx.Panel(self)

        descr = wx.StaticText(panel, -1,
                              "The folowing text will be added automatically when creating a new tab:",
                              pos=(10, 10), size=(-1, -1))

        self.text_ctrl = wx.TextCtrl(panel, -1, "", size=(300, 350), pos=
                (10, 300), style=wx.TE_MULTILINE)
        self.text_ctrl.AppendText(Config.GetOption("DefaultText"))

        save_btn = wx.Button(panel, -1, "Save", size=(-1, -1), pos=(600,
                             460))
        close_btn = wx.Button(panel, -1, "Close", size=(-1, -1), pos=(600,
                              460))

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(save_btn, 0, wx.EXPAND)
        btn_sizer.Add(close_btn, 0, wx.EXPAND)

        self.Bind(wx.EVT_CLOSE, self.HideMe)
        close_btn.Bind(wx.EVT_BUTTON, self.HideMe)
        save_btn.Bind(wx.EVT_BUTTON, self.OnSave)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(descr, 0, wx.EXPAND)
        main_sizer.AddSpacer(10)
        main_sizer.Add(self.text_ctrl, 0, wx.EXPAND)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND)
        panel.SetSizer(main_sizer)
        panel.Fit()

        self.Centre()
        self.Hide()

    def OnSave(self, event):
        """
        OnSave

        Saves the contents of the TextCtrl to the configuration file
        using Config.ChangeOption.
        """
        Config.ChangeOption("DefaultText", self.text_ctrl.GetValue())

    def ShowMe(self, event):
        """
        ShowMe

        Makes window visible.
        """
        self.Show()

    def HideMe(self, event):
        """
        Hides the window.
        """
        self.Hide()
