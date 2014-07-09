#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import wx.lib.inspection
from configClass import *
from logClass import *
from SyntaxHighlight import *
from logClass import *

try:
    import enchant
    from SpellChecker import *
    NO_SPELL_CHECK = False
except:
    print "module enchant not found."
    NO_SPELL_CHECK = True



class StcTextCtrl(wx.stc.StyledTextCtrl):
    """
    StcTextCtrl

    Provides the editing facilities and function.
    Creates the editor object and its environment.
    Stores its file path.
    """
    def __init__(self, parent, id, src_br, file_path="New Document"):
        """
        __init__

        Initializes the StyledTextCtrl object and sets up its
        environment.
        Binds the proper events to their functions and sets up the
        spell checker object.
        """
        wx.stc.StyledTextCtrl.__init__(self, parent, id, pos=(0, 0),
                size=(1, 1))
        self.CharCount = 0
        self.SaveTarget = file_path
        self.parent = parent
        if ".py" in self.SaveTarget: self.py_file = True
        else: self.py_file = False

        if file_path != "New Document" and file_path != "":
            self.LoadFile(file_path)

        else:

            self.SaveTarget = ""

            if Config.GetOption("DefaultTextAct"):
                self.AppendText(Config.GetOption("DefaultText"))


        self.SaveRecord = self.GetText()

        self.HOMEDIR = os.path.expanduser('~')

        self.nb = wx.FindWindowById(900)

        self.StatusBar = wx.FindWindowById(999)
        self.InitSrcBr = src_br
        self.text_id = id
        if not NO_SPELL_CHECK:
            self.Bind(wx.stc.EVT_STC_CHARADDED, self.OnSpellCheck)
            self.Bind(wx.EVT_KEY_DOWN, self.OnCheckSpace)

        self.last_word = ""
        self.spell_error = False

        if Config.GetOption("Autosave") == True:
            self.Bind(wx.stc.EVT_STC_CHARADDED, lambda event: self.Autosave(event,
                      Config.GetOption("Autosave Interval")))

        self.brace_dict={
                    40:")",
                    91:"]",
                    123:"}",
                    39:"'",
                    34:'"'
                    }

        self.file_exts = {
                    "py"   : ".py Python",
                    "pyw"  : ".pyw Python",
                    "cpp"  : ".cpp C++",
                    "h"    : ".h C/C++",
                    "txt"  : ".txt Text",
                    "sh"   : ".sh Bash",
                    "bat"  : ".bat Batch",
                    "conf" : ".conf Config",
                    "php"  : ".php PHP",
                    "html" : ".html HTML",
                    "xhtml": ".xhtml XHTML",
                    "tcl"  : ".tcl Tcl",
                    "pl"   : ".pl Perl",
                    "c"    : ".c C",
                    "rb"   : ".rb Ruby",
                    "js"   : ".js Javascript",
                    "java" : ".java Java",
                    "lua"  : ".lua LUA",
                    "pm"   : ".pm Perl Module",
                    "vbs"  : ".vbs Visual Basic"
                    }

        self.Bind(wx.stc.EVT_STC_CHARADDED, self.OnCompBrace)
        try:
            self.ext = self.file_exts[self.SaveTarget.split(".")[-1].lower()]
            self.SetStatusFileExt()
        except:
            self.ext = "Unknown format"
            self.SetStatusFileExt()

        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.UpdateCords)

        self.Bind(wx.stc.EVT_STC_UPDATEUI, lambda event: self.OnUpdateUI)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK,
                     self.OnMarginClick)

        self.TabCount = self.text_id

        self.Bind(wx.EVT_KEY_UP,  self.AutoIndent)


    def OnReload(self,event):
        """
        OnReload

        Loads the current file from the hard disk once again.
        Checks for its existence first. If it does not exists,
        prompts the user.
        """
        if self.SaveTarget != "":
            if os.path.exists(self.SaveTarget):
                self.LoadFile(self.SaveTarget)
                Log.AddLogEntry("Reloaded "+self.SaveTarget)

            else:
                fl_not_exists = wx.MessageDialog(self,"The file "+self.SaveTarget+" does\
 not exists. Do you wish to save it?","Missing File",style = wx.YES | wx.NO)
                if fl_not_exists.ShowModal() == 5103:
                    self.Save(0)
        else:
                message = wx.MessageDialog(self,"The file seems unsaved, it does not exists\
 on the disk. Do you wish to save it?","File Not Saved",
                style = wx.YES | wx.NO)
                if message.ShowModal() == 5103:
                    self.Save(0)


    def OnCompBrace(self,event):
        """
        OnCompBrace

        If the feature is enabled, it adds a closing brace
        at the current cursor position.
        """
        key = event.GetKey()
        if key in [40,91,123,39,34]:
            if Config.GetOption("BraceComp"):
                self.AddText(self.brace_dict[key])
                self.CharLeft()
        event.Skip()

    def SaveAs(self, event):
        """
        SaveAs

        Ask the user for a path via a file dialog and the uses
        the StyledTextCtrl's function to write the date to file.
        Returns False if the user did not complete the process.
        Checks if there is a lexer for the file type and enables
        it if the option is active.
        Adds a log entry.
        """
        SaveFileAs = wx.FileDialog(None, style=wx.SAVE)
        parent_frame = self.parent.GetParent().GetParent().GetParent().GetParent().GetParent().GetParent()
        if parent_frame.menubar.last_recent != "":
            SaveFileAs.SetDirectory(parent_frame.menubar.last_recent)
        else:
            SaveFileAs.SetDirectory(self.HOMEDIR)
        if SaveFileAs.ShowModal() == wx.ID_OK:
            SaveAsFileName = SaveFileAs.GetFilename()
            SaveAsPath = SaveFileAs.GetDirectory() + "/" + \
                SaveAsFileName

            self.SaveFile(SaveAsPath)

            if Config.GetOption("StripTrails"):
                self.OnRemoveTrails(0)

            SaveContent = self.GetText()

            self.SaveTarget = SaveAsPath

            if Config.GetOption("StatusBar"):
                self.StatusBar.SetStatusText("Saved as" + SaveAsPath)

            self.nb.SetPageText(self.nb.GetSelection(), SaveAsFileName)
            self.InitSrcBr.RefreshTree(self.text_id, SaveAsPath)

            self.SaveRecord = SaveContent
            if self.py_file:
                SyntCol.ActivateSyntaxHighLight(self.text_id)

            SaveFileAs.Destroy()
            return True
        else:
            SaveFileAs.Destroy()
            return False

    def Save(self, event):
        """
        Save

        Checks if the objects file path is valid and saves to it.
        If not, it calls the SaveAs function to.
        Checks if there is a lexer for the file type and enables
        it if the option is active.
        Adds a log entry.
        """
        if self.SaveTarget == "" or self.SaveTarget == "New Document":
            self.SaveAs(0)
            return

        try:

            self.SaveFile(self.SaveTarget)

            if Config.GetOption("StatusBar"):
                self.StatusBar.SetStatusText("Saved")

            if Config.GetOption("StripTrails"):
                self.OnRemoveTrails(0)

            SaveContent = self.GetText()
            Log.AddLogEntry("Saved file " + self.SaveTarget)
            self.InitSrcBr.RefreshTree(self.text_id, self.SaveTarget)
            self.SaveRecord = SaveContent
            if self.py_file:
                SyntCol.ActivateSyntaxHighLight(self.text_id)

        except:
            self.SaveAs(0)

    def OnSpellCheck(self, event):
        """
            OnSpellCheck

            Delivers the data to the spell checker, and manages
            the underlineing and clearing of the text.
        """
        if Config.GetOption("SpellCheck"):
            st = self.WordStartPosition(self.GetCurrentPos(), False)
            end = self.WordEndPosition(self.GetCurrentPos(), False)
            word = self.GetTextRange(st, end)
            self.last_word = word
            spelled_ok = WordSpeller.CheckWord(word)

            if not spelled_ok:
                self.StartStyling(st, wx.stc.STC_INDIC2_MASK)
                self.SetStyling(end - st, wx.stc.STC_INDIC2_MASK)
                self.spell_error = True
            else:
                self.StartStyling(st, wx.stc.STC_INDIC2_MASK)
                self.SetStyling(end - st, 0)
                self.spell_error = False
            event.Skip()
            return end
        event.Skip()

    def OnCheckSpace(self, event):
        """
        OnCheckSpace

        Helper function for the OnSpellCheck function.
        Checks if the last entered characted is a space.
        If it is, calls OnSpellCheck.
        """
        key = event.GetKeyCode()
        if key == 32:
            if self.spell_error:
                if Config.GetOption("SpellSuggestions"):
                    self.CallTipShow(self.GetCurrentPos(), ("\n").join(WordSpeller.GetSuggestion(self.last_word)))
        event.Skip()

    def Autosave(self, event, interval):
        """
        AutoSave

        Count the numbers of characters entered. If they reach a
        value, calls Save.

        Adds a log entry.

        """
        if self.CharCount == interval:
            self.Save(0)
            Log.AddLogEntry("Autosaved "+self.SaveTarget)
            self.CharCount = 0
        else:

            self.CharCount += 1
        event.Skip()

    def OnDedent(self, event):
        """
        OnDedent

        Dedents the selected lines.
        """
        self.BackTab()

    def OnIndent(self, event):
        """
        OnIndent

        Indents the selected lines.
        """
        sel_end = self.LineFromPosition(self.GetSelectionEnd())
        sel_start = self.LineFromPosition(self.GetSelectionStart())

        for line in xrange(sel_start, sel_end + 1):
            self.SetLineIndentation(line, self.GetLineIndentation(line) +
                                    self.GetIndent())

    def OnZoomIn(self, event):
        """
        OnZoomIn

        Zooms in the editor.
        """
        self.ZoomIn()
        event.Skip()

    def OnZoomOut(self, event):
        """
        OnZoomOut

        Zooms out the editor.
        """
        self.ZoomOut()
        event.Skip()

    def OnResetZoom(self, event):
        """
        OnResetZoom

        Resets the zoom at the normal state.
        """
        self.SetZoom(0)
        event.Skip()

    def OnRedo(self, event):
        """
        OnRedo

        Redos the editor one step.
        """
        if self.CanRedo():
            self.Redo()
        event.Skip()

    def OnUndo(self, event):
        """
        OnUndo

        Undos the editor one step.
        """
        if self.CanUndo():
            self.Undo()
        event.Skip()

    def OnCut(self, event):
        """
        OnCut

        Cuts the selected text and copies it to clipboard.
        """
        self.Cut()
        event.Skip()

    def OnCopy(self, event):
        """
        OnCopy

        Copies the selected text to clipboard.
        """
        self.Copy()
        event.Skip()

    def OnSelectAll(self, event):
        """
        OnSelectAll

        Selects all the text in the editor.
        """
        self.SelectAll()
        event.Skip()

    def OnPaste(self, event):
        """
        OnPaste

        Pastes from clipboard.
        """
        self.Paste()
        event.Skip()

    def OnInsertDate(self, event):
        """
        OnInsertDate

        Find the date and inserts it in the current postion.
        """
        self.AddText(str(time.ctime()))
        event.Skip()

    def OnRemoveTrails(self,event):
        """
        OnRemoveTrails

        Removes the trailing whitespace in the current document.

        """
        line_nr = self.GetLineCount()
        ln = 1
        while ln <= line_nr:
            ln += 1
            length = self.LineLength(ln)
            if " " not in self.GetLine(ln): continue
            st = self.GetLineEndPosition(ln) - length
            end = self.GetLineEndPosition(ln)
            txt = self.GetTextRange(st,end)
            self.SetTargetStart(st)
            self.SetTargetEnd(end)
            self.ReplaceTarget(txt.rstrip(" ").rstrip("\t"))


    def OnComment(self,event):
        """
        OnComment

        Appends a '#' at the eggining of the selected lines.
        """
        sel_end = self.LineFromPosition(self.GetSelectionEnd())
        sel_start = self.LineFromPosition(self.GetSelectionStart())
        for line in range(sel_start, sel_end+1):
            line_text = "# "+self.GetLine(line)
            ln_length = self.LineLength(line)
            st = self.GetLineEndPosition(line) - ln_length
            end = self.GetLineEndPosition(line)
            self.SetTargetStart(st+1)
            self.SetTargetEnd(end+1)
            self.ReplaceTarget(line_text)


    def OnUnComment(self,event):
        """
        OnUnComment

        Removes the '#' at teh beggining of the selected lines.
        """
        sel_end = self.LineFromPosition(self.GetSelectionEnd())
        sel_start = self.LineFromPosition(self.GetSelectionStart())
        for line in range(sel_start, sel_end+1):
            line_text = self.GetLine(line)
            #Remove Comment:
            comment = line_text.find('#')
            if comment > -1:
                line_text = line_text[comment+1:]
                ln_length = self.LineLength(line)
                st = self.GetLineEndPosition(line) - ln_length
                end = self.GetLineEndPosition(line)
                self.SetTargetStart(st+1)
                self.SetTargetEnd(end+1)
                self.ReplaceTarget(line_text)

    def SetStatusFileExt(self):
        self.StatusBar.SetStatusText(self.ext+" file.",2)

    def ToHtmlHelper(self,event):
        save_path = wx.FileDialog(None, style=wx.SAVE)
        if save_path.ShowModal() == wx.ID_OK:
            html_file = open(save_path.GetPath(),"w")
            html_file.write(self.ToHTML())
            html_file.close()

    def ToHTML(self):
        """
        ToHTML

        Formats the document text to HTML form.
        Returns it.
        """
        text = self.GetText().replace('&', "&amp;").replace('<', "&lt;").replace('>',
                "&gt;")

        if self.GetLineCount():
            text = "1<a href=\"#\">00000</a>" + text.replace(' ',
                    " &nbsp;")
            x = 0
            l = len(text)
            line = 2
            n = ""
            while x < l:
                if text[x] == "\n":
                    n = n + "\n" + str(line)
                    if line < 10:
                        n = n + "<a href=\"#\">00000</a>"
                    elif line < 100:
                        n = n + "<a href=\"#\">0000</a>"
                    elif line < 1000:
                        n = n + "<a href=\"#\">000</a>"
                    else:
                        n = n + "<a href=\"#\">00</a>"
                    line = line + 1
                else:
                    n = n + text[x]
                x = x + 1

            text = n

        thehtml = \
            "<html><body link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">" + \
            text.replace("\n", "\n<br>") + "</span></body></html>"
        return thehtml

    def UpdateCords(self, event):
        """
        UpdateCords

        Updates the x,y coordinates of the cursor.
        """

        self.StatusBar.SetStatusText("line: " + str(self.GetCurrentLine()) +
                "    col: " + str(self.GetColumn(self.GetCurrentPos())),
                1)
        event.Skip()

    def AutoIndent(self, event):
        """
        AutoIndent

        Responsible for the autoindentation feature.

        """
        key = event.GetKeyCode()
        if key == wx.WXK_NUMPAD_ENTER or key == wx.WXK_RETURN:
            if Config.GetOption("Autoindentation") == True:
                try:  #to silence a useless error message

                        line = self.GetCurrentLine()
                        if self.GetLine(line - 1)[-2] == ":":
                            self.SetLineIndentation(line, self.GetLineIndentation(line -
                                    1) + self.GetIndent())
                            self.LineEnd()
                        else:
                            self.SetLineIndentation(line, self.GetLineIndentation(line -
                                    1))
                            self.LineEnd()
                except: pass
        event.Skip()


    def OnUpdateUI(self ,evt):
        """
        OnUpdateUI

        Responsible for the bad brace check feature.
        """


        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == wx.stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == wx.stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

        evt.Skip()


    def OnMarginClick(self, evt):
        """
        OnMarginClick

        Responsible for the interaction of the user with
        code folding.
        """

        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(lineClicked) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)
        evt.Skip()


    def FoldAll(self):
        """
        FoldAll

        Folds all the code when given the command.

        """

        lineCount = self.GetLineCount()
        expanding = True

        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & wx.stc.STC_FOLDLEVELHEADERFLAG and level & wx.stc.STC_FOLDLEVELNUMBERMASK == \
                wx.stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum + 1, lastChild)

            lineNum = lineNum + 1


    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        """
        Expand

        Expands the provided line in argument line.
        """

        lastChild = self.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

                    line = Expand(text_id, line, doExpand, force, visLevels -
                                  1)
                else:

                    if doExpand and self.GetFoldExpanded(line):
                        line = Expand(text_id, line, True, force, visLevels -
                                      1)
                    else:
                        line = Expand(text_id, line, False, force, visLevels -
                                      1)
            else:
                line = line + 1

        return line


    def OnSelectCodeBlock(self,event):
        up_line = self.GetCurrentLine()
        down_line = up_line
        indent = self.GetLineIndentation(up_line)

        while True:
            if self.GetLineIndentation(up_line) >= indent:
                up_line -= 1
            elif self.GetLineIndentation(up_line) < indent:
                if self.GetLine(up_line).isspace():
                    up_line -= 1
                else: break


        while True:
            if self.GetLineIndentation(down_line) >= indent:
                down_line += 1
            elif self.GetLineIndentation(down_line) < indent:
                if self.GetLine(down_line).isspace():
                    down_line += 1
                else: break

        self.SetSelection(self.GetLineEndPosition(up_line),
                        self.GetLineEndPosition(down_line-1))
