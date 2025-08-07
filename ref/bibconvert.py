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
import bisect
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

def getBooktitle(stringMap, publishType, entry): 
    booktitleKeyMap = {'book' : 'booktitle', 'journal' : 'journal', 'conference' : 'booktitle', 'patent' : 'publisher', 'phdthesis' : 'booktitle'}
    if publishType == 'conference_journal':
        if 'journal' in entry: # journal, must be consistent to the function printBibDB 
            booktitle = entry[booktitleKeyMap['journal']]
        else: # conference 
            booktitle = entry[booktitleKeyMap['conference']]
    else: 
        booktitle = entry[booktitleKeyMap[publishType]]

    booktitle = stringMap[booktitle] if booktitle in stringMap else booktitle 
    return booktitle 

def getPrefix(publishType, entry): 
    if publishType == 'book':
        prefix = "B"
    elif publishType == 'journal':
        prefix = "J"
    elif publishType == 'phdthesis': 
        prefix = ""
    elif publishType == 'patent':
        prefix = "P"
    elif publishType == 'conference_journal':
        if 'journal' in entry: 
            prefix = 'J'
        else:
            prefix = 'C'
    else:
        prefix = "C"
    return prefix 


# switch from [last name, first name] to [first name last name]
def switchToFirstLastNameStyle(author, getArray=False):
    authorArray = author.split(' and ')
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
    if getArray: 
        return authorArray
    else: 
        return author

