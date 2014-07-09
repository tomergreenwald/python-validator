#!/usr/bin/python
# -*- coding: utf-8 -*-

# Anthony Labarre © 2013
#
# An extension for nautilus to have it launch squeeze on the selected item.
#
# TODO:
# * allow selection of multiple files

# Imports ---------------------------------------------------------------------
from gi.repository import Nautilus, GObject
from squeeze import *
import urllib


def URItoPath(uri):
    """Returns the path to a file pointed to by an URI."""
    return urllib.unquote(str(uri)[7:])


class ColumnExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        # initialize the squeezer
        self.S = Squeezer()
        #self.S.setKeepArchives(args.keep)

    def menu_activate_cb(self, menu, file):
        """Implements the action to be triggered when the item is clicked."""
        self.S.compress(URItoPath(file.get_uri()))

    def get_file_items(self, window, files):
        """The item that will show up in the context menu."""
        if len(files) != 1:
            return

        file = files[0]

        item = Nautilus.MenuItem(
            name="SimpleMenuExtension::Show_File_Name",
            label="Squeeze %s" % file.get_name(),
            tip="Squeeze %s" % file.get_name()  # TODO no effect
        )
        item.connect('activate', self.menu_activate_cb, file)

        return [item]
