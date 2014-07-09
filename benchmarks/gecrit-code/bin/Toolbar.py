#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from Fonts import *




class MainToolbar(wx.ToolBar):
    """
    MainToolbar

    Creates the application toolbar object.

    """
    def __init__(self, parent, id=wx.ID_ANY):

        """
         __init__

         Builds the ToolBar object and adds elemensts to it.
         Takes the icons from the icons/ folder.
        """

        wx.ToolBar.__init__(self, parent, id, style=wx.TB_HORIZONTAL |
                            wx.NO_BORDER)

        self.NewTabImage = wx.Image('icons/newtab.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.OpenImage = wx.Image('icons/open.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SaveImage = wx.Image('icons/save.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SaveAsImage = wx.Image('icons/saveas.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        ConfigImage = wx.Image('icons/config.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.QuitImage = wx.Image('icons/quit.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.CloseImage = wx.Image("icons/close.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.PrintImage = wx.Image("icons/printer.bmp", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.RunImage = wx.Image("icons/run.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.AddSimpleTool(600, self.NewTabImage, 'New',
                           'Open a new tab.')
        self.AddSimpleTool(601, self.OpenImage, 'Open',
                           'Open a new document.')
        self.AddSimpleTool(602, self.SaveImage, 'Save',
                           'Save the current document.')
        self.AddSimpleTool(603, self.SaveAsImage, 'Save As',
                           'Save the current document under a differend name.')
        self.AddSimpleTool(604, ConfigImage, 'Settings',
                           'Open the configuration window.')
        self.AddSeparator()
        self.AddSimpleTool(605, self.QuitImage, 'Quit', 'Quit gEcrit')
        self.AddSeparator()
        self.AddSimpleTool(606, self.CloseImage, 'Close tab',
                           'Close the current tab.')

        self.AddSeparator()
        self.AddSimpleTool(609, self.PrintImage, "Print",
                           "Print the current document.")
        self.AddSimpleTool(610, self.RunImage, "Run",
                           "Run the current file.(Python only)")
        self.Realize()