def printBibDB(bibDB, highlightAuthors, suffix, header):
    # differentiate journal and conference 
    # I assume journal uses 'journal' 
    # conference uses 'booktitle'
    bookEntries = {'UT' : [], 'PKU' : [], 'all' : []}
    journalEntries = {'UT' : [], 'PKU' : [], 'all' : []}
    conferenceEntries = {'UT' : [], 'PKU' : [], 'all' : []}
    conferenceJournalEntries = {'UT' : [], 'PKU' : [], 'all' : []}
    thesisEntries = {'UT' : [], 'PKU' : [], 'all' : []}
    patentEntries = {'UT' : [], 'PKU' : [], 'all' : []}

    for entry in bibDB.entries:
        if 'editor' in entry and 'publisher' in entry:
            bookEntries[entry['affiliation']].append(entry)
        elif 'journal' in entry:
            journalEntries[entry['affiliation']].append(entry)
        elif entry['ENTRYTYPE'].lower() == 'phdthesis':
            thesisEntries[entry['affiliation']].append(entry)
        elif entry['ENTRYTYPE'].lower() == 'misc' and 'publisher' in entry and 'patent' in entry['publisher'].lower():
            patentEntries[entry['affiliation']].append(entry)
        else:
            conferenceEntries[entry['affiliation']].append(entry)

    for affi in ['UT', 'PKU']: 
        bookEntries['all'].extend(bookEntries[affi])
        journalEntries['all'].extend(journalEntries[affi])
        conferenceEntries['all'].extend(conferenceEntries[affi])
        thesisEntries['all'].extend(thesisEntries[affi])
        patentEntries['all'].extend(patentEntries[affi])

    # sort by years from large to small 
    for affi in ['UT', 'PKU', 'all']: 
        bookEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
        journalEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
        conferenceEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
        conferenceJournalEntries[affi] = journalEntries[affi] + conferenceEntries[affi] 
        conferenceJournalEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
        thesisEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
        patentEntries[affi].sort(key=lambda entry: getDatetime(entry), reverse=True)
    stringMap = dict(bibDB.strings)

    # compute statistics 
    stats = {}
    for affi in ['UT', 'PKU', 'all']: 
        stats[affi] = {}
        dac_count = 0
        iccad_count = 0
        date_count = 0
        tcad_count = 0
        for entry in conferenceEntries[affi]: 
            dac_count += (entry['booktitle'] == stringMap['dac'])
            iccad_count += (entry['booktitle'] == stringMap['iccad'])
            date_count += (entry['booktitle'] == stringMap['date'])
        for entry in journalEntries[affi]: 
            tcad_count += (entry['journal'] == stringMap['tcad'])
        stats[affi] = {'dac' : dac_count, 'iccad' : iccad_count, 'date' : date_count, 'tcad' : tcad_count} 

    # call kernel print functions 
    if header:
        print(header)
    if suffix.lower() == 'web':
        print("""
= Publications

""")
        printJemdoc(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['all'], 'conference_journal')
        #printJemdoc(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference')
        #printJemdoc(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal')
        printJemdoc(bibDB, stringMap, highlightAuthors, bookEntries['all'], 'book')
        printJemdoc(bibDB, stringMap, highlightAuthors, thesisEntries['all'], 'phdthesis')
        #printJemdoc(bibDB, stringMap, highlightAuthors, patentEntries['all'], 'patent')
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
        printJekyll(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['all'], 'conference_journal')
        #printJekyll(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference')
        #printJekyll(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal')
        printJekyll(bibDB, stringMap, highlightAuthors, bookEntries['all'], 'book')
        printJekyll(bibDB, stringMap, highlightAuthors, thesisEntries['all'], 'phdthesis')
        #printJekyll(bibDB, stringMap, highlightAuthors, patentEntries['all'], 'patent')
    elif suffix.lower() == 'cv':
        print("""\\begin{rSection}{Publications}
""")
        printCV(bibDB, stringMap, highlightAuthors, bookEntries['PKU'], 'book', len(bookEntries['UT']))
        printCV(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['PKU'], 'conference_journal', len(conferenceJournalEntries['UT']), stats['PKU'])
        # printCV(bibDB, stringMap, highlightAuthors, patentEntries['PKU'], 'patent', 0)
        print("""
\\begin{description}[font=\\normalfont, rightmargin=2em]
    \item \\textbf{========== Below are publications during Ph.D. and Postdoc ==========}
\\end{description}
        """)
        printCV(bibDB, stringMap, highlightAuthors, bookEntries['UT'], 'book', 0)
        printCV(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['UT'], 'conference_journal', 0, stats['UT'])
        #printCV(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal', 0)
        #printCV(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference', 0)
        print("""
\\end{rSection}

""")
    elif suffix.lower() == 'cv_cn': 
        print("""\\begin{rSection}{发明专利列表}

""")
        printCVCN(bibDB, stringMap, highlightAuthors, patentEntries['PKU'], 'patent', 0)
        print("""
\\end{rSection}

""")
        print("""\\begin{rSection}{著作及论文列表}

""")
        printCVCN(bibDB, stringMap, highlightAuthors, bookEntries['PKU'], 'book', len(bookEntries['UT']))
        printCVCN(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['PKU'], 'conference_journal', len(conferenceJournalEntries['UT']), stats['PKU'])
        print("""
\\begin{description}[font=\\normalfont, rightmargin=2em]
%{{{
    \item \\textbf{================ 以下为博士及博士后期间发表内容 ================}
%}}}
\\end{description}
        """)
        printCVCN(bibDB, stringMap, highlightAuthors, bookEntries['UT'], 'book', 0)
        printCVCN(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['UT'], 'conference_journal', 0, stats['UT'])
        #printCVCN(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal', 0)
        #printCVCN(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference', 0)
        print("""
\\end{rSection}

""")
    elif suffix.lower() == 'cvjekyll':
        print("""
{% include base_path %}
""")
        printCVJekyll(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['all'], 'conference_journal')
        #printCVJekyll(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference')
        #printCVJekyll(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal')
        printCVJekyll(bibDB, stringMap, highlightAuthors, bookEntries['all'], 'book')
        #printCVJekyll(bibDB, stringMap, highlightAuthors, patentEntries['all'], 'patent')
    elif suffix.lower() == 'shortref': 
        printShortRef(bibDB, stringMap, highlightAuthors, conferenceJournalEntries['all'], 'conference_journal')
        #printShortRef(bibDB, stringMap, highlightAuthors, conferenceEntries['all'], 'conference')
        #printShortRef(bibDB, stringMap, highlightAuthors, journalEntries['all'], 'journal')
        printShortRef(bibDB, stringMap, highlightAuthors, bookEntries['all'], 'book')
        printShortRef(bibDB, stringMap, highlightAuthors, thesisEntries['all'], 'phdthesis')
        #printShortRef(bibDB, stringMap, highlightAuthors, patentEntries['all'], 'patent')
    else:
        assert 0, "unknown suffix = %s" % suffix

