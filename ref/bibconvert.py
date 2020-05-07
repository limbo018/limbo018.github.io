# -*- coding: utf-8 -*-

#########################################################################
# File Name: bibconvert.py
# Author: Yibo Lin
# mail: yibolin@utexas.edu
# Created Time: Fri Dec  9 12:00:28 2016
#########################################################################
#!/bin/python

import sys
import re
import datetime
import bibtexparser 
import pdb

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

def getDatetime(entry):
    date = entry['year']
    timeFormat = "%Y"
    if 'month' in entry and entry['month']:
        date = date+","+entry['month']
    else:
        date = date+","+'December'
    timeFormat = "%Y,%B"
    if 'day' in entry and entry['day']:
        date = date+","+entry['day'].split('-', 1)[0]
        timeFormat = "%Y,%B,%d"
    return datetime.datetime.strptime(date, timeFormat)

def getAddressAndDate(entry):
    addressAndDate = ""
    prefix = ""
    if 'address' in entry and entry['address']:
        addressAndDate += prefix + entry['address']
        prefix = ", "
    if 'month' in entry and entry['month']:
        addressAndDate += prefix + datetime.datetime.strptime(entry['month'], "%B").strftime("%b")
        prefix = " " if 'day' in entry and entry['day'] else ", "
    if 'day' in entry and entry['day']:
        addressAndDate += prefix + entry['day'].replace("--", "-")
        prefix = ", "
    if 'year' in entry and entry['year']:
        addressAndDate += prefix + entry['year']
    return addressAndDate

# switch from [last name, first name] to [first name last name]
def switchToFirstLastNameStyle(author):
    authorArray = author.split('and')
    for i, oneAuthor in enumerate(authorArray):
        if ',' in oneAuthor:
            nameArray = oneAuthor.split(',')
            assert len(nameArray) == 2, "len(nameArray) = %d" % len(nameArray)
            authorArray[i] = nameArray[1].strip() + ' ' + nameArray[0].strip()
        if i == 0:
            author = authorArray[i]
        elif i+1 < len(authorArray):
            author += ", " + authorArray[i]
        else:
            author += " and " + authorArray[i]
    return author

