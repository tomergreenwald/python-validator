#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import enchant
except:
    print "Spell checker pyenchant is not available."


class NeatSpell:
    """
    Provides the necessary functions for spellchecking.
    Uses the enchant module.

    """

    def __init__(self):
        """
        __init__

        Initializes the enchant module, sets the language
        dictionary.
        """
        try:
            self.dictionary = enchant.Dict()
        except enchant.Error:
            print "The Dictionary could not be identified.\n  Falling back to English."
            self.dictionary = enchant.Dict("en_US")

    def CheckWord(self, word):
        """
        CheckWord

        Calls enchant to check the suplied argument word.
        """
        return self.dictionary.check(word)

    def GetSuggestion(self, word):
        """
        GetSuggestion

        Calls the enchant library to generate
        spelling suggestion for the suplied argument
        word.
        """
        return self.dictionary.suggest(word)

    def ShowSpellDialog(self, event):
        """"
        ShowSpellDialog

        not implemented
        """
        pass


WordSpeller = NeatSpell()
