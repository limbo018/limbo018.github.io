#########################################################################
# File Name: bibconvert.py
# Author: Yibo Lin
# mail: yibolin@utexas.edu
# Created Time: Fri Dec  9 12:00:28 2016
#########################################################################
#!/bin/python

import sys
import re
import bibtexparser 

def read(filenames, commentPrefix):
    # read content from bibtex files 
    content = ""
    for filename in filenames:
        with open(filename) as inFile:
            for line in inFile:
                # remove comments 
                # it is not perfect now, since I cannot merge them 
                line = re.sub(re.compile("[ \t]"+commentPrefix+".*?$"), "", line)
                line = re.sub(re.compile("^"+commentPrefix+".*?$"), "", line)
                content = content+line+"\n"

    bibDB = bibtexparser.loads(content)
    return bibDB

def printBibDB(bibDB, highlightAuthors, suffix):
    # differentiate journal and conference 
    # I assume journal uses 'journal' 
    # conference uses 'booktitle'
    journalEntries = []
    conferenceEntries = []

    for entry in bibDB.entries:
        if 'journal' in entry:
            journalEntries.append(entry)
        else:
            conferenceEntries.append(entry)
    # sort by years from large to small 
    journalEntries.sort(key=lambda entry: entry['year'], reverse=True)
    conferenceEntries.sort(key=lambda entry: entry['year'], reverse=True)
    stringMap = dict(bibDB.strings)

    # call kernel print functions 
    if suffix.lower() == 'web':
        print """
# jemdoc: menu{MENU}{publications.html}
# jemdoc: addcss{yibolin_homepage/jemdoc.css}
# jemdoc: title{Yibo Lin's Homepage}

= Publications

"""
        printWeb(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printWeb(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
    elif suffix.lower() == 'cv':
        print """
\\begin{rSection}{Publications}

"""
        printCV(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printCV(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
    else:
        assert 0, "unknown suffix = %s" % suffix

def printWeb(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'journal':
        print "=== Journal Papers\n"
        prefix = "J"
    else:
        print "=== Conference Papers\n"
        prefix = "C"
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
            print "==== %s\n" % (currentYear)
        author = entry['author']
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author.replace(highlightAuthor, "*"+highlightAuthor+"*")
        title = entry['title'].replace("{", "").replace("}", "")
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "[" + publishlink + " " + title +"]"
        print """
- \[%s%d\] %s, 
  "%s", 
  %s, %s. 
  %s
        """ % (prefix, count, author, title, booktitle, currentYear, annotate)
        count = count-1

def printCV(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'journal':
        print """
\\textbf{Journal Papers}
        """
        prefix = "J"
    else:
        print """
\\textbf{Conference Papers}
        """
        prefix = "C"
    print """
\\begin{description}[font=\\normalfont]
%{{{
    """

    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        author = entry['author']
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author.replace(highlightAuthor, "\\textbf{"+highlightAuthor+"}")
        title = entry['title']
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotatecv'] if 'annotatecv' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "\\href{" + publishlink + "}{" + title +"}"
        print """
\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
        """ % (prefix, count, author, title, booktitle, currentYear, annotate)
        count = count-1

    print """
%}}}
\end{description}
    """
    print """
\end{rSection}

"""

if __name__ == "__main__":
    filenames = []
    suffix = None
    if len(sys.argv) > 1:
        suffix = sys.argv[1]
        filenames = [sys.argv[i] for i in range(2, len(sys.argv))]
    else:
        print "usage: python bibconvert.py suffix 1.bib [2.bib [3.bib]...]"

    bibDB = read(filenames, "%")
    #print(bibDB.strings)
    #print(bibDB.entries)
    
    # write 
    printBibDB(bibDB, "", suffix)
