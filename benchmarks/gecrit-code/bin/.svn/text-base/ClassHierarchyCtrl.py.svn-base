#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx


class HierarchyCtrl(wx.TreeCtrl):
    """
    HierarchyCtrl

    Manages data colection, processing and displaying of python
    classes from a source of files.
    Creates hierarchies of them in tree.
    """
    def __init__(self,parent, id = wx.ID_ANY, pos = (10,10), size=(-1,-1)):
        """
        __inti__

        Initializes the wx.TreeCtrl object, creates a tree root
        and the environment.
        """

        wx.TreeCtrl.__init__(self, parent, id,pos,size,style =
                                   wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                   wx.TR_HAS_VARIABLE_ROW_HEIGHT)

        self.root = self.AddRoot("Top")
        self.classes = []
        self.base_cls = []

    def GenerateHierarchies(self,id_range):
        """
        GenerateHierarchies

        Gathers data using helper functions and organizes it
        on the tree.
        First clears the tree with the help of the helper function
        and then populates it.
        """
        classed = []
        file_list = self.GetFileList(id_range)
        if file_list:
            for fl in file_list:
                cls = self.GetClassesFromFile(fl)
                if cls:
                    for c in cls:
                        self.classes.append(c)

        for c in self.classes:
            if not self.Inherits(c):
                self.base_cls.append(c)
                self.classes.remove(c)

        for c in self.base_cls:
            kids = self.FindChilds(c)
            if c not in classed:
                root = self.AppendItem(self.root,self.CleanName(c))
                classed.append(c)
            if kids:
                for n in kids:
                    root2 = self.AppendItem(root,self.CleanName(n))
                    kids_kids = self.FindChilds(n)
                    i = 0
                    if kids_kids:
                        kids_len = len(kids_kids)
                    while kids_kids:
                        try:
                            kid = kids_kids[i]
                        except: pass
                        has_kid = self.FindChilds(kid)
                        if not has_kid and i == kids_len: break
                        i+=1
                        root3 = self.AppendItem(root2,self.CleanName(kid))


        self.classes = []


    def FindChilds(self,cls):
        """
        FindChilds

        Finds the child classes of the suplied argument cls.
        Uses a helper class to check inheritance.
        Return the list if found. If not, returns False.
        """
        childs = []
        for i in self.classes:
            if self.InheritsFrom(cls,i):
                childs.append(i)
        if childs:
             return childs
        else:
             return False


    def GetClassesFromFile(self,file_path):
        """
        GetClassesFromFile

        Reads and collects the class statements from the suplied
        file_path argument.
        Creates a list of found classes and returns it if not empty.
        If empty, returns False.
        """
        classes = []
        try:
            fl = open(file_path,"r")
            for line in fl.readlines():
                if "class" in line and ":" in line:
                    line = line.strip("class ")
                    line2 = ""
                    for i in line:
                        if i!=":": line2+=i

                    classes.append(line2)
            if classes:
                 return classes
            else:
                 return False
            fl.close()
        except:
             return False


    def GetFileList(self,id_range):
        """
        GetFileList

        Iterates through all the editor objects, retrieves their
        file paths, gathers them into a list and returns it.
        If none Found, return False.
        """
        file_list = []
        for id in id_range:
            file_name = wx.FindWindowById(id).SaveTarget
            if file_name != "":
                file_list.append(file_name)
        if file_list:
             return file_list
        else:
             return False

    def Refresh(self,id_range):
        """
        Refresh

        Rebuild the class hierarchy tree.
        """
        self.DeleteChildren(self.root)
        self.GenerateHierarchies(id_range)


    def Inherits(self,cls_line):
        """
        Inherits

        Checks if the suplied argument cls_line has a base class.
        Returns True or False.
        """

        if "(" not in cls_line:
            return False
        else:
            lst = cls_line.split("(")

            if lst[-1][0] == ")":

                return False

            elif lst[-1][0] != " " or  lst[-1][-2] != ")":

                return True



    def GetClassBases(self,cls):
        """
        GetBaseClasses

        Iterates through the class list and makes a list with
        classes that have no base.
        """
        name = ""
        for i in cls:
            if i != ")":
                name+=i

        lst = name.split("(")
        cls_lst = lst[-1].split(",")
        if cls_lst:
             return cls_lst
        else:
             return False

    def CleanName(self,name):
        """
        CleanName

        Takes the argument name and clears all the syntactic
        elements to make it suitable for displaying.
        """
        name2 = ""
        for c in name:
            if c == "(":
                break
            else: name2+=c

        return name2.strip("\n")

    def InheritsFrom(self,base_class,child_class):
        """
        InheritsFrom

        Takes the sting argument base_class and checks if it the base
        of the string argument child_class.
        Returns True or False.
        """
        if self.CleanName(base_class) in child_class.split("(")[-1]:
            return True
        else:
            return False
