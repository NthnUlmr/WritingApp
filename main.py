# <GPLv3_Header>
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# \copyright
#                    Copyright (c) 2024 Nathan Ulmer.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# <\GPLv3_Header>

##
# \mainpage Writing App
#
# \copydoc main.py

##
# \file main.py
#
# \author Nathan Ulmer
#
# \date \showdate "%A %d-%m-%Y"
#
# \brief An app with some of the features I want in writing applications built for long-form novel writing.
# - - -
# \section desc Details
# \par
# This app primarily uses tkinter to create the GUI and handle the backend for the interactible writing boxes.
# The book is really a collection of documents
# I want to be able to edit either the unstructured document or the formatted book and have those changes reflected on both ends
# \section a Example:
# \par Unformatted
# Lorem ipsum dolor these are notes on the fall of the roman empire that are relevant to this chapter there are lots of words here
# and these words are important to my understanding of the text.
# ```
# [Sally walked the dog down the stree menacingly, in the way only a child with a large dog knows how to do with her head
# swivelling back and forth. The back and forths weren't those from a person looking for threats. They were the head-held-high
# actions of a laser targeting system.]
# ```
#
# \par Formatted:
# ```
# Sally walked the dog down the stree menacingly, in the way only a child with a large dog knows how to do with her head
# swivelling back and forth. The back and forths weren't those from a person looking for threats. They were the head-held-high
# actions of a laser targeting system.
# ```
# \par
# If you edit the formatted text, it should be able to know where it belongs in the unformated version and vice-versa.
# That way if I want to focus only on writing the final text, I can do that and it will automatically fit itself into
# my notes. If I want to work in a more free-form planning manner, I can dod that too.
# \par
# At a later stage, It would be nice if I could automatically integrate noun detection of some sort, so I could
# automatically link things to their description. That way if I get lost while writing, I could click on a person or a
# place name and see things about them.
#
# # Analytic Tools
# - Track total word count
# - Track time-series data on time worked, words per minute, day, etc.
# - Track those separately for the formatted and unformatted text
# - Be able to plot the analytics in real time and just in general. That way I can see how my words per minute, day, week,
# etc change over time.
# - Be able to track word usage with one of those word clouds
# - Be able to track sentence composition (simple vs complex)
#
# I want the window to display multiple documents at a time using markdown so they can be formatted

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import math
import keyboard
from tkinter.filedialog import askopenfilename, asksaveasfilename



import os
import time

class Book:

    basePath = 'book'

    knownDocumentPaths = ['unstructured','world','characters','universeOutline','partOutline','chapterOutline','book']
    otherDocumentPaths = []
    allPaths = []

    allString = ""

    docTree = {}

    def __init__(self):

        for (a,b,file) in os.walk('./book'):
            self.allPaths = file
        self.loadDocTree()

        print("Total Chars Slow: ", self.getTotalWordsExpensive()[0])
        print("Total Words Slow: ", self.getTotalWordsExpensive()[1])
        #self.saveAll()


    def loadAllString(self):
        self.allString = ""
        for doc in self.allPaths:
            with open(os.path.join(self.basePath, doc), 'r') as doc:
                for line in doc:
                    self.allString = self.allString + line
            self.allString = self.allString + "\n"

        return self.allString

    def loadDocTree(self):
        # Document A
        #  Section A
        #    Unstructured Part A
        #    Structured Part A
        #    Unstructured Part B
        #    Structured Part B
        #  Section B
        #    ...
        # Document B
        #  ...
        self.docTree = {}
        for doc in self.allPaths:
            docList = []
            currentSection = ""
            with open(os.path.join(self.basePath, doc), 'r') as doc:
                for line in doc:
                    if line.startswith("##"):
                        if not currentSection == '':
                            docList.append(currentSection)
                        currentSection = line
                    else:
                        currentSection = currentSection + line
                docList.append(currentSection)
            self.docTree[doc.name.split('\\')[1]] = docList.copy()
        return self.docTree


    def saveDoc(self,docName):
        with open(os.path.join(self.basePath, docName), 'w') as doc:
            for section in self.docTree[docName]:
                doc.writelines(section)

    def saveAll(self):
        for docName in self.allPaths:
            self.saveDoc(docName)

    def getTotalWordsExpensive(self):
        totalWords = 0
        totalChars = 0
        for k in self.docTree:
            for section in self.docTree[k]:
                totalWords += len(section.split())
                totalChars += len(section)
        return (totalChars, totalWords)

    def setSection(self,doc,section,text):
        self.docTree[doc][section] = text

    def addChar(self, doc, section, idx, text):
        self.docTree[doc][section] = self.docTree[doc][section][:idx] + text + self.docTree[doc][section][idx:]

    def rmChar(self, doc, section, idx):
        self.docTree[doc][section] = self.docTree[doc][section][:idx] + self.docTree[doc][section][idx+1:]


