from bs4 import BeautifulSoup
import urllib2
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import os

def get_page(url): #cache webpages locally
    filename = 'cache/'+urllib2.quote(url, safe='')
    try:
        return open(filename).read()
    except IOError:
        page = urllib2.urlopen(url).read()
        open(filename, 'w').write(page)
        return page

page = get_page('http://projects.propublica.org/docdollars/states/alabama')
soup = BeautifulSoup(page)
tag = soup.find_all('tr')[1].find_all('td') #


def track_money(tag): #get payment information
    name = tag[0].find(class_=False).string
    site = tag[0].find(href=True)['href']
    
    g.add( (clinic, RDF.type, FOAF.Person) )
    g.add( (clinic, FOAF.name, Literal(name)) )

    

g = Graph()
clinic = BNode()



##PRINTING##

print("--- printing raw triples ---")
for s, p, o in g:
    print((s, p, o))

print("--- printing mboxes ---")
for clinic in g.subjects(RDF.type, FOAF.Person):
    for mbox in g.objects(clinic, FOAF.mbox):
        print(mbox)

print( g.serialize('/home/aimi/pharmasoup/data.rdf', format='xml') )