def printBibDB(bibDB, highlightAuthors, suffix, header):
    # differentiate journal and conference 
    # I assume journal uses 'journal' 
    # conference uses 'booktitle'
    bookEntries = []
    journalEntries = []
    conferenceEntries = []
    thesisEntries = []

    for entry in bibDB.entries:
        if 'editor' in entry and 'publisher' in entry:
            bookEntries.append(entry)
        elif 'journal' in entry:
            journalEntries.append(entry)
        elif entry['ENTRYTYPE'].lower() == 'phdthesis':
            thesisEntries.append(entry)
        else:
            conferenceEntries.append(entry)
    # sort by years from large to small 
    journalEntries.sort(key=lambda entry: getDatetime(entry), reverse=True)
    conferenceEntries.sort(key=lambda entry: getDatetime(entry), reverse=True)
    thesisEntries.sort(key=lambda entry: getDatetime(entry), reverse=True)
    stringMap = dict(bibDB.strings)

    # call kernel print functions 
    if header:
        print(header)
    if suffix.lower() == 'web':
        print("""
= Publications

""")
        printJemdoc(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printJemdoc(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printJemdoc(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
        printJemdoc(bibDB, stringMap, highlightAuthors, thesisEntries, 'phdthesis', 'booktitle')
    elif suffix.lower() == 'jekyll':
        print("""---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

<br>

""")
        printJekyll(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printJekyll(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printJekyll(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
        printJekyll(bibDB, stringMap, highlightAuthors, thesisEntries, 'phdthesis', 'booktitle')
    elif suffix.lower() == 'cv':
        print("""\\begin{rSection}{Publications}

""")
        printCV(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printCV(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printCV(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
        print("""
\end{rSection}

""")
    elif suffix.lower() == 'cv_cn': 
        print("""\\begin{rSection}{出版物}

""")
        printCVCN(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printCVCN(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printCVCN(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
        print("""
\end{rSection}

""")
    elif suffix.lower() == 'cvjekyll':
        print("""
{% include base_path %}
""")
        printCVJekyll(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printCVJekyll(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printCVJekyll(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
    elif suffix.lower() == 'shortref': 
        printShortRef(bibDB, stringMap, highlightAuthors, bookEntries, 'book', 'booktitle')
        printShortRef(bibDB, stringMap, highlightAuthors, journalEntries, 'journal', 'journal')
        printShortRef(bibDB, stringMap, highlightAuthors, conferenceEntries, 'conference', 'booktitle')
        printShortRef(bibDB, stringMap, highlightAuthors, thesisEntries, 'phdthesis', 'booktitle')
    else:
        assert 0, "unknown suffix = %s" % suffix

def printJemdoc(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        print("=== Book Chapters\n")
        prefix = "B"
    elif publishType == 'journal':
        print("=== Journal Papers\n")
        prefix = "J"
    elif publishType == 'phdthesis': 
        print("=== PhD Thesis\n")
        prefix = ""
    else:
        print("=== Conference Papers\n")
        prefix = "C"
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
            print("==== %s\n" % (currentYear))
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "*"+highlightAuthor+"*")
        title = entry['title'].replace("/", "\\/").replace("{", "").replace("}", "")
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "[" + publishlink + " " + title +"]"
        addressAndDate = getAddressAndDate(entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
- \[%s%d\] %s, 
  "%s", 
  %s, %s, %s, edited by %s. 
  %s
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        else:
            print("""
- \[%s%d\] %s, 
  "%s", 
  %s, %s. 
  %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

def printJekyll(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        print("Book Chapters\n======\n")
        prefix = "B"
    elif publishType == 'journal':
        print("Journal Papers\n======\n")
        prefix = "J"
    elif publishType == 'phdthesis':
        print("PhD Thesis\n======\n")
        prefix = ""
    else:
        print("Conference Papers\n======\n")
        prefix = "C"
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
            print("* %s\n" % (currentYear))
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "**"+highlightAuthor+"**")
        title = entry['title'].replace("{", "").replace("}", "")
        htmltitle = title
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        # change delimiter
        annotate = annotate.replace(")(", " \\| ").replace("(", "").replace(")", "")
        # change link syntax 
        annotateLinks = re.findall('\[([^\]]*)\]', annotate)
        for annotateLink in annotateLinks: 
            tokens = annotateLink.strip().split()
            link = tokens[0]
            link = link.replace("limbo018.github.io", "/publications")
            content = tokens[1]
            annotate = annotate.replace("["+annotateLink+"]", "<a href=\"%s\" style=\"color:#3793ae\">%s</a>" % (link, content))
        if annotate: 
            annotate = """
     * %s""" % (annotate)
        if publishlink: # create link if publishlink is set 
            htmltitle = "<a href=\"%s\" style=\"color:#3793ae\">%s</a>" % (publishlink, title) # not used
            title = "[" + title + "](" + publishlink + ")"
        addressAndDate = getAddressAndDate(entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s, %s.
     * Edited by %s. 
            """ % (prefix, count, title, annotate, author, booktitle, publisher, addressAndDate, editor))
        else:
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s.
            """ % (prefix, count, title, annotate, author, booktitle, addressAndDate))
        count = count-1

def printCVJekyll(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        print("**Book Chapters**\n\n")
        prefix = "B"
    elif publishType == 'journal':
        print("**Journal Papers**\n\n")
        prefix = "J"
    else:
        print("**Conference Papers**\n\n")
        prefix = "C"
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "**"+highlightAuthor+"**")
        title = entry['title'].replace("{", "").replace("}", "")
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        # change link syntax 
        annotateLinks = re.findall('\[([^\]]*)\]', annotate)
        for annotateLink in annotateLinks: 
            tokens = annotateLink.strip().split()
            link = tokens[0]
            link = link.replace("limbo018.github.io", "/publications")
            content = tokens[1]
            annotate = annotate.replace("["+annotateLink+"]", "["+content+"]("+link+")"+"{: .share-button-noborder}")
        if publishlink: # create link if publishlink is set 
            title = "[" + title + "](" + publishlink + ")"
        addressAndDate = getAddressAndDate(entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""\
* %s%d. %s, "%s," %s, %s, %s, edited by %s. %s
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        else:
            print("""\
* %s%d. %s, "%s," %s, %s. %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

def printCV(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        print("""
\\textbf{Book Chapters}
        """)
        prefix = "B"
    elif publishType == 'journal':
        print("""
\\textbf{Journal Papers}
        """)
        prefix = "J"
    else:
        print("""
\\textbf{Conference Papers}
        """)
        prefix = "C"
    print("""
\\begin{description}[font=\\normalfont]
%{{{
    """)

    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "\\textbf{"+highlightAuthor+"}")
        title = entry['title']
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotatecv'] if 'annotatecv' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "\\href{" + publishlink + "}{" + title +"}"
        addressAndDate = getAddressAndDate(entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s, edited by %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        else:
            print("""
\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

    print("""
%}}}
\end{description}
    """)

def printCVCN(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        print("""
\\textbf{书籍章节}
        """)
        prefix = "B"
    elif publishType == 'journal':
        print("""
\\textbf{期刊论文}
        """)
        prefix = "J"
    else:
        print("""
\\textbf{会议论文}
        """)
        prefix = "C"
    print("""
\\begin{description}[font=\\normalfont]
%{{{
    """)

    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "\\textbf{"+highlightAuthor+"}")
        title = entry['title']
        booktitle = stringMap[entry[booktitleKey]] if entry[booktitleKey] in stringMap else entry[booktitleKey]
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotatecv'] if 'annotatecv' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "\\href{" + publishlink + "}{" + title +"}"
        addressAndDate = getAddressAndDate(entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s, edited by %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        else:
            print("""
\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

    print("""
%}}}
\end{description}
    """)

def printShortRef(bibDB, stringMap, highlightAuthors, entries, publishType, booktitleKey):
    prefix = ""
    if publishType == 'book':
        prefix = "B"
    elif publishType == 'journal':
        prefix = "J"
    elif publishType == 'phdthesis':
        prefix = ""
    else:
        prefix = "C"

    # print 
    count = len(entries)
    for i, entry in enumerate(entries):
        print("\\DefMacro{%s}{%s%d}" % (entry['ID'], prefix, count))
        count = count-1

def printHelp():
    print("""
usage: python bibconvert.py --suffix suffix --highlight author1 [--highlight author2] --input 1.bib [--input 2.bib]
suffix can be 'web' or 'cv'
    'web': jemdoc format for personal webpage 
    'cv': latex format for resume 
""")

if __name__ == "__main__":
    suffix = None
    highlightAuthors = []
    filenames = []
    header = ""

    if len(sys.argv) < 3 or sys.argv[1] in ('--help', '-h'):
        printHelp()
        raise SystemExit
    for i in range(1, len(sys.argv), 2):
        if sys.argv[i] == '--suffix':
            if suffix:
                raise RuntimeError("only one suffix can be accepted")
            suffix = sys.argv[i+1]
        elif sys.argv[i] == '--highlight':
            highlightAuthors.append(sys.argv[i+1])
        elif sys.argv[i] == '--input':
            filenames.append(sys.argv[i+1])
        elif sys.argv[i] == '--header':
            with open(sys.argv[i+1]) as headerFile:
                header = headerFile.read()
        else:
            break

    bibDB = read(filenames, "%")
    #print(bibDB.strings)
    #print(bibDB.entries)
    
    # write 
    printBibDB(bibDB, highlightAuthors, suffix, header)