class Telemetry:
    tmPath = "telem"
    words = []
    times = []

    def __init__(self,book):
        self.bk = book
        with open('rawSessionTm.csv', 'a+') as rawSesTmFile:
            rawSesTmFile.write('\n')

    def update(self):
        totalWords = self.bk.getTotalWordsExpensive()
        t = time.time()
        with open('rawSessionTm.csv','a+') as rawSesTmFile:
            rawSesTmFile.write(str(t) + ',' + str(totalWords[0]) + ',' + str(totalWords[1]) + ';')
        self.words.append(totalWords[0])
        self.times.append(t)

    def plot(self,plot,canvas):
        if(len(self.words) < 1000):

            return
        deltaTimes = []
        deltaWords = []
        wpts = []
        for ids in range(len(self.times) - 1):
            deltaTimes.append(self.times[ids + 1] - self.times[ids])
            deltaWords.append(self.words[ids + 1] - self.words[ids])
            wpts.append(deltaWords[ids] / deltaTimes[ids] * 60 / 5)

        N = 1000
        runMean = np.convolve(wpts, np.ones(N) / N, mode='valid')
        runMean = np.convolve(runMean, np.ones(N) / N, mode='valid')
        plot.cla()
        plot.plot(self.times[:len(runMean)], runMean)
        mdwords = np.average(wpts)
        plot.plot(self.times[:len(runMean)], [mdwords]*len(self.times[:len(runMean)]))
        ax = plt.gca()
        ax.set_ylim([0,120])
        canvas.draw()
        #plt.show(block=False)



class WritingSession:

    startTime = 0
    currentTime = 0
    prevSaveTime = 0
    saveInterval = 1.0 # 5 seconds
    tmInterval = 0.01 # 1 second

    bk = None
    tm = None

    activeIdx = ('',0,0)

    def __init__(self):
        self.startTime = time.time()
        self.currentTime = time.time()
        self.prevSaveTime = self.currentTime
        self.prevTmTime = self.currentTime
        self.bk = Book()
        self.tm = Telemetry(self.bk)

        self.plot1 = None
        self.canvas = None

    def update(self):
        self.currentTime = time.time() - self.startTime

        # Poll User Inputs

        # Update book with inputs


        if(abs(self.prevSaveTime - self.currentTime) >= self.saveInterval):
            self.prevSaveTime = self.currentTime
            self.bk.saveAll()
            self.tm.plot(self.plot1,self.canvas)

        if(abs(self.prevTmTime - self.currentTime) >= self.tmInterval):
            self.prevTmTime = self.currentTime
            self.tm.update()

    def setPlotCanv(self,plot,can):
        self.plot1 = plot
        self.canvas = can

