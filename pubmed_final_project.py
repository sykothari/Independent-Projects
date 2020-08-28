# Query PubMed for list of publications related to keyword(s) inputted by user
# List will have the requested number of publications sorted by relevance

# Output is a bibliography of these publications

# Code

import urllib.request
import json
import ssl
import xml.etree.ElementTree as ET

# code to format the entry (bibliographic reference and abstract)

# set linelength to the desired line length
linelength = 70

def linebreak(str):
    # what we return
    retstr = ""
    # grab linelength chars and go backwards until the first blank
    # then print that
    i = 0
    nchars = len(str)
    while i < nchars:
        # if first char is a blank, skip it; it's the break
        if str[i].isspace():
            i += 1            
        j = i + linelength
        # case: less than linelength chars left
        # just print it
        if j >= nchars:
            retstr += str[i:nchars] + "\n"
            #print("%s" % (str[i:nchars]))
            break
        # j < nchar so print the chars
        # from j to i + linelength
        k = j
        while i < j:
            # go backwards until you find a space
            if str[j].isspace():                
                break;
            j -= 1
        # either found a space, or no space
        if i == j:
            # no space: print the full length
            # and append \ to show it continues
            retstr += str[i:k] + "\\\n"
            #print("%s\\" % (str[i:k]))
            i = k
        else:
            # print up to but not including the last blank
            retstr += str[i:j] + "\n"
            #print("%s" % (str[i:j]))
            i = j
    # return the abstract
    return retstr


name = ["Jan. ", "Feb. ", "Mar. ", "Apr. ", "May ", "June ",
        "July ", "Aug. ", "Sep. ", "Oct. ", "Nov. ", "Dec. " ]

def namemonth(mon):
    if not mon.isdigit():
        return mon + ". "
    nmon =  int(mon)
    if 1 <= nmon and nmon <= 12:
        return name[nmon-1]
    return mon + " "





#function to obtain list of PubMed ID's

def pubmed(t,n):
    pubmetadatacontents = {}
    pubmedlink = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=" + str(n) + "&sort=relevance&term=" + t
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn’t verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn’t support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    webcontents = urllib.request.urlopen(pubmedlink)
  
    webdict = json.loads(webcontents.read())
    publist = webdict["esearchresult"]["idlist"]
    
    if publist != []:
        for i in range(len(publist)):
            publist[i] = int(publist[i])
        print("\nYou requested ", n, " publications regarding ", t.replace("+", " "), ".\n\nHere is a list of PubMed ID's for ", str(len(publist)), " publications regarding this topic, sorted by relevance:\n\n", publist, "\n\nBibliography of the above publications with abstract text:\n\n")
    else:
        print('\n\nNo PubMed articles available on the topic "%s". Sorry!\n\n' % (t.replace("+", " ")))
    return publist



#obtain metadata and parse xml