def printJemdoc(bibDB, stringMap, highlightAuthors, entries, publishType):
    prefix = ""
    if publishType == 'book':
        print("=== Book Chapters\n")
    elif publishType == 'journal':
        print("=== Journal Papers\n")
    elif publishType == 'phdthesis': 
        print("=== PhD Thesis\n")
    elif publishType == 'patent':
        print("=== Patents\n")
    elif publishType == 'conference_journal':
        print("=== Conference and Journal Papers\n")
    else:
        print("=== Conference Papers\n")
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
        booktitle = getBooktitle(stringMap, publishType, entry)
        booktitle = booktitle.replace("\\", "")
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "[" + publishlink + " " + title +"]"
        addressAndDate = getAddressAndDate(entry)
        prefix = getPrefix(publishType, entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
- \\[%s%d\\] %s, 
  "%s", 
  %s, %s, %s, edited by %s. 
  %s
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        elif publishType == 'patent': 
            publisher = entry['publisher']
            number = entry['number']
            print("""
- \\[%s%d\\] %s, 
  "%s", 
  %s, %s, %s. 
  %s
            """ % (prefix, count, author.replace(" and", ","), title, publisher, number, addressAndDate, annotate))
        elif publishType == 'conference_journal': 
            print("""
- \\[%s%d\\] %s, 
  "%s", 
  %s, %s. 
  %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        else:
            print("""
- \\[%s%d\\] %s, 
  "%s", 
  %s, %s. 
  %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

def printJekyll(bibDB, stringMap, highlightAuthors, entries, publishType):
    prefix = ""
    if publishType == 'book':
        print("Book Chapters\n======\n")
    elif publishType == 'journal':
        print("Journal Papers\n======\n(\\* denotes corresponding authors)\n")
    elif publishType == 'phdthesis':
        print("PhD Thesis\n======\n")
    elif publishType == 'patent':
        print("Patents\n======\n")
    elif publishType == 'conference_journal':
        print("Conference and Journal Papers\n======\n(\\* denotes corresponding authors)\n")
    else:
        print("Conference Papers\n======\n(\\* denotes corresponding authors)\n")
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
            print("* %s\n" % (currentYear))
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if 'corresponding' in entry and entry['corresponding']: # mark corresponding authors
            correspondingAuthors = switchToFirstLastNameStyle(entry['corresponding'], getArray=True)
            for correspondingAuthor in correspondingAuthors: 
                author = author.replace(correspondingAuthor, correspondingAuthor+"\\*")
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "**"+highlightAuthor+"**")
        title = entry['title'].replace("{", "").replace("}", "")
        htmltitle = title
        booktitle = getBooktitle(stringMap, publishType, entry)
        booktitle = booktitle.replace("\\", "")
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        # change delimiter
        annotate = annotate.replace(")(", " \\| ").replace("(", "").replace(")", "")
        # change link syntax 
        annotateLinks = re.findall('\\[([^\\]]*)\\]', annotate)
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
        prefix = getPrefix(publishType, entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s, %s.
     * Edited by %s. 
            """ % (prefix, count, title, annotate, author, booktitle, publisher, addressAndDate, editor))
        elif publishType == 'patent': 
            publisher = entry['publisher']
            number = entry['number']
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s, %s.
            """ % (prefix, count, title, annotate, author.replace(" and", ","), publisher, number, addressAndDate))
        elif publishType == 'conference_journal':
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s.
            """ % (prefix, count, title, annotate, author, booktitle, addressAndDate))
        else:
            print("""\
  ### %s%d. %s %s
     * %s 
     * %s, %s.
            """ % (prefix, count, title, annotate, author, booktitle, addressAndDate))
        count = count-1

def printCVJekyll(bibDB, stringMap, highlightAuthors, entries, publishType):
    prefix = ""
    if publishType == 'book':
        print("**Book Chapters**\n\n")
    elif publishType == 'journal':
        print("**Journal Papers**\n\n(\\* denotes corresponding authors)\n\n")
    elif publishType == 'patent':
        print("**Patents**\n\n")
    elif publishType == 'conference_journal': 
        print("**Conference and Journal Papers**\n\n(\\* denotes corresponding authors)\n\n")
    else:
        print("**Conference Papers**\n\n(\\* denotes corresponding authors)\n\n")
    # print 
    currentYear = '' 
    count = len(entries)
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if 'corresponding' in entry and entry['corresponding']: # mark corresponding authors
            correspondingAuthors = switchToFirstLastNameStyle(entry['corresponding'], getArray=True)
            for correspondingAuthor in correspondingAuthors: 
                author = author.replace(correspondingAuthor, correspondingAuthor+"\\*")
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "**"+highlightAuthor+"**")
        title = entry['title'].replace("{", "").replace("}", "")
        booktitle = getBooktitle(stringMap, publishType, entry)
        booktitle = booktitle.replace("\\", "")
        address = entry['address'] if 'address' in entry else ""
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotateweb'] if 'annotateweb' in entry else ""
        # change link syntax 
        annotateLinks = re.findall('\\[([^\\]]*)\\]', annotate)
        for annotateLink in annotateLinks: 
            tokens = annotateLink.strip().split()
            link = tokens[0]
            link = link.replace("limbo018.github.io", "/publications")
            content = tokens[1]
            annotate = annotate.replace("["+annotateLink+"]", "["+content+"]("+link+")"+"{: .share-button-noborder}")
        if publishlink: # create link if publishlink is set 
            title = "[" + title + "](" + publishlink + ")"
        addressAndDate = getAddressAndDate(entry)
        prefix = getPrefix(publishType, entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""\
* %s%d. %s, "%s," %s, %s, %s, edited by %s. %s
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        elif publishType == 'patent':
            publisher = entry['publisher']
            number = entry['number']
            print("""\
* %s%d. %s, "%s," %s, %s, %s. %s
            """ % (prefix, count, author.replace(" and", ","), title, publisher, number, addressAndDate, annotate))
        elif publishType == 'conference_journal': 
            print("""\
* %s%d. %s, "%s," %s, %s. %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        else:
            print("""\
* %s%d. %s, "%s," %s, %s. %s
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

def printCV(bibDB, stringMap, highlightAuthors, entries, publishType, indexOffset, stats=None):
    prefix = ""
    if publishType == 'book':
        print("""
\\textbf{Book Chapters}
        """)
    elif publishType == 'journal':
        print("""
\\textbf{Journal Papers} (* denotes corresponding authors)
        """)
    elif publishType == 'patent':
        pass 
        # print("""
        # \\textbf{Patents}
        # """)
    elif publishType == 'conference_journal': 
        print("""
\\textbf{Conference and Journal Papers} (* denotes corresponding authors)
        """)
        if stats: 
            print("""
            \\textit{\\underline{Summary: DAC (%d), ICCAD (%d), IEEE TCAD (%d), DATE (%d), etc.}} 
    """ % (stats['dac'], stats['iccad'], stats['tcad'], stats['date']))
    else:
        print("""
\\textbf{Conference Papers} (* denotes corresponding authors)
        """)
    print("""
\\begin{description}[font=\\normalfont, rightmargin=2em]
%{{{
    """)

    # print 
    currentYear = '' 
    count = len(entries) + indexOffset
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if 'corresponding' in entry and entry['corresponding']: # mark corresponding authors
            correspondingAuthors = switchToFirstLastNameStyle(entry['corresponding'], getArray=True)
            for correspondingAuthor in correspondingAuthors: 
                author = author.replace(correspondingAuthor, correspondingAuthor+"*")
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "\\textbf{"+highlightAuthor+"}")
        title = entry['title']
        booktitle = getBooktitle(stringMap, publishType, entry)
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotatecv'] if 'annotatecv' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "\\href{" + publishlink + "}{" + title +"}"
        addressAndDate = getAddressAndDate(entry)
        prefix = getPrefix(publishType, entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s, edited by %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        elif publishType == 'patent':
            publisher = entry['publisher']
            number = entry['number']
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s.
    %s
}
            """ % (prefix, count, author.replace(" and", ","), title, publisher, number, addressAndDate, annotate))
        elif publishType == 'conference_journal':
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        else:
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

    print("""
%}}}
\\end{description}
    """)

def printCVCN(bibDB, stringMap, highlightAuthors, entries, publishType, indexOffset, stats=None):
    prefix = ""
    if publishType == 'book':
        print("""