class RichText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_font = tkFont.nametofont(self.cget("font"))

        em = default_font.measure("m")
        default_size = default_font.cget("size")
        bold_font = tkFont.Font(**default_font.configure())
        italic_font = tkFont.Font(**default_font.configure())
        h1_font = tkFont.Font(**default_font.configure())
        h2_font = tkFont.Font(**default_font.configure())
        h3_font = tkFont.Font(**default_font.configure())


        bold_italic_font = tkFont.Font(**default_font.configure())
        bold_font.configure(weight="bold")
        italic_font.configure(slant="italic")
        bold_italic_font.configure(weight="bold",slant="italic")
        h1_font.configure(size=int(default_size*2), weight="bold")
        h2_font.configure(size=int(default_size * 1.5), weight="bold")
        h3_font.configure(size=int(default_size * 1.2), weight="bold")

        self.tag_configure("bold", font=bold_font,)
        self.tag_configure("italic", font=italic_font)
        self.tag_configure("bold_italic", font=bold_italic_font)
        self.tag_configure("H1", font=h1_font, spacing3=default_size)
        self.tag_configure("H2", font=h2_font, spacing3=default_size)
        self.tag_configure("H3", font=h3_font, spacing3=default_size)
        self.tag_configure('hidden',elide=True)

        lmargin2 = em + default_font.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=em, lmargin2=lmargin2)

    def insert_bullet(self, index, text):
        self.insert(index, f"\u2022 {text}", "bullet")

    def myUpdate(self):
        pass

    def hideText(self, start, end):
        self.tag_add('hidden',start,end)

    def unhideText(self, start, end):
        self.tag_remove('hidden',start,end)

    def applyTag(self,start,end,tg):
        self.tag_add(tg, start, end)



class myEvent:
    def __init__(self,ch=''):
        self.char = ch
    def setChar(self,ch):
        self.char = ch

