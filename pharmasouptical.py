from bs4 import BeautifulSoup
import urllib2
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import Namespace, FOAF
import os

PAY = Namespace("http://reference.data.gov.uk/def/payment")

def get_page(url): #cache webpages locally
    print url
    filename = 'cache/'+urllib2.quote(url, safe='')
    try:
        return open(filename).read()
    except IOError:
        page = urllib2.urlopen(url).read()
        open(filename, 'w').write(page)
        return page

mainpage = get_page('http://projects.propublica.org/docdollars/')
majorsoup = BeautifulSoup(mainpage)
States = []
for td in majorsoup.find_all("td",class_="label",style=False)[1:-1]:
    States.append(td.string)
g = Graph()
state = BNode()
clinic = BNode()
company = BNode()
transaction = BNode()
payment = BNode()

for state in States:
    try:
        page = get_page('http://projects.propublica.org/docdollars/states/'+state.replace(' ','-'))
        soup = BeautifulSoup(page)
        state_txns = soup.find_all('tr') #find all transactions
    except urllib2.HTTPError:
        print state+' not available'
        continue

    def track(tag): #get payment information
        #clinic info
        clinic_name = tag[0].find(class_=False).string
        DDsite = tag[0].find(href=True)['href'] #Propublica's docdollars site
        city = tag[1].string.strip() #city
        state = soup.find("strong").string #state

        g.add( (clinic, RDF.type, FOAF.Organization) )
        g.add( (clinic, FOAF.name, Literal(clinic_name)) )
        g.add( (clinic, FOAF.Document, URIRef(DDsite)) )
        g.add( (clinic, FOAF.based_near, Literal(city)) )
        g.add( (clinic, FOAF.based_near, Literal(state.replace(' ','_'))) )

        #company info
        company_name =  tag[2].string.strip()
        g.add( (company, RDF.type, FOAF.Organization) )
        g.add( (company, FOAF.name, Literal(company_name)) )

        #transaction info
        #year = tag[3].string.strip()
        #purpose = tag[4].string.strip()
        #dollars = tag[5].string.strip()
        g.add( (transaction, RDF.type, PAY.Payment) )
        g.add( (transaction, PAY.payee, company) )
        g.add( (transaction, PAY.payer, clinic) )
        #g.add( (transaction, PAY.purchase, purpose) )  #can't find correct BVACOP
        #g.add( (transaction, PAY.date, year) )
        #g.add( (transaction, PAY.grossAmount, dollars) )

    for index in range(1,len(state_txns)):
        txn = state_txns[index].find_all('td')
        track(txn)

##PRINTING##

print( g.serialize(format='xml') )

print( g.serialize('/home/aimi/pharmasoup/data.rdf', format='xml') )
