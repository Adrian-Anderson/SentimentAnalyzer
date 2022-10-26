from requests_html import HTMLSession
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        self.url = f'https://www.amazon.com/{self.title}/reviews/{self.asin}/ref=cm_cr_othr_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber='
    

    def next_page(self, page):                            #cycle through pages by adding page number I want to self.url
        r = self.pagedata.get(self.url + str(page))
        if not r.html.find('div[data-hook=review]'):
            return False
        else:
            return r.html.find('div[data-hook=review]')


    def get_reviews(self, reviews):                       #collects data from reviews, and appends them to total
        total = []
        for review in reviews:
            title = review.find('a[data-hook=review-title]', first=True).text
            rating = review.find('i[data-hook=review-star-rating] span', first=True).text
            body = review.find('span[data-hook=review-body] span', first=True).text.replace('\n', '').strip()  #exchange newlines with a space

            data = {                                     #dictionary formating the data with title hooks for the analyzer to link to
                "title": title,
                'rating': rating,
                'body': body
            }

            total.append(data)                   
        return total

    def save_reviews(self, results):
        with open(self.asin + '-reviews.json', 'w') as file:
            json.dump(results, file)




if __name__ == '__main__':      
    with open('user_url.txt', "r") as file:              #opens a text file to pull the item's store page URL
        user_url = file.read()                  
        print(user_url)
    _, _, _, title, _, asin, *_ = user_url.split("/")    #pulls the items asin and title from the store page URL
   
    amz_rvw = Reviews(asin, title)                        #Call with asin and title, needed to find reviews page
   
    results = []                                         #gather output

    for x in range(1, 9):                                #pagination
        print('getting page ', x)
        time.sleep(0.5)                                  #a pause to ensure we get the reviews
        reviews = amz_rvw.next_page(x)
        if reviews is not False:
            results.append(amz_rvw.get_reviews(reviews))
        else:
            print('no more pages')
            break

    print(results)

    amz_rvw.save_reviews(results)
    