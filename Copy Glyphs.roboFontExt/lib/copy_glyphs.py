from vanilla import ColorWell, Button, HorizontalLine, Window, CheckBox, PopUpButton, TextBox, Sheet, ProgressBar
from defconAppKit.controls.glyphCollectionView import GlyphCollectionView
from defconAppKit.controls.fontList import FontList
from mojo.roboFont import OpenWindow, AllFonts
from AppKit import NSColor
from lib.tools.misc import NSColorToRgba


class CopyGlyphs:

    def __init__(self):
        self.doMarkGlyphs = 0
        self.doOverwrite = 1
        self.sourceFontList = AllFonts()
        self.destinationFontList = AllFonts()
        self.source_font = self.sourceFontList[0]
        self.destination_fonts = None
        self.glyphs = None
        self.mark = NSColor.redColor()

        sl = []
        for f in self.sourceFontList:
            if f.info.familyName != None:
                fn = f.info.familyName
            else:
                fn = "None"
            if f.info.styleName != None:
                fs = f.info.styleName
            else:
                fs = "None"
            sl.append(fn+" "+fs)

        ## create a window
        self.w = Window((700, 500), "Copy Glyphs", minSize=(700, 500))
        self.w.sourceTitle = TextBox((15, 20, 200, 20), "Source Font:")
        self.w.sourceFont = PopUpButton((15, 42, -410, 20), sl, callback=self.sourceCallback)
        self.w.glyphs = GlyphCollectionView((16, 70, -410, -65), initialMode="list", enableDelete=False, allowDrag=False, selectionCallback=self.glyphCallback)
        self._sortGlyphs(self.source_font)
        self.w.desTitle = TextBox((-400, 20, 200, 20), "Destination Fonts:")
        self.w.destinationFonts = FontList((-400, 42, -15, -115), self.destinationFontList, selectionCallback=self.desCallback)
        self.w.overwrite = CheckBox((-395, -105, 130, 22), "Overwrite glyphs", callback=self.overwriteCallback, value=self.doOverwrite)
        self.w.markGlyphs = CheckBox((-395, -84, 100, 22), "Mark Glyphs", callback=self.markCallback, value=self.doMarkGlyphs)
        self.w.copyButton = Button((-115, -40, 100, 20), 'Copy Glyphs', callback=self.copyCallback)
        self.w.line = HorizontalLine((10, -50, -10, 1))
        self._checkSelection()
        self._updateDest()
        ## open the window
        self.w.open()

    def _updateDest(self):
        des = list(self.sourceFontList)
        des.remove(self.source_font)
        self.w.destinationFonts.set(des)

    def _sortGlyphs(self, font):
        gs = font.keys()
        gs.sort()
        self.w.glyphs.set([font[x] for x in gs])

    def _altName(self, font, glyph):
        name = glyph + '.copy'
        count = 1
        while name in font.keys():
            name = name + str(count)
            count += 1
        return name


    def _checkSelection(self):
        if self.glyphs == None or len(self.glyphs) == 0:
            if len(self.source_font.selection) != 0:
                self.glyphs = self.source_font.selection
                select = []
                for i, g in enumerate(self.w.glyphs):
                    if g.name in self.glyphs:
                        select.append(i)
                print(select)
                self.w.glyphs.setSelection(select)
        print(self.glyphs)


    def copyGlyphs(self, glyphs, source_font, destination_fonts, overwrite, mark):
        for glyph in glyphs:
            for font in destination_fonts:
                if glyph in font.keys() and overwrite == 0:
                    n = self._altName(font, glyph)
                else:
                    n = glyph

                font.insertGlyph(source_font[glyph], name=n)

                if mark == 1:
                    font[n].mark = NSColorToRgba(self.mark)

    def overwriteCallback(self, sender):
        self.doOverwrite = sender.get()

    def markCallback(self, sender):
        self.doMarkGlyphs = sender.get()
        if self.doMarkGlyphs == 1:
            self.w.colorWell = ColorWell((-265, -85, 100, 23), callback=self.colorCallback, color=self.mark)
        else:
            del self.w.colorWell

    def colorCallback(self, sender):
        self.mark = sender.get()

    def sourceCallback(self, sender):
        self.source_font = self.sourceFontList[sender.get()]
        self._sortGlyphs(self.source_font)
        self._checkSelection()
        self._updateDest()

    def glyphCallback(self, sender):
        self.glyphs = [self.w.glyphs[x].name for x in sender.getSelection()]

    def desCallback(self, sender):
        self.destination_fonts = [sender.get()[x] for x in sender.getSelection()]

    def copyCallback(self, sender):
        self.sheet = Sheet((300, 50), self.w)
        self.sheet.bar = ProgressBar((10, 20, -10, 10), isIndeterminate=True, sizeStyle="small")
        self.sheet.open()
        self.sheet.bar.start()
        self.copyGlyphs(self.glyphs, self.source_font, self.destination_fonts, self.doOverwrite, self.doMarkGlyphs)
        self.sheet.bar.stop()
        self.sheet.close()
        del self.sheet
        self.w.close()

OpenWindow(CopyGlyphs)