def retrieve_info(publist):
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn’t verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn’t support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    pubmetadata = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + str(publist).replace(" ", "")   
    pubcontents = urllib.request.urlopen(pubmetadata)
    pubstring = pubcontents.read()

    #read contents as string using xml parser (xml.etree.ElementTree as ET)
    root = ET.fromstring(pubstring)    

    #obtain text from each node and root
    pubcount = 1
    for node in root.iter('Article'):
        print(pubcount, end = ". ")

        #start with empty string for citation and keep concatenating it with the information
        biblio = ""

        #using counter and conditional statements since an "and" is needed for the last author
        try:
            count = 0
            for author in node.iter('Author'):
                count += 1
            i = 1
            if count <= 6:
                for author in node.iter('Author'):
                    if author.find('Initials') != None:
                        initl = author.find('Initials').text
                        if author.find('LastName') != None:
                            lastname = author.find('LastName').text
                            if i == count - 1 and count != 1:
                                biblio += initl.strip()+". "+lastname.strip() + " and "
                            else: 
                                biblio += initl.strip()+". "+lastname.strip() + ", "
                    else:
                        if author.find('LastName') != None:
                            lastname = author.find('LastName').text
                            if i == count - 1 and count != 1:
                                biblio += lastname.strip() + " and "
                            else: 

                                biblio += lastname.strip() + ", "
                    i += 1
            else:
                #print just the last name  and "et al." if too many authors (more than six)
                for author in node.iter('Author'):
                    if author.find('LastName') != None:
                        lastname = author.find('LastName').text
                        biblio += lastname.strip() + " et al., "
                        break

            #title
            for titlenode in node.iter('ArticleTitle'):
                if titlenode != None:
                    title = titlenode.text
                    title = title.strip()
                    if title[-1] == '.':
                        title = title[:-1]
                    biblio += '"' + title + ',"'
                    break

            #journal name, using ISO Abbreviation because it makes the journal name the standard short form
            for journal in node.iter('Journal'):
                if journal.find('ISOAbbreviation') != None:
                    journalname = journal.find('ISOAbbreviation').text
                    biblio += " " + journalname + " "
                    break

            #publication info (Volume, Issue)
            for pubinfo in node.iter('JournalIssue'):
                if pubinfo.attrib:
                    if pubinfo.find('Volume'):
                        volume = pubinfo.find('Volume').text
                        biblio += volume
                    if pubinfo.find('Issue'):
                        issue = pubinfo.find('Issue').text
                        biblio += "(" + issue + ") "
                    break
                else:
                    break

            #page numbers
            for pg in node.iter('Pagination'):
                if pg.find('MedlinePgn'):
                    pagenum = pg.find('MedlinePgn').text
                    biblio += "pp. " + pagenum
                    break

            #publication date
            for date in node.iter('PubDate'): 
                biblio += " ("
                if date:
                    month = date.find('Month')
                    year = date.find('Year')
                    if month != None: 
                        biblio += namemonth(month.text)
                    if year != None:
                        biblio += year.text
                    biblio += "). "
                    break

            #PubMed ID (Couldn't be retrieved from <PMID> or <ArticleId> so listed it from publist)
            biblio += "PUBMED: " + str(publist[pubcount - 1]) + "; "
            #PII if it exists
            for pid in node.iter('ELocationID'):
                if pid.attrib['EIdType'] == "pii":
                    pmid = pid.text
                    biblio += "PII: " + pmid + "; "
                    break

            #DOI if it exists
            for eid in node.iter('ELocationID'):
                if eid.attrib['EIdType'] == "doi":
                    doi = eid.text
                    biblio += "DOI: " + doi
                    break
            biblio += " .\n\n"
            #abstract text
            for abstract in node.iter('Abstract'):
                if abstract.find('AbstractText') != None:
                    abstract_text = abstract.find('AbstractText').text
                    if abstract_text == None:
                        biblio += "ABSTRACT:\nAbstract text could not be extracted from the following PubMed ID: " + str(publist[pubcount - 1]) + "\nPlease look this article up manually.\n\n"
                    else:
                        biblio += "ABSTRACT:\n" + linebreak(abstract_text) + "\n"
                    break
            #print concatenated string
            print(biblio)
        except Exception as msg:
            print("Exception: ", msg)
            print("There was a problem with obtaining information from the following PubMed ID: ", str(publist[pubcount - 1]), "\nPlease look this article up manually.\n\n")
            pubcount += 1
            continue
        #continue to next article, pubcount is a counter for the relevant article (in order of PMID's in publist)
        else:
            pubcount += 1
            continue
    return


#bibliography format is authors, title, journal name, volume, issue, pages, publication date, pubmed id, doi
# Iterate for <LastName> and <Initials>
# <ArticleTitle> for article name
# <Journal> has <Title><ISOAbbreviation> 
# <JournalIssue> which has <Volume><Issue><PubDate>
# <Pagination> has <MedlinePgn>
# <PubDate> is in <JournalIssue> and has <Year><Month>
# <ELocationID EIdType="doi" has the DOI <ELocationID EIdType="pii" has the PII
# <AbstractText>


try:
    #ensure valid input for keyword stored in topic and number of publications stored in pubnum
    topic = str(input("\nEnter the keyword/topic you would like to search: "))
    pubnum = int(input("Enter the number of publications you would like returned: "))
    while pubnum <= 0:
        print("Sorry you typed zero or a negative integer! Try again.")
        pubnum = int(input("Enter the number of publications you would like returned: "))

#account for EOF error separately from other errors, good for debugging purposes
except EOFError:
    print("\nEnd of file or some other issue. Sorry!")
    exit()
except:
    print("\nNot end of file but some other problem.\nYou either typed a non-integer for number of publications or there was some other issue.\n\nBye!\n")
    exit()
else:
    topic = topic.replace(" ", "+")
    pubmetalist = pubmed(topic, pubnum)
    if pubmetalist != []:
        retrieve_info(pubmetalist)
    else:
        print("\n\nNo articles - cannot retrieve publication information. Bye!\n\n")
        exit()



