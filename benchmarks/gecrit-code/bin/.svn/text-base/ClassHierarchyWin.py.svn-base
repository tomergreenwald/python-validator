#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from ClassHierarchyCtrl import *


class HierarchyFrame(wx.Frame):
    """
    HierarchyFrame

    Provides a display space and controls for the
    ClassHierarchyCtrl object.
    """
    def __init__(self,parent,id = wx.ID_ANY):
        """
        __init__

        Build the frame GUI components and initializes the wx.Frame
        object.
        Initializes the ClassHierarchyCtrl object.
        """
        wx.Frame.__init__(self, parent,id,"Class Hierarchies",size=(300,500))
        self.panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree_ctrl = HierarchyCtrl(self.panel)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.refresh = wx.Button(self.panel,-1,"Refresh",pos=(200,400),
                                                         size=(-1,-1))

        self.close = wx.Button(self.panel,-1, "Close", pos = (250,400),
                                                       size=(-1,-1))
        self.button_sizer.Add(self.refresh,0)
        self.button_sizer.Add(self.close,0)

        panel_sizer.Add(self.tree_ctrl,1,wx.EXPAND)
        panel_sizer.Add(self.button_sizer,0)

        self.panel.SetSizer(panel_sizer)
        self.panel.Fit()
        self.Hide()

        self.Bind(wx.EVT_CLOSE, self.HideMe)
        self.refresh.Bind(wx.EVT_BUTTON, self.OnRefresh)
        self.close.Bind(wx.EVT_BUTTON, self.HideMe)


    def ShowMe(self,event,id_range):
        """
        ShowMe

        Makes window visible and refreshes the class hierarchy tree.
        """
        self.id_range = id_range
        self.tree_ctrl.Refresh(self.id_range)
        self.Show()

    def HideMe(self,event):
        """
        HideMe

        Hides the window.
        """
        self.Hide()

    def OnRefresh(self,event):
        """
        OnRefresh

        Calls the ClassHierarchyCtrl's function Refresh.
        """
        self.tree_ctrl.Refresh(self.id_range)
