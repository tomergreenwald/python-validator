#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os.path
from configClass import *




class MainMenu(wx.MenuBar):
    """
    MainMenu

    Creates the application menubar.
    Provides a few helper functios.

    """
    def __init__(self, parent, id=wx.ID_ANY):
        """
        __init__

        Build the application menu. Adds the entryes, creates recent
        file list.

        """
        #creating application menu
        self.parent = parent
        menubar = wx.MenuBar()
        self.recent_dict = {}
        wx.MenuBar.__init__(self)
        file = wx.Menu()
        self.recent_files = wx.Menu()
        edit = wx.Menu()
        help = wx.Menu()
        search = wx.Menu()
        view = wx.Menu()
        document = wx.Menu()

        if Config.GetOption("RecentFiles"):  # check if list is empty
            self.last_recent = Config.GetOption("RecentFiles")[-1]
        else:
            self.last_recent = ""

        file.Append(500, '&New Tab\tCtrl+N', 'Open a new tab.')
        file.Append(501, '&Open\tCtrl+O', 'Open a new document.')
        file.Append(502, '&Save\tCtrl+S', 'Save the document.')
        file.Append(503, 'Save As',
                    'Save the document under a different name.')
        file.Append(506, "Save All",
                    "Saves all the open documents that have a path.")
        file.Append(507,"Reload\tCtrl+R","Reload the current file from disk.")
        file.Append(504, '&Print\tCtrl+P', 'Print the current document.')
        file.Append(505, 'Close &Tab\tCtrl+W', 'Close the current tab.')



        self.recent_submenu = wx.Menu()

        self.GenerateRecentFiles()

        file.AppendMenu(700,"Recent files\tShow the last opened files.",self.recent_submenu)
        file.AppendSeparator()
        quit = wx.MenuItem(file, 506, '&Quit\tCtrl+Q', 'Quit gEcrit.')
        file.AppendItem(quit)


        edit.Append(520, "&Undo\tCtrl+Z", "Cancel the last action.")
        edit.Append(521, "&Redo\tCtrl+Y", "Bring back the last action.")
        edit.AppendSeparator()
        edit.Append(522, "&Cut\tCtrl+X", "Cut the selection.")
        edit.Append(523, "C&opy\tCtrl+C", "Copy the selection.")
        edit.Append(524, "P&aste\tCtrl+V", "Paste the selection.")
        edit.AppendSeparator()
        edit.Append(525, "Select All\tCtrl+A",
                    "Select all the document.")
        edit.Append(562, "Select Code Block\tCtrl+Shift+A",
                    "Select all the current code block.")
        edit.AppendSeparator()
        edit.Append(529, "Indent\tCtrl+K", "Indent the selected lines.")
        edit.Append(528, "Dedent\tCtrl+J", "Dedent the selected lines.")

        edit.Append(559, "Comment Lines\tCtrl+Shift+C","Comment the selected lines.")
        edit.Append(560, "Uncomnet Lines\tCtrl+Shift+X","Uncomment the selected lines.")

        edit.AppendSeparator()
        edit.Append(526, "Insert date",
                    "Insert the date at cursor position.")
        edit.AppendSeparator()
        edit.Append(527, "Preferences\tCtrl+E",
                    "Open the configuration window.")

        search.Append(530, "Find\tCtrl+F",
                      "Search text in the current document.")
        search.Append(531, "Find and Replace\tCtrl+H",
                      "Search and replace text in the current document.")

        view.Append(535, "Zoom In\tCtrl++",
                    "Increase the size of the text.")
        view.Append(536, "Zoom Out\tCtrl+-",
                    "Decrease the size of the text.")
        view.Append(537, "Normal Size\tCtrl+0",
                    "Set the size of the text to normal.")
        view.AppendSeparator()
        view.AppendCheckItem(538, "Line Numbers",
                             "Show/Hide line numbers.").Check(Config.GetOption("LineNumbers"))
        view.AppendCheckItem(539, "Fold Marks", "Show/Hide fold marks.").Check(Config.GetOption("FoldMarks"))
        view.AppendCheckItem(540, "White Space",
                             "Show/Hide white spaces.").Check(Config.GetOption("Whitespace"))
        view.AppendCheckItem(541, "Indentation Guides",
                             "Show/Hide indentation guides.").Check(Config.GetOption("IndetationGuides"))
        view.AppendCheckItem(546, "Edge Line",
                             "Show/Hide the edge line.").Check(Config.GetOption("EdgeLine"))
        view.AppendCheckItem(547, "Syntax Highlight",
                             "Enable/Disable Syntax Highlight.").Check(Config.GetOption("SyntaxHighlight"))
        view.AppendSeparator()
        view.AppendCheckItem(542, "Python Shell",
                             "Stop/Start a python shell.").Check(Config.GetOption("PythonShell"))
        view.AppendCheckItem(543, "OS Shell", "Stop/Start an OS shell.").Check(Config.GetOption("BashShell"))
        view.AppendCheckItem(544, "Source Browser",
                             "Show/Hide the source browser.").Check(Config.GetOption("SourceBrowser"))
        view.AppendCheckItem(555, "FileTree",
                             "Show/Hide the file browser.").Check(Config.GetOption("FileTree"))

        view.Append(556,"Class Hierarchy Tree","Tries to build a class hierachy tree from the opened documents")

        view.AppendCheckItem(545, "Statusbar", "Show/Hide statusbar.").Check(Config.GetOption("StatusBar"))
        view.AppendCheckItem(557,"Fullscreen\tF11","Toggle Fullscreen mode.")

        document.Append(549, "Send to Pastebin\tCtrl+I",
                        "Submit the current document to pastebin.com")
        document.Append(548, "Check for errors\tCtrl+B",
                        "Check the current document for errors.(python only)")

        document.Append(551,"Remove Trailing  Spaces","Remove spaces at the end of the line.")
        document.Append(558, "Run File\tF5","Run the current document.(python only)")
        document.Append(561,"Convert to HTML","Convert the current document to HTML format.")
        help.Append(550, "About", "Open the about window.")

        self.Append(file, '&File')
        self.Append(edit, '&Edit')
        self.Append(search, "&Search")
        self.Append(view, "&View")
        self.Append(document, "&Document")
        self.Append(help, '&Help')


    def NewTabHelper(self,event):
        """
        NewTabHelper

        Used to help for calling the NewTab function of this object
        parent.
        """
        self.parent.NewTab(0,os.path.split(self.recent_dict[event.GetId()])[-1],
        self.recent_dict[event.GetId()])
        self.last_recent = self.recent_dict[event.GetId()]

    def ClearRecentFiles(self):
        """
        ClearRecentFiles

        Deletes all the entryes under the Recent Files submenu.
        """
        #deleting items from menu
        items = self.recent_submenu.GetMenuItems()
        for i in items:
            self.recent_submenu.DeleteItem(i)

    def GenerateRecentFiles(self):
        """
        GenerateRecentFiles

        Takes the recent files list from config and generates
        a Recent Files submenu with them.
        Binds the events to them with NewTabHelper.
        """
        #generating new items
        st_id = 701
        last_nm = ""
        #cleaning it first (must have less than 10 elements)
        lst = Config.GetOption("RecentFiles")
        if len(lst) >10:
            while len(lst) > 10:
                lst.remove(lst[0])
            Config.ChangeOption("RecentFiles",lst)

        lst = Config.GetOption("RecentFiles") # refreshing list
        # creating recent file menu list

        for i in lst:
            if last_nm != i:
                self.recent_submenu.Append(st_id,i)
                st_id+=1
                last_nm = i


        #binding events
        st_id = 701
        items = self.recent_submenu.GetMenuItems()
        for item in items:
            self.parent.Bind(wx.EVT_MENU, self.NewTabHelper,id=item.GetId())
            self.recent_dict[item.GetId()] = item.GetLabel()


    def UpdateRecentFiles(self):
        """
        UpdateRecentFiles

        Calls the 2 function that are involved in creating a new
        Recent Files submenu.
        """
        self.ClearRecentFiles()
        self.GenerateRecentFiles()