\\textbf{书籍章节}
        """)
    elif publishType == 'journal':
        print("""
\\textbf{期刊论文} (标*表示通讯作者)
        """)
    elif publishType == 'patent':
        pass 
        # print("""
        # \\textbf{专利}
        # """)
    elif publishType == 'conference_journal': 
        print("""
\\textbf{会议及期刊论文} (标*表示通讯作者)
        """)
        if stats: 
            print("""
            \\underline{论文成果包括: DAC (%d篇), ICCAD (%d篇), IEEE TCAD (%d篇), DATE (%d篇), ...} 
    """ % (stats['dac'], stats['iccad'], stats['tcad'], stats['date']))
    else:
        print("""
\\textbf{会议论文} (标*表示通讯作者)
        """)
    print("""
\\begin{description}[font=\\normalfont, rightmargin=2em]
%{{{
    """)

    # print 
    currentYear = '' 
    count = len(entries) + indexOffset
    for i, entry in enumerate(entries):
        if not currentYear or currentYear.lower() != entry['year'].lower():
            currentYear = entry['year']
        # switch from [last name, first name] to [first name last name]
        author = switchToFirstLastNameStyle(entry['author'])
        if 'corresponding' in entry and entry['corresponding']: # mark corresponding authors
            correspondingAuthors = switchToFirstLastNameStyle(entry['corresponding'], getArray=True)
            for correspondingAuthor in correspondingAuthors: 
                author = author.replace(correspondingAuthor, correspondingAuthor+"*")
        if highlightAuthors: # highlight some authors 
            for highlightAuthor in highlightAuthors:
                author = author.replace(highlightAuthor, "\\textbf{"+highlightAuthor+"}")
        title = entry['title']
        booktitle = getBooktitle(stringMap, publishType, entry) 
        publishlink = entry['publishlink'] if 'publishlink' in entry else ""
        annotate = entry['annotatecv'] if 'annotatecv' in entry else ""
        if publishlink: # create link if publishlink is set 
            title = "\\href{" + publishlink + "}{" + title +"}"
        addressAndDate = getAddressAndDate(entry)
        prefix = getPrefix(publishType, entry)
        if publishType == 'book': 
            editor = switchToFirstLastNameStyle(entry['editor'])
            publisher = entry['publisher']
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s, edited by %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, publisher, addressAndDate, editor, annotate))
        elif publishType == 'patent':
            publisher = entry['publisher']
            number = entry['number']
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s, %s.
    %s
}
            """ % (prefix, count, author.replace(" and", ","), title, 
                   "中国专利" if publisher == 'Chinese Patent' else publisher, 
                   number, addressAndDate, annotate))
        elif publishType == 'conference_journal':
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        else:
            print("""
\\item[{[%s%d]}]{
        %s, 
    ``%s'', 
    %s, %s.
    %s
}
            """ % (prefix, count, author, title, booktitle, addressAndDate, annotate))
        count = count-1

    print("""
%}}}
\\end{description}
    """)

def printShortRef(bibDB, stringMap, highlightAuthors, entries, publishType):
    # print 
    count = len(entries)
    for i, entry in enumerate(entries):
        prefix = getPrefix(publishType, entry)
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