class Application(tk.Frame):

    ws = None
    key = 'A'
    activeDoc = -1
    boundDoc = ''
    activeWidget = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.ws = WritingSession()
        self.pack()


        self.createWidgets()
        self.bindCallbacks()

        self.key = ''

    def createWidgets(self):
        #self.now = tk.StringVar()
        #self.time = tk.Label(self, font=('Helvetica', 24))
        #self.time.pack(side="top")
        #self.time["textvariable"] = self.now

        #self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        #self.QUIT.pack(side="bottom")



        ## Setup Master
        self.master.title("Text Editor Application")

        self.masterNb = ttk.Notebook(self.master)
        self.masterNb.pack(expand=True,fill=tk.BOTH)
        self.docNb = ttk.Frame(self.masterNb)
        self.docNb.rowconfigure(0, minsize=1000, weight=1)
        self.docNb.columnconfigure(0, minsize=800, weight=1)
        self.docNb.columnconfigure(1, minsize=800, weight=1)
        self.docNb.columnconfigure(2, minsize=800, weight=1)
        self.masterNb.add(self.docNb,text='Docs')

        self.analNb = ttk.Frame(self.masterNb)
        self.fig = Figure()
        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot([0,1,2,3,4],[0,1,2,3,4])
        self.canvas = FigureCanvasTkAgg(self.fig,master=self.analNb)
        self.canvas.draw()
        self.ws.setPlotCanv(self.plot1,self.canvas)
        self.canvas.get_tk_widget().pack(expand=True,fill=tk.BOTH)

        self.masterNb.add(self.analNb, text='Analysis')


        ## Setup Tabs
        self.tabControl1 = ttk.Notebook(self.docNb)
        self.tabControl2 = ttk.Notebook(self.docNb)
        self.tabControl3 = ttk.Notebook(self.docNb)

        self.ntab1 = ttk.Frame(self.tabControl1)
        self.ntab2 = ttk.Frame(self.tabControl2)
        self.ntab3 = ttk.Frame(self.tabControl3)

        self.tab1 = ttk.Frame(self.tabControl1)
        self.tab2 = ttk.Frame(self.tabControl2)
        self.tab3 = ttk.Frame(self.tabControl3)


        self.tabControl1.add(self.tab1, text='Tab1')
        self.tabControl2.add(self.tab2, text='Tab2')
        self.tabControl3.add(self.tab3, text='Tab3')


        self.tabControl1.add(self.ntab1, text='+')
        self.tabControl2.add(self.ntab2, text='+')
        self.tabControl3.add(self.ntab3, text='+')

        self.tabControl1.grid(row=0, column=0, sticky='nsew')
        self.tabControl2.grid(row=0, column=1, sticky='nsew')
        self.tabControl3.grid(row=0, column=2, sticky='nsew')


        ## Setup Text Edit Areas
        self.text_edit1 = RichText(self.tab1, undo=True)
        self.text_edit1.pack(expand=True,fill=tk.BOTH)

        self.text_edit2 = RichText(self.tab2, undo=True)
        self.text_edit2.pack(expand=True,fill=tk.BOTH)

        self.text_edit3 = RichText(self.tab3, undo=True)
        self.text_edit3.pack(expand=True,fill=tk.BOTH)

        self.bookWidget = self.text_edit3

        # Load Documents
        self.loadDoc(self.text_edit1,'unstructured')
        self.loadDoc(self.text_edit2, 'universeOutline')
        self.loadDoc(self.text_edit3, 'book')
        # initial time display
        self.onUpdate()

    def bindCallbacks(self):
        self.master.bind('<KeyPress>', self.onKeyPress)
        self.master.bind('<BackSpace>', self.onBackSpace)
        self.master.bind('<<Paste>>', self.onPaste)

        self.tabControl1.bind("<Button-3>", self.onTabRightClick1)
        self.tabControl2.bind("<Button-3>", self.onTabRightClick2)
        self.tabControl3.bind("<Button-3>", self.onTabRightClick3)

        self.tabControl1.bind("<Button-1>",self.handleTabChanged1)
        self.tabControl2.bind("<Button-1>", self.handleTabChanged2)
        self.tabControl3.bind("<Button-1>", self.handleTabChanged3)



    def onPaste(self,event):
        print(event.__dict__)
        print("clipboard",self.master.clipboard_get())

        #self.activeWidget.edit_undo()
        for ch in self.master.clipboard_get():
            ev = myEvent(ch)
            self.onKeyPress(ev)

        #self.ws.bk.setSection(self.boundDoc, 0, self.activeWidget.get('1.0', 'end-1c'))
        #self.ws.bk.saveAll()
        #self.ws.bk.loadDocTree()
        #for doc in self.ws.bk.allPaths:
        #    print(doc)
        #    self.loadDoc(self.bookWidget, doc)
    def onTabRightClick1(self,event):
        clicked_tab = self.tabControl1.tk.call(self.tabControl1._w, "identify", "tab", event.x, event.y)

        if not clicked_tab == self.tabControl1.index(self.tabControl1.tabs()[-1]):
            self.tabControl1.forget(clicked_tab)

    def onTabRightClick2(self,event):
        clicked_tab = self.tabControl2.tk.call(self.tabControl2._w, "identify", "tab", event.x, event.y)

        if not clicked_tab == self.tabControl2.index(self.tabControl2.tabs()[-1]):
            self.tabControl2.forget(clicked_tab)

    def onTabRightClick3(self,event):
        clicked_tab = self.tabControl3.tk.call(self.tabControl3._w, "identify", "tab", event.x, event.y)

        if not clicked_tab == self.tabControl3.index(self.tabControl3.tabs()[-1]):
            self.tabControl3.forget(clicked_tab)



    def handleTabChanged1(self,event):
        clicked_tab = self.tabControl1.tk.call(self.tabControl1._w, "identify", "tab", event.x, event.y)

        if clicked_tab == self.tabControl1.index(self.tabControl1.tabs()[-1]):
            index = clicked_tab
            frame = tk.Frame(self.tabControl1)
            self.tabControl1.insert(index, frame, text="<untitled" + str(index) + ">")
            self.tabControl1.select(index)

    def handleTabChanged2(self,event):
        clicked_tab = self.tabControl2.tk.call(self.tabControl2._w, "identify", "tab", event.x, event.y)

        if clicked_tab == self.tabControl2.index(self.tabControl2.tabs()[-1]):
            index = clicked_tab
            frame = tk.Frame(self.tabControl2)
            self.tabControl2.insert(index, frame, text="<untitled" + str(index) + ">")
            self.tabControl2.select(index)

    def handleTabChanged3(self,event):
        clicked_tab = self.tabControl3.tk.call(self.tabControl3._w, "identify", "tab", event.x, event.y)

        if clicked_tab == self.tabControl3.index(self.tabControl3.tabs()[-1]):
            index = clicked_tab
            frame = tk.Frame(self.tabControl3)
            self.tabControl3.insert(index, frame, text="<untitled" + str(index) + ">")
            self.tabControl3.select(index)

    def loadDoc(self,txt_wgt, docName):
        txt_wgt.delete('1.0','end-1c')
        procSection = []
        for section in self.ws.bk.docTree[docName]:
            tagSplit = section.split('<')
            cpTagSplit = tagSplit.copy()
            countTag = 0
            for tidx in range(len(tagSplit)):
                splitTagSplit = tagSplit[tidx].split('>')
                if len(splitTagSplit) > 1:
                    cpTagSplit[tidx + countTag] = splitTagSplit[0]
                    cpTagSplit.insert(tidx + 1 + countTag, splitTagSplit[1])
                    countTag = countTag + 1

            tagSplit = cpTagSplit.copy()
            for taggedSection in tagSplit:
                if '@' in taggedSection:
                    splitTaggedSection = taggedSection.split("@")
                    procSection.append('<'+splitTaggedSection[0]+'@')
                    procSection.append(splitTaggedSection[1])
                    procSection.append('>')
                    txt_wgt.insert(tk.INSERT, '<'+splitTaggedSection[0]+'@', 'hidden')
                    if ']' in splitTaggedSection[1] and docName == 'book': # TODO This is where I would add the logic to add tags to link back to the original section. Or tags to link back to proper nouns.
                        splitBookTags  = splitTaggedSection[1].split(']')
                        for glomp in splitBookTags:
                            txt_wgt.insert(tk.INSERT, glomp, splitTaggedSection[0].strip())
                            txt_wgt.insert(tk.INSERT, ']', 'hidden')
                    else:
                        txt_wgt.insert(tk.INSERT, splitTaggedSection[1], splitTaggedSection[0].strip())
                    txt_wgt.insert(tk.INSERT, '>', 'hidden')
                else:
                    procSection.append('<@')
                    procSection.append(taggedSection)
                    procSection.append('>')
                    if ']' in taggedSection and docName == 'book':
                        splitBookTags  = taggedSection.split(']')
                        for glomp in splitBookTags:
                            txt_wgt.insert(tk.INSERT, glomp, [])
                            txt_wgt.insert(tk.INSERT, ']', 'hidden')
                    else:
                        txt_wgt.insert(tk.INSERT, taggedSection, [])
    def onUpdate(self):
        if(self.focus_get() == self.text_edit1):
            self.activeDoc = 0
            self.boundDoc = 'unstructured'
            self.activeWidget = self.text_edit1
        elif(self.focus_get() == self.text_edit2):
            self.activeDoc = 1
            self.boundDoc = 'universeOutline'
            self.activeWidget = self.text_edit2
        elif(self.focus_get() == self.text_edit3):
            self.activeDoc = 2
            self.boundDoc = 'book'
            self.activeWidget = self.text_edit3
        else:
            self.activeDoc = -1
            self.boundDoc = ''

        self.ws.update()


    def onKeyPress(self,event):
        self.ws.bk.setSection(self.boundDoc,0,self.activeWidget.get('1.0','end-1c'))

        if event.char == '>':
            stringIdx = self.activeWidget.index(tk.INSERT)

            numCharConsumed = 0

            relText = self.activeWidget.get('1.0', stringIdx)
            #' <bold@ Prologue>'
            splitText = relText.split('>')
            numCharConsumed = numCharConsumed + len(splitText) -1
            #' <bold@ Prologue',''
            splitText = splitText[-2].split('<')
            numCharConsumed = numCharConsumed + len(splitText) - 1
            # ' ','bold@ Prologue'
            hideText = splitText[1]


            #'bold@ Prologue'
            splitHideText = hideText.split('@')
            numCharConsumed = numCharConsumed + len(splitText) - 1
            numHideConsumed = numCharConsumed
            # 'bold',' Prologue'


            if len(splitText) > 1:
                numText = len(splitHideText[0]) + len(splitHideText[1]) + 3
                # 'bold@ Prologue' -> 14 + 2 = 16 (2 is the number of chars consumed in splits)
                numAtText = len(splitHideText[0]) + 2
                # 'bold' -> 4 + 3 = 7 (3 is the number of chars consumed in splits
                self.activeWidget.hideText(stringIdx + '- 1c', stringIdx)
                # ' <bold@ Prologue>'
                self.activeWidget.hideText(stringIdx + '- %dc' % (numText), stringIdx + '- %dc' % (numText-numAtText))
                self.activeWidget.applyTag(stringIdx + '- %dc' %  (numText-numAtText),stringIdx+ '- 1c',splitHideText[0])


        if event.char == ']':
            stringIdx = self.activeWidget.index(tk.INSERT)

            numCharConsumed = 0

            relText = self.activeWidget.get('1.0', stringIdx)

            #' <bold@ Prologue>'
            splitText = relText.split(']')
            countBookSects = len(splitText) -2 # Num of ']'

            numCharConsumed = numCharConsumed + len(splitText) -1
            #' <bold@ Prologue',''
            splitText = splitText[-2].split('[')
            numCharConsumed = numCharConsumed + len(splitText) - 1
            # ' ','bold@ Prologue'
            hideText = splitText[1]


            #'bold@ Prologue'
            splitHideText = hideText.split('|')
            numCharConsumed = numCharConsumed + len(splitText) - 1
            numHideConsumed = numCharConsumed
            # 'bold',' Prologue'


            if len(splitText) > 1:
                numText = len(splitHideText[0]) + len(splitHideText[1]) + 3
                # 'bold@ Prologue' -> 14 + 2 = 16 (2 is the number of chars consumed in splits)
                numAtText = len(splitHideText[0]) + 2
                # 'bold' -> 4 + 3 = 7 (3 is the number of chars consumed in splits
                #self.activeWidget.hideText(stringIdx + '- 1c', stringIdx)
                # ' <bold@ Prologue>'
                #self.activeWidget.hideText(stringIdx + '- %dc' % (numText), stringIdx + '- %dc' % (numText-numAtText))
                #self.activeWidget.applyTag(stringIdx + '- %dc' %  (numText-numAtText),stringIdx+ '- 1c',splitHideText[0])
                targets = splitHideText[0].split(',')

                for target in targets:
                    sect = self.activeWidget.get(stringIdx + '- %dc' %  (numText-numAtText),stringIdx+ '- 1c')

                    splitBook = self.ws.bk.docTree[target][0].split(']')

                    sumStr = ''
                    for spl in range(len(splitBook)):
                        if spl == countBookSects:
                            sumStr = sumStr + sect + ']'
                        elif not splitBook[spl] == '':
                            sumStr = sumStr + splitBook[spl] + ']'

                    self.ws.bk.setSection(target,0,sumStr)
                    self.ws.bk.saveAll()
                    self.ws.bk.loadDocTree()
                    self.loadDoc(self.bookWidget,target)

    def onBackSpace(self,event):
        self.ws.bk.setSection(self.boundDoc, 0, self.activeWidget.get('1.0', 'end-1c'))

        stringIdx = self.activeWidget.index(tk.INSERT)
        self.activeWidget.edit_undo()
        chair = self.activeWidget.get(stringIdx+' - 0c', stringIdx+' + 1c')
        self.activeWidget.edit_redo()

        if chair == '>':
            # Search backwards and find the beginning of the tag index so we can unhide it
            relText = self.activeWidget.get('1.0', stringIdx)
            splitText = relText.split('>')
            if len(splitText) > 1:
                splitText = splitText[-1].split('<')
            else:
                splitText = relText.split('<')

            if len(splitText) > 1:
                numText = len(splitText[-1]) + 1
                self.activeWidget.unhideText(stringIdx + '- %dc' %(numText),stringIdx)
        '''  
        if chair == ']':
            # Search backwards and find the beginning of the tag index so we can unhide it
            relText = self.activeWidget.get('1.0', stringIdx)
            splitText = relText.split(']')
            if len(splitText) > 1:
                splitText = splitText[-1].split('[')
            else:
                splitText = relText.split('[')

            if len(splitText) > 1:
                numText = len(splitText[-1]) + 1
                self.activeWidget.unhideText(stringIdx + '- %dc' %(numText),stringIdx)
        '''


