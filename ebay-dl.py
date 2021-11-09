import argparse
from typing import Text
import requests
from bs4 import BeautifulSoup
import json

def parse_itemssold(text):
    ''''
    Takes as input a string and returns the number of items sold, as specified in the string
    
    >>> parse_itemssold('78 sold')
    78
    >>> parse_itemssold('14 watchers')
    0
    >>> parse_itemssold('Almost gone')
    0
    '''

    numbers = ''
    for char in text:
        if char in '1234567890':
            numbers += char
    if 'sold' in text:
        return int(numbers)
    else:
        return 0

def parse_itemsshipping(text):
    '''
    takes input as a string and returns the shipping cost as required 
    >>> parse_itemsshipping('+$5.00 shipping')
    500
    >>> parse_itemsshipping('Free shipping')
    0
    >>> parse_itemsshipping('+$31.31 shipping estimate')
    3131
    '''
    numbers = ''
    for char in text:
        if char in '1234567890':
            numbers += char
    if 'shipping' in text:
        if numbers == '':
            return 0
        return int(numbers) 
    else:
        return None   

    
def parse_price(text):
    '''
    Takes as input a string and returns the price of the item as specified in the string
    >>> parse_price ('$15.95')
    1595
    >>> parse_price ('$24.36 to $141.04') 
    2436
    '''
    numbers = ''
    if '$' not in text:
        return 0
    elif 'to' in text:
        num= text.split(' to ')
        fgh = num[0]  
        for char in fgh:
            if char in '1234567890':
                numbers += char
        return int(numbers)
    else:
        for char in text:
            if char in '1234567890':
                numbers += char
        return int(numbers)
    

if __name__== '__main__':

    #get command line arguements 
    parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON. ')
    parser.add_argument('search_term')
    parser.add_argument('--num_pages', default=10)
    parser.add_argument('--csv', nargs= '?')
    args = parser.parse_args()
    print('args.search_term=', args.search_term)

    #list of all items found on all ebay webpages
    items = []

    #loop over the ebay web pages
    for page_number in range (1,int(args.num_pages)+1):

        #build the url
        url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
        url += args.search_term
        url += '&_sacat=0&LH_TitleDesc=0&_pgn='
        url += str(page_number)
        url += '&rt=nc'
        print('url=', url)

        # download the html
        r = requests.get(url)
        status = r.status_code
        print('status=', status)
        html=r.text

        #process the html
        soup = BeautifulSoup(html, 'html.parser') 

        # loop over the items in the page 
        tags_items = soup.select('.s-item')
        for tag_item in tags_items:

            #extract the name 
            name = None
            tags_name = tag_item.select('.s-item__title')
            for tag in tags_name:
                name= tag.text

            # extract the free_returns
            freereturns = False
            tags_freereturns = tag_item.select('.s-item__free-returns')
            for tag in tags_freereturns:
                freereturns = True

            #items sold 
            items_sold=None
            tags_itemssold = tag_item.select('.s-item__hotness')
            for tag in tags_itemssold:
                items_sold = parse_itemssold(tag.text)
            
            #item status 
            items_status = None
            tags_itemssatus = tag_item.select('.s-item__subtitle')
            for tag in tags_itemssatus:
                items_status= tag.text
            
            #price
            price =  None
            tags_price = tag_item.select('.s-item__price')
            for tag in tags_price:
                price = parse_price(tag.text)
                
            
            items_shipping = None
            tags_itemsshipping = tag_item.select('.s-item__shipping')
            for tag in tags_itemsshipping:
                items_shipping = parse_itemsshipping(tag.text)


            #dictionary 
            item = {
                'name': name,
                'free_returns': freereturns,
                'items_sold': items_sold,
                'items_status': items_status,
                'items_shipping': items_shipping,
                'price': price,
            }
            items.append(item)
            
        print ( 'len(tags_items)=', len(tags_items))
        print ('len(items)=', len(items))



    # write the json to a file
    if args.csv:
        filename = args.search_term+'.csv'
    else:
        filename = args.search_term+'.json'
    with open(filename, 'w', encoding= 'ascii') as f:
        f.write(json.dumps(items))
    
    # 'surfboard' --csv [CSV] 
