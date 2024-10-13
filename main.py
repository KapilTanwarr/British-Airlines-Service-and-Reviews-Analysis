import re  # Regular Expressions for pattern matching
import requests  # For making HTTP requests
from bs4 import BeautifulSoup, SoupStrainer  # For parsing HTML

# Set the URL to scrape British Airways reviews
URL = "https://www.airlinequality.com/airline-reviews/british-airways/page/page_no/?sortby=post_date%3ADesc&pagesize=100"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.59",
    "Accept-Language": "en-US,en;q=0.9"
}

# Prompt user for filename to save the scraped data as a CSV
filename = input("Save data as (filename.extension): ")
while not filename:
    print("Invalid filename.")
    filename = input("Save data as (filename.extension): ")

# Open file to write data, and define CSV headers
with open(filename, 'w') as file:
    file.write("rating,header,customer_country,date,review,Aircraft,Type of Traveller,Seat Type,Route,Date Flown,Seat Comfort,Cabin Staff Service,Food & Beverages,Inflight Entertainment,Ground Service,Wifi & Connectivity,Value For Money,Recommended\n")

    # Loop through 36 pages of reviews
    for i in range(1, 37):
        # Make a GET request for each review page
        response = requests.get(url=URL.replace('page_no', str(i)), headers=headers)

        # Parse only the 'article' elements that match the review section using SoupStrainer
        articles = SoupStrainer("article", class_=re.compile("list-item"))
        soup = BeautifulSoup(response.text, 'html.parser', parse_only=articles)
        articles = soup.find_all('article')

        # Loop through each article (review) found
        for article in articles:
            # Extract the rating out of 10
            rating = article.find('div', class_="rating-10").get_text().strip().split("/")[0]
            
            # Extract the review header (title)
            header = article.find('h2', class_="text_header").string.replace(",", "")

            # Extract customer country and review date
            try:
                cust_details1 = article.find('h3', class_="text_sub_header").get_text().strip().split("(")
                customer_country = cust_details1[1].split(") ")[0]
                date = cust_details1[1].split(") ")[1]
            except (AttributeError, IndexError):
                customer_country, date = '', ''

            # Extract the review text, clean up, and handle cases without " |"
            try:
                review = article.find('div', class_="text_content").get_text().split(" |")[1].strip().replace(",", "")
            except IndexError:
                review = article.find('div', class_="text_content").get_text().strip().replace(",", "")

            # Initialize dictionary for each review with default values
            my_dict = {
                "rating": rating,
                "header": header,
                "customer_country": customer_country,
                "date": date,
                "review": '"'+review+'"',
                "Aircraft": '',
                "Type Of Traveller": '',
                "Seat Type": '',
                "Route": '',
                "Date Flown": '',
                "Seat Comfort": '',
                "Cabin Staff Service": '',
                "Food & Beverages": '',
                "Inflight Entertainment": '',
                "Ground Service": '',
                "Wifi & Connectivity": '',
                "Value For Money": '',
                "Recommended": ''
            }

            # Parse the article HTML again to extract more specific data
            article = BeautifulSoup(str(article), 'html.parser')

            # Extract each 'td' element with the review value (such as 'Aircraft', 'Seat Type', etc.)
            for i in article.find_all('td', 'review-value'):
                my_dict[i.previousSibling.get_text()] = i.get_text()

            # Extract review rating stars for categories like 'Seat Comfort', 'Cabin Staff Service', etc.
            for j in article.find_all('td', 'review-rating-stars'):
                my_dict[j.parent.find('td', 'review-rating-header').get_text()] = str(len(j.parent.find_all('span', class_="fill")))

            # Write the review data to the file, handling encoding errors
            try:
                print(",".join(str(value) for value in my_dict.values()), file=file)
            except UnicodeEncodeError:
                pass  # Skip reviews that cause encoding errors
