#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx.lib.inspection
import sys, subprocess
import collections
import wx.richtext
from configClass import *
from logClass import *
from aboutClass import *
from SyntaxHighlight import *
from Fonts import *
from ConfigWindow import *
from PrintDialog import *
from FindReplaceText import *
from SourceBrowser import *
from AutoCompletition import *
from ShellEmulator import *
from PastebinDialog import *
from SyntaxChecker import *
from StcControl import *
from DirTreeCtrl import *
from Menu import *
from Toolbar import *
from ClassHierarchyWin import *


class Editor(wx.Frame):
    """
    Editor

    This class is the entry point in the program.
    It creates all the user interface and initializes
    the required objects and classes.
    The functions that cannot go into another objects
    for diverse reasons go here.
    """
    def __init__(self, id, parent):
        """
        __init__

        Creates the user interface.
        Initializez the terminals if enabled.
        Creates the required GUI and non GUI objects.

        """
        SHELLTAB_ID = 4002
        BASH_ID = 4000
        PY_ID = 4001


        pathname = os.path.abspath(os.path.dirname((sys.argv)[0]))  #  Finding where
        os.chdir(pathname)  #  gEcrit is running

        self.SaveRecord = {}
        self.IdRange = []

        if "editorClass.py" not in (sys.argv)[-1]:
            self.TargetFile = os.path.normpath(os.path.realpath((sys.argv)[-1]))
            self.job_file = True
            Name = self.TargetFile.split("/")[-1]
        else:

            self.job_file = False
            self.TargetFile = "New Document"  #Default Name
            Name = "New Document"

        self.MainFrame = wx.Frame.__init__(self, parent, 1000, 'gEcrit',
                size=(700, 600))

        self.Bind(wx.EVT_CLOSE, self.OnQuit)


        self.StatusBar = self.CreateStatusBar()
        self.StatusBar.SetStatusText("Done")
        self.StatusBar.SetFieldsCount(3)
        self.StatusBar.SetId(999)
        if not Config.GetOption("StatusBar"):
            self.StatusBar.Hide()

        self.menubar = MainMenu(self)
        self.SetMenuBar(self.menubar)

        mega_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetIcon(wx.Icon('icons/gEcrit.png', wx.BITMAP_TYPE_PNG))

        self.text_id = 0

        main_splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D | wx.SP_BORDER)
        main_splitter.SetMinimumPaneSize(150)
        tab_panel = wx.Panel(main_splitter)
        nb_panel = wx.Panel(main_splitter)
        nb_panel.SetId(998)  #needed in configClass.py

        self.HOMEDIR = os.path.expanduser('~')
        os.chdir(os.path.abspath(self.HOMEDIR))

        ShellTabs = wx.Notebook(tab_panel, id=SHELLTAB_ID, size=(700,
                                100), style=wx.BORDER_SUNKEN)

        BashPanel = wx.Panel(ShellTabs)
        PythonPanel = wx.Panel(ShellTabs)
        self.BashShell = ShellEmulator(BashPanel, Config.GetOption("OSPath"),
                BASH_ID)
        self.PythonShell = ShellEmulator(PythonPanel, Config.GetOption("PyPath"),
                PY_ID)

        python_sizer = wx.BoxSizer(wx.VERTICAL)
        python_sizer.Add(self.PythonShell, 1, wx.ALL | wx.EXPAND)
        PythonPanel.SetSizer(python_sizer)
        PythonPanel.Fit()

        bash_sizer = wx.BoxSizer(wx.VERTICAL)
        bash_sizer.Add(self.BashShell, 1, wx.ALL | wx.EXPAND)
        BashPanel.SetSizer(bash_sizer)
        PythonPanel.Fit()

        if Config.GetOption("PythonShell") or Config.GetOption("BashShell"):
            if Config.GetOption("BashShell"):
                self.BashShell.OnRun(0, Config.GetOption("OSPath"))

                ShellTabs.AddPage(BashPanel, "OS Shell")

            if Config.GetOption("PythonShell"):
                self.PythonShell.OnRun(0, Config.GetOption("PyPath"))

                ShellTabs.AddPage(PythonPanel, "Python")
            will_split = True
        else:
            will_split = False

        self.nb = wx.aui.AuiNotebook(nb_panel, style=wx.aui.AUI_NB_TOP)
        self.nb.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnChangeTab)
        self.nb.SetId(900)  #Needed in StcControl.py
        nb_sizer = wx.BoxSizer(wx.VERTICAL)
        nb_sizer.Add(self.nb, 1, wx.EXPAND)
        nb_panel.SetSizer(nb_sizer)
        nb_panel.Fit()

        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        tab_sizer.Add(ShellTabs, 1, wx.EXPAND)
        tab_panel.SetSizer(tab_sizer)
        tab_panel.Fit()

        main_splitter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_splitter_sizer.Add(nb_sizer, 0, wx.EXPAND)
        main_splitter_sizer.Add(tab_sizer)
        main_splitter.SetSizer(main_splitter_sizer)
        main_splitter.Fit()

        os.chdir(pathname)

        main_splitter.SplitHorizontally(nb_panel, tab_panel, -1)

        if not will_split:
            main_splitter.Unsplit(tab_panel)

        f = wx.FindWindowById
        self.Bind(wx.EVT_MENU, lambda event: self.NewTab(event,
                  "New Document", "New Document"), id=500)
        self.Bind(wx.EVT_MENU, lambda event: self.OpenFile(event), id=
                  501)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).Save(event),
                  id=502)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).SaveAs(event),
                  id=503)
        self.Bind(wx.EVT_MENU, lambda event: self.OnPrint(event, (self.IdRange)[self.nb.GetSelection()]),
                  id=504)
        self.Bind(wx.EVT_MENU, lambda event: self.ManageCloseTab(event,
                  (self.IdRange)[self.nb.GetSelection()]), id=505)
        self.Bind(wx.EVT_MENU, lambda event: self.OnQuit(event), id=506)
        self.Bind(wx.EVT_MENU, self.SaveAll, id=506)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnReload(event),id = 507)

        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnUndo(event),
                  id=520)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnRedo(event),
                  id=521)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnCut(event),
                  id=522)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnCopy(event),
                  id=523)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnPaste(event),
                  id=524)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnSelectAll(event),
                  id=525)

        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnSelectCodeBlock(event),
                  id=562)


        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnInsertDate(event),
                  id=526)
        self.Bind(wx.EVT_MENU, lambda event: self.OnPrefs(event), id=527)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnDedent(event),
                  id=528)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnIndent(event),
                  id=529)

        self.Bind(wx.EVT_MENU, lambda event:f((self.IdRange)[self.nb.GetSelection()]).OnComment(event),
                  id=559)
        self.Bind(wx.EVT_MENU, lambda event:f((self.IdRange)[self.nb.GetSelection()]).OnUnComment(event),
                  id=560)

        self.Bind(wx.EVT_MENU, lambda event: FindRepl.FindDocText((self.IdRange)[self.nb.GetSelection()]),
                  id=530)
        self.Bind(wx.EVT_MENU, lambda event: FindRepl.ReplaceDocText((self.IdRange)[self.nb.GetSelection()]),
                  id=531)

        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnZoomIn(event),
                  id=535)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnZoomOut(event),
                  id=536)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnResetZoom(event),
                  id=537)

        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("LineNumbers",
                  self.menubar.IsChecked(538), self.IdRange), id=538)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("FoldMarks",
                  self.menubar.IsChecked(539), self.IdRange), id=539)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("Whitespace",
                  self.menubar.IsChecked(540), self.IdRange), id=540)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("IndetationGuides",
                  self.menubar.IsChecked(541), self.IdRange), id=541)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("EdgeLine",
                  self.menubar.IsChecked(546), self.IdRange), id=546)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("SyntaxHighlight",
                  self.menubar.IsChecked(547), self.IdRange), id=547)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("PythonShell",
                  self.menubar.IsChecked(542), self.IdRange), id=542)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("BashShell",
                  self.menubar.IsChecked(543), self.IdRange), id=543)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("SourceBrowser",
                  self.menubar.IsChecked(544), self.IdRange), id=544)
        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("FileTree",
                  self.menubar.IsChecked(555), self.IdRange), id=555)

        self.Bind(wx.EVT_MENU,lambda event: self.ClsHier.ShowMe(event,self.IdRange),id=556)

        self.Bind(wx.EVT_MENU, lambda event: Config.ChangeOption("StatusBar",
                  self.menubar.IsChecked(545), self.IdRange), id=545)
        self.Bind(wx.EVT_MENU, self.OnFullScreen, id=557)
        self.Bind(wx.EVT_MENU, lambda event: self.PastebinDlg.ShowMe(event,
                  (self.IdRange)[self.nb.GetSelection()]), id=549)
        self.Bind(wx.EVT_MENU, lambda event: SyntaxDoc.CheckSyntax(event,
                  (self.IdRange)[self.nb.GetSelection()]), id=548)
        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]).OnRemoveTrails(event),id=551)
        self.Bind(wx.EVT_MENU, lambda event: self.OnRun(event,self.IdRange[self.nb.GetSelection()]), id = 558)

        self.Bind(wx.EVT_MENU, lambda event: f((self.IdRange)[self.nb.GetSelection()]). ToHtmlHelper(event), id = 561)

        self.Bind(wx.EVT_MENU, lambda event: self.OnAbout(event), id=550)

        self.toolbar = MainToolbar(self, -1)

        self.FontCtrl = wx.FontPickerCtrl(self.toolbar, 607, size=(100,
                30))

        self.Bind(wx.EVT_FONTPICKER_CHANGED, lambda event: ChangeFont(event,
                  self.FontCtrl.GetSelectedFont(), self.IdRange))

        self.toolbar.AddControl(self.FontCtrl)
        self.toolbar.AddControl(wx.TextCtrl(self.toolbar, 608, size=(-1,
                                -1), style=wx.TE_PROCESS_ENTER))

        self.Bind(wx.EVT_TOOL, lambda event: self.NewTab(event,
                  "New Document", "New Document"), id=600)
        self.Bind(wx.EVT_TOOL, self.OpenFile, id=601)
        self.Bind(wx.EVT_TOOL, lambda event: f((self.IdRange)[self.nb.GetSelection()]).Save(event),
                  id=602)
        self.Bind(wx.EVT_TOOL, lambda event: f((self.IdRange)[self.nb.GetSelection()]).SaveAs(event),
                  id=603)
        self.Bind(wx.EVT_TOOL, self.OnPrefs, id=604)
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=605)
        self.Bind(wx.EVT_TOOL, lambda event: self.ManageCloseTab(event,
                  (self.IdRange)[self.nb.GetSelection()]), id=606)

        self.Bind(wx.EVT_TEXT_ENTER, lambda event: self.OnGotoBox(event,
                  (self.IdRange)[self.nb.GetSelection()]), id=608)

        self.Bind(wx.EVT_TOOL, lambda event: self.OnPrint(event, (self.IdRange)[self.nb.GetSelection()]),
                  id=609)
        self.Bind(wx.EVT_TOOL, lambda event: self.OnRun(event, (self.IdRange)[self.nb.GetSelection()]),
                  id=610)

        if self.TargetFile == "New Document":
            if os.path.exists(self.menubar.last_recent):
                self.TargetFile = self.menubar.last_recent
                Name = os.path.split(self.menubar.last_recent)[-1]

        self.NewTab(0, Name, self.TargetFile)

        mega_sizer.Add(self.toolbar, 0)

        mega_sizer.Add(main_splitter, 1, wx.EXPAND)

        self.SetSizer(mega_sizer)

        self.Centre()
        self.PastebinDlg = PastebinWin(self)
        self.GoConfWin = ConfFrame = CfgFrame(self.IdRange, None)
        self.ClsHier = HierarchyFrame(self)


    def OnFullScreen(self,event):
        """
        OnFullScreen

        Makes the main window fullscreen.
        """
        self.ShowFullScreen(not self.IsFullScreen(),wx.FULLSCREEN_NOCAPTION)


    def OnPrefs(self, event):
        """
        OnPrefs

        Shows the preferences window.
        """
        self.GoConfWin.ShowMe(0)



    def NewTab(self, event, nb, TargetFile):
        """
            NewTab

            Creates a new AUI NOTEBOOK tab, adds the contents,
            initializez a STC object for it and binds some of its events.
            Creates the sidebar, adds a notebook and adds its utilities
            in its tabs.
        """
        if TargetFile == False:
            return

        panel = wx.Panel(self)
        panel.identifierTag = nb
        TABBER = self.nb

        text_id = self.text_id

        splitter = wx.SplitterWindow(panel, -1, style=wx.SP_3D | wx.SP_BORDER)
        splitter.SetMinimumPaneSize(150)
        notebk_panel = wx.Panel(splitter)
        side_nb = wx.Notebook(notebk_panel, -1, pos=(0, 0), size=(-1, -1))
        side_nb.SetId(4003 + text_id)

        notebk_sizer = wx.BoxSizer(wx.HORIZONTAL)
        notebk_sizer.Add(side_nb, 1, wx.EXPAND)
        notebk_panel.SetSizer(notebk_sizer)
        notebk_panel.Fit()

        if TargetFile != "New Document" and TargetFile != "":
            file_dir = os.path.split(TargetFile)[0]
            lst = Config.GetOption("RecentFiles")
            lst.append(TargetFile)
            Config.ChangeOption("RecentFiles",lst)
            self.menubar.UpdateRecentFiles()
        else:
            file_dir = self.HOMEDIR + "/"

        dir_ctrl_panel = wx.Panel(side_nb)
        dir_ctrl = DirTreeCtrl(dir_ctrl_panel, -1, file_dir, pos=(0, 0),
                               size=(-1, -1))
        dir_ctrl.SetId(5000 + text_id)
        dir_ctrl_pnl_sz = wx.BoxSizer(wx.VERTICAL)
        dir_ctrl_pnl_sz.Add(dir_ctrl, 1, wx.EXPAND)
        dir_ctrl_panel.SetSizer(dir_ctrl_pnl_sz)
        dir_ctrl_panel.Fit()

        dir_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, lambda event: self.NewTab(event,
                      os.path.split(dir_ctrl.GetSelectedPath(event))[-1],
                      dir_ctrl.GetSelectedPath(event)))

        src_br_panel = wx.Panel(side_nb)
        text_panel = wx.Panel(splitter)
        text_panel.SetId(1001 + text_id)

        splitter.SplitVertically(notebk_panel, text_panel, 20)

        self.InitSrcBr = SrcBrowser(TargetFile, nb, text_id,
                                    src_br_panel)

        self.TextWidget = StcTextCtrl(text_panel, self.text_id, self.InitSrcBr,
                TargetFile)

        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_sizer.Add(self.TextWidget, 1, wx.EXPAND)
        text_panel.SetSizer(text_sizer)
        text_panel.Fit()

        self.IdRange.append(self.text_id)
        self.TextWidget.SetBufferedDraw(True)
        self.TextWidget.StyleSetFont(0, self.FontCtrl.GetSelectedFont())

        cur_doc = wx.FindWindowById(text_id)

        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN, wx.stc.STC_MARK_BOXMINUS,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER, wx.stc.STC_MARK_BOXPLUS,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARK_VLINE,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL, wx.stc.STC_MARK_LCORNER,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARK_BOXPLUSCONNECTED,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED,
                             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER,
                             "white", "#808080")

        Config.ApplyIDEConfig(text_id, TargetFile.split(".")[-1])

        cur_doc.SetXOffset(1)

        cur_doc.Bind(wx.EVT_KEY_DOWN, lambda event: AutoComp.OnKeyPressed(event,
                     text_id))


        self.TabCount = self.text_id
        (self.SaveRecord)[text_id] = wx.FindWindowById(text_id).GetText()



        src_sizer = wx.BoxSizer(wx.HORIZONTAL)
        src_sizer.Add(self.InitSrcBr, 1, wx.EXPAND)
        src_br_panel.SetSizer(src_sizer)
        src_br_panel.Fit()

        if Config.GetOption("SourceBrowser"):
            side_nb.AddPage(src_br_panel, "Source Browser")
        if Config.GetOption("FileTree"):
            side_nb.AddPage(dir_ctrl_panel, "File Browser")


        if Config.GetOption("SourceBrowser") or Config.GetOption("FileTree"):
            will_split = True
        else:
            will_split = False
        if not will_split:
            splitter.Unsplit(notebk_panel)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(splitter, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)
        main_sizer.Fit(panel)

        self.nb.AddPage(panel, str(nb), select=True)

        self.text_id += 1

    def OnRun(self, event, text_id):
        """
            Runs the current document in a xterm window, for testing.
        """
        cur_doc = wx.FindWindowById(text_id)
        cur_doc.Save(0)
        os.system("xterm -e sh runner.sh "+cur_doc.SaveTarget)

    def OnGotoBox(self, event, text_id):
        """
            OnGotoBox

            Finds the current document, and scrolls to the line indicated
            by its input upon the Return key.
        """
        cur_doc = wx.FindWindowById(text_id)
        Goto = wx.FindWindowById(608)

        scroll_pos = int(Goto.GetLineText(0))

        cur_doc.ScrollToLine(scroll_pos - 1)

    def OnPrint(self, event, text_id):
        """
            OnPrint

            Finds the document, sets the prints name, and calls the
            wxPython toolkit to print the contents
        """
        FileName = wx.FindWindowById(text_id).SaveTarget
        if "/" not in FileName:
            FileName = "ForPrint"
        GoPrint = PrettyPrinter(FileName, text_id, self)

    def OnAbout(self, event):
        """
            OnAbout

            Shows the about window.
        """
        ShowAbout = AboutWindow
        ShowAbout()

    def OnQuit(self, event):
        """
            OnQuit

            Closes the main window, stops the terminals, and kills the
            application process.
            It promps the user for confirmation.
        """
        Warn = wx.MessageDialog(None,
                                "Please make sure that your data is\
 saved.\nAre you sure you want to quit?",
                                "Are you sure?", style=wx.YES_NO)
        WarnAnswer = Warn.ShowModal()
        if WarnAnswer != 5104:
            if Config.GetOption("BashShell"):
                self.BashShell.OnClose(event)
            if Config.GetOption("PythonShell"):
                self.PythonShell.OnClose(event)
            quit()

    def ManageCloseTab(self, event, text_id):
        """
            ManageCloseTab

            Manages the process of closing a tab.
            Checks if document is saved, prompts the user if not.
            If this is the last tab in the application, it closes the
            terminals, the window and kills the application.
            If not, it decreases the number of tabs and delted the AUI
            NETBOOK page.
        """
        cur_doc = wx.FindWindowById(text_id)
        TextCheck = cur_doc.GetText()
        if cur_doc.SaveRecord != TextCheck:
            SavePrompt = wx.MessageDialog(None, "The file " + os.path.split(cur_doc.SaveTarget)[-1] +
                    " is not saved.\n\
Do you wish to save it?", "",
                    style=wx.CANCEL | wx.YES | wx.NO)
            PromptValue = SavePrompt.ShowModal()
            if PromptValue == 5103:     #yes
                if not cur_doc.Save(0):
                    return
            elif PromptValue == 5101:   #Cancel
                return
            elif PromptValue == 5102:
                pass

            SavePrompt.Destroy()

        if self.TabCount == 0:
            try:
                if Config.GetOption("BashShell"):
                    self.BashShell.OnClose(event)
                if Config.GetOption("PythonShell"):
                    self.PythonShell.OnClose(event)
            except:
                pass
            quit()
        else:
            self.TabCount -= 1
            try:
                self.IdRange.remove(text_id)
            except:
                pass
            self.nb.DeletePage(self.nb.GetSelection())
        event.Skip()

    def OpenFile(self, event):
        """
            OpenFile

            Collects a path for a new file via a file dialog.
            Calls NewTab with the collected path.
            Supports multiple path selection.
        """
        OpenFileGetPath = wx.FileDialog(None, style=wx.OPEN | wx.FD_MULTIPLE)
        if self.menubar.last_recent != "":
            OpenFileGetPath.SetDirectory(self.menubar.last_recent)
        else:
            OpenFileGetPath.SetDirectory(self.HOMEDIR)

        if OpenFileGetPath.ShowModal() == wx.ID_OK:
            paths = OpenFileGetPath.GetPaths()
            for f in paths:
                self.NewTab(0, os.path.split(f)[-1], f)
                Log.AddLogEntry("Opened file " + f)

        OpenFileGetPath.Destroy()

    def SetStatus(self, event, Text):
        """
            ResetStatus

            Sets the status of statusbar.
        """
        self.StatusBar.SetStatusText(Text)
        event.Skip()

    def ResetStatus(self, event):
        """
        ResetStatus

        Sets the status bar status to nothing.
        """
        self.StatusBar.SetStatusText("")
        event.Skip()

    def SaveAll(self, event):
        """
        SaveAll

        Saves all the current documents using the
        objects Save function.

        """
        for id in self.IdRange:
            cur_doc = wx.FindWindowById(id)
            if cur_doc.SaveTarget != "" and cur_doc.SaveTarget != \
                "New Document":
                cur_doc.Save(0)

    def OnChangeTab(self,event):
        wx.FindWindowById((self.IdRange)[self.nb.GetSelection()]).SetStatusFileExt()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = Editor(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