# TODO: Add labels to documents to make it easy to identify them (see TODO for interactive tabs)
# TODO: ****Add start/stop/pause buttons to control whether to record telemetry
# DONETODO: Add formatting to text box? https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter
# DONETODO: Add system for parsing out what is part of the book and what isn't -> make the system work both ways (maybe need intermediary document which tracks the links between each document?). Possibly tags to identify where to put things
# TODO: Make the book parsing work in reverse
# TODO: Add a navigator for seeing the sections of the book that lets you jump to each 'section' (indicated by the ##)
    #TODO: Prerequisite fix this so it properly supports multiple sections instead of assuming section 0
# TODO: ***Add timer to ui
# TODO: ***Add total word count and session word counnt to UI
# TODO: Add scroll bars to text boxes
# TODO: Automatic interactive hyperlinks to proper nouns would be cool https://stackoverflow.com/questions/72407200/tkinter-text-that-executes-functions-on-click-highlights-when-cursor-hovers
# 1. Set up definitions in documents (with tags I define or something like <definition> <\definition>)
# 2. Could also use to link to character sheets or location sheets (not really definitions) would need some way to establish them as keywords (tags?)
# 3. Search text for those words and apply formatting change to underline them or something
# 4. Detect mouse hover over those words and open tool-tip with description
# 5. On click, scroll to the definition
# TODO: Word cloud, word usage statistics
# 1. List of most common words
# 2. Word usage breakdown by runtime of book
# 3. Sentence complexity
# 4. Reading level breakdown by runtime of book
# 5. Reading level over whole book
# DONETODO: embed plots in gui https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
# TODO: Make interface dynamic -> can load and unload documents to each pane, maybe change number of panes? https://www.geeksforgeeks.org/creating-tabbed-widget-with-python-tkinter/
# TODO: *Make a word goal and burndown chart for the year
# TODO: *Make a time spent chart for the year
# TODO: *Make an average wpm/session chart over the year
# TODO: Docking and undocking the plotting tabs
if __name__ == '__main__':





    root = tk.Tk()
    app = Application(master=root)
    running = True
    while running:
        root.update()
        root.update_idletasks()

        try:
            root.winfo_exists()
        except:
            running = False
            app.ws.bk.saveAll()

        if(running):
            app.onUpdate()




# <GPLv3_Footer>
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      Copyright (c) 2024 Nathan Ulmer.
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# <\GPLv3_Footer>