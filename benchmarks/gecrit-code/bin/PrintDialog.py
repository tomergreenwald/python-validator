#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx.html
import wx


class PrettyPrinter(wx.html.HtmlEasyPrinting):
    """
    PrettyPrinter

    Provides the necessary functions for printing
    documents.

    Build the GUI and provides the appropriate controls.
    """

    def __init__(self, filename, text_id, parent=None):
        """
        __init__

        Initializes the HtmlEasyPrinting object.

        Creates the necessary dialogs.
        Retrieves the content to be printed.

        """
        wx.html.HtmlEasyPrinting.__init__(self)
        self.parent = parent
        data = wx.PrintDialogData()

        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.SetMinPage(1)
        data.SetMaxPage(5)
        data.SetAllPages(True)

        dlg = wx.PrintDialog(parent, data)

        dlg.Destroy()
        self.cur_doc = wx.FindWindowById(text_id)

        self.DoPrint(filename)

    def DoPrint(self,filename):
        """
        DoPrint

        Sets the print hedear and calls the HTML
        generation function.

        Sends the output to HtmlEasyPrinting object for printing.
        """
        self.SetHeader(filename)
        self.PrintText(self.cur_doc.ToHTML(), filename)
