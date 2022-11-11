from requests_html import HTMLSession
from selectorlib import Extractor
from fake_useragent import UserAgent
import requests
import urllib.request
import json
import time



class Reviews:

    #asin is the amazon identification number unique to each item sold by amazon
    #title is the URL title (abbriviated main title) used as part of the individual URLs to get to the reviews
    #These two are the unique parts of the review URL, having them allows us to contruct the review page URL 
    #pagedata is the requests-HTML session object
    #headers is the code equivilant of the "I am not a robot" check box, required to access the site
    #url is the url we're costructing to get to the reviews page from the main page, at the end we are leaving off the page number
    #we will append the page number to url in order to "turn the page" in the reviews section
    #the item url will be pulled from a txt file named user_url.text and parsed here
    #the reviews will be collected in a JSON named <asin>-reviews.json to be parsed by the analyzer

    def __init__(self, *args):
        self.asin = asin
        self.title = title
        self.pagedata = HTMLSession()
        self.headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': ua.random,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
        self.url = f'https://www.amazon.com/{self.title}/reviews/{self.asin}/ref=cm_cr_othr_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber='
    

    def next_page(self, page):                            #cycle through pages by adding page number I want to self.url
        r = self.pagedata.get(self.url + str(page))
        if not r.html.find('div[data-hook=review]'):      
            return False
        else:
            return r.html.find('div[data-hook=review]')   #grab a page of review data and return it
            
    
    def get_pages(self):                           #This gets # of reviews, formats the text, and turns it into number of review pages for pagination
        r = self.pagedata.get(self.url + str(1))
        r.html.find('div[data-hook=cr-filter-info-review-rating-count]')        #finds the line with number of reviews
        text = r.html.find('div[data-hook=cr-filter-info-review-rating-count]', first=True).text     #parses the website text to python text

        _, _, _, reviews, *_ = text.split(" ")
        num_rev = ''.join(i for i in reviews if i.isdigit())           # to pull commas from large numbers
        pages = (int(num_rev) // 10) + 1                               # 10 reviews / page
        if int(num_rev) % 10 > 0:                                      # grab the reviews past base 10
            pages = pages + 1
        return pages                       

    def get_image(self, url):
        extract = Extractor.from_yaml_file('amz_img_info.yml')         # activting an extractor instance from selectorlib
        r = requests.get(url, headers=self.headers)                    # requests pulling HTML from user_url
        img_data = extract.extract(r.text)                             # using extractor to capture all the URL with matching attributes from the yml file                           
        #print (img_data)                                              #for troobleshooting

        try:
            if img_data:
                img_data['images'] = img_data['images'].split('\":')[0].split('{"')[1]
                urllib.request.urlretrieve(img_data['images'], "user_img.jpg")
        except:
            pass

                     
       
    def get_reviews(self, reviews):  # collects data from reviews, and appends them to total
        total = []
        try:
            for review in reviews:
                title = review.find('a[data-hook=review-title]', first=True).text
                rating = review.find('i[data-hook=review-star-rating] span', first=True).text
                body = review.find('span[data-hook=review-body] span', first=True).text.replace('\n','').strip()  # exchange newlines with a space

            data = {                                             # dictionary formating the data with title hooks for the analyzer to link to
                "title": title,
                'rating': rating,
                'body': body
            }

            total.append(data)
                
        except:
            pass

        return total


    def save_reviews(self, results):                           #saves reviews to json file
        with open(self.asin + '-reviews.json', 'w') as file:   #file name: <product ASIN>-reviews.JSON
            json.dump(results, file)




if __name__ == '__main__':
    ua = UserAgent()                         # Using User Agent Library, rather than using personal UA
    with open('user_url.txt', "r") as file:  # opens a text file to pull the item's store page URL
        user_url = file.read()               # get url from txt file
        #print(user_url)
    
    _, _, _, title, _, asin, *_ = user_url.split("/")    #pulling asin and item title from given URL
           
    if len(asin) > 10:                      # some asin don't end in a "/", this fixes those.
        temp = asin
        asin = temp[0 : 9]

  
    amz_rvw = Reviews(asin, title)  # Call with asin and title, needed to find reviews page
    
    amz_rvw.get_image(user_url)
    
    pages = amz_rvw.get_pages()   #for pagination, finds # of reviews and turns that into a number of review pages
    #print(pages)                   #test for making sure reviews are being parsed

    results = []                    # gather output

    for x in range(1, pages):      # pagination
        print('getting page ', x)
        time.sleep(0.1)             # a pause to slow us down, ensuring more consistent results
        reviews = amz_rvw.next_page(x)
        if reviews is not False:
            results.append(amz_rvw.get_reviews(reviews))   #collecting reviews
        else:
            print('no more pages')
            break

    #print(results)

    amz_rvw.save_reviews(results)       #saving collected reviews to JSON


