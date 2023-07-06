"""Webscraping functions for collecting articles."""

import requests
import feedparser
import time
import re
from bs4 import BeautifulSoup

CRAWL_DELAY = 5
DEFAULT_HEADERS = {
    "Accept-Language":"en-US,en;q=0.9",
    "User-Agent":"Mozilla/5.0 (Macintosh; \
    Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/98.0.4758.102 Safari/537.36"
}

##### ARXIV #####

def collect_arxiv(cats, limit=50, checkpoint=None):
    """Collect arXiv papers by category using feedparser.
    Example categories: ['cs.*', 'econ.*', 'stat.ML']
    Reference for category names: https://arxiv.org/category_taxonomy

    Params
    ----------
    cats: list[str]
        List of categories in arXiv format e.g. cs.AI for artificial intelligence.
    limit: int, default = 50
        Total number of papers to be retrieved. Should be a multiple of 10.

    checkpoint : str, default = None
        URL of the most recent paper for a particular query. To be used
        in the case of repeated queries. Collection will terminate if the checkpoint
        is encountered.

    Returns
    ----------
    Tuple[list, str] : (List of dicts, checkpoint)
        Each dict refers to a paper. Checkpoint is the url from the most
        recent paper retrieved."""

    base_url = 'http://export.arxiv.org/api/query?search_query='
    params = '&sortBy=lastUpdatedDate&sortOrder=descending'

    cat_concat = '+OR+'.join(['cat:'+cat for cat in cats])

    # Defaults
    start = 0
    page_size = 10
    entries = []
    new_checkpoint = checkpoint

    for i in range(start, limit, page_size):
        feed = feedparser.parse(
            base_url+cat_concat+params+f'&start={i}&max_results={page_size}'
        )

        # Check for failed retrievals
        if not feed.bozo and feed.entries:
            for entry in feed.entries:
                # Early stopping condition
                if entry.link == checkpoint:
                    return entries, new_checkpoint
                # Build a dict from entry details
                entries.append({
                    'title': entry.title_detail.value,
                    'summary': entry.summary_detail.value,
                    'author': entry.author,
                    'url': entry.link,
                    'category': entry.arxiv_primary_category['term']
                })
            # Set a new checkpoint after first successful update
            if new_checkpoint == checkpoint:
                new_checkpoint = entries[0]['url']

        time.sleep(CRAWL_DELAY)

    return entries, new_checkpoint


##### HACKERNEWS #####


def collect_hn_post_data(num_pages=1):
    """Collect data on posts from the front page(s) of HackerNews.

    Params
    ----------
    num_pages: int, default = 1
        Total number of pages to be scraped.
    Returns
    ----------
    List[dict]
        A list of dicts, each containing details of a HackerNews post.
        If an error occurs, the current list (or empty list) is returned."""

    news_url = 'https://news.ycombinator.com/news?p='
    post_url = 'https://news.ycombinator.com/item?'
    detail_url = 'https://news.ycombinator.com/'
    posts = []

    for page_num in range(1, num_pages+1):

        try:
            page = requests.get(news_url+str(page_num))
        except:
            return posts

        if page.status_code != 200:
            return posts

        soup = BeautifulSoup(page.content)
        all_posts = soup.find_all('tr', class_='athing')

        for post in all_posts:
            post_data = {}

            title = post.find_all('a')[-2]
            post_data['title'] = title.get_text(strip=True)

            link = title['href']
            if link.startswith('http'):
                post_data['url'] = link
            else:
                post_data['url'] = post_url + re.search(r'id=[0-9]+', link)[0]

            post_detail_url = detail_url + post.next_sibling.find_all('a')[-1]['href']
            print(post_detail_url, detail_url)
            post_data['detail_url'] = post_detail_url

            subtitle = post.next_sibling.text.split()
            post_data['points'] = int(subtitle[0])
            post_data['comments'] = int(subtitle[-2]) if subtitle[-2].isnumeric() else 0

            posts.append(post_data)

            if num_pages > 1:
                time.sleep(CRAWL_DELAY)

        return posts


def collect_hn_comments(url, max_comments=50):
    """Collect comments from a HackerNews post.

    Params
    ----------
    url: str
        URL to a HackerNews post.
    max_comments: int, default = 50
        Maximum comments to be retrieved.

    Returns
    ----------
    List[str] | None
        A list of each comment as a single string.
        If an error occurs, returns None."""

    try:
        page = requests.get(url)
    except:
        return None

    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content)

    comments_list = []

    for comm in soup.find_all('tr', class_='athing comtr')[:max_comments]:
        comment = comm.find('span', class_='commtext').get_text(strip=True)
        comments_list.append(comment)

    return comments_list


##### TECHMEME #####

def collect_techmeme_fp(mode: str ='all'):
    """Collect data on posts from the front page of Techmeme.

    Params
    ----------
    mode: str, default = 'all'
        Determines how many articles to pull. Should be 'all' (~48),
        'most' (30), or 'some' (12).
    Returns
    ----------
    List[dict] | None
        A list of dicts, each containing details of a Techmeme post.
        If an error occurs, returns None."""

    if mode == 'all':
        cap = None
    elif mode == 'most':
        cap = 30
    elif mode == 'some':
        cap = 12
    else:
        raise ValueError(f'Value for "mode" must be "all", "most", or "some". Not "{mode}".')


    url = 'https://www.techmeme.com/'
    res = requests.get(url)

    if res.status_code != 200:
        return None

    articles = []

    soup = BeautifulSoup(res.content)
    all_articles = soup.find_all('a', class_='ourh')

    for article in all_articles:
        post = {}

        post['title'] = article.get_text(strip=True)
        post['url'] = article.get('href', 0)

        articles.append(post)

    return articles


##### LITTLEWHITELIES #####


def collect_lwl_reviews(checkpoint=None):
    """Collect data on reviews from the littlewhitelies movie blog.

    Params
    ----------
    checkpoint: str
        Name of the most recent article scraped. Stops collecting articles
        when encountered.
    Returns
    ----------
    List[dict] | None
        A list of dicts, each containing details of a review.
        If an error occurs or checkpoint is first item, returns None."""


    res = requests.get('https://lwlies.com/reviews/')

    if res.status_code != 200:
        return None

    lwl_rev = BeautifulSoup(res.content)
    articles_list = []
    posts = lwl_rev.find_all('div', class_='postBlock')

    for post in posts:
        post_dict = {}

        post_dict['title'] = post.find('h3').get_text()

        if post_dict['title'] == checkpoint:
            if articles_list:
                return articles_list
            else:
                return None

        post_dict['author'] = post.select_one('p a').get_text()
        post_dict['url'] = post.find('a').get('href', None)
        post_dict['blurb'] = post.find('p', class_='excerpt').get_text()

        score_types = ['anticipation', 'enjoyment', 'retrospect']
        marker = 0
        scores = post.find_all('span')
        for score in scores:
            if score.get('class', None) and score['class'][-1].startswith('icon-rating'):
                post_dict[score_types[marker]] = int(score['class'][-1][-1])
                marker += 1


        articles_list.append(post_dict)

    return articles_list


##### ROGEREBERT #####

def collect_ebert_reviews(checkpoint=None):
    """Get titles, links, and scores from reviews page of rogerebert.com"""

    review_url = 'https://www.rogerebert.com/reviews'
    base_url = 'https://www.rogerebert.com'

    try:
        res = requests.get(review_url)
    except:
        return None

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content)
    reviews = soup.find_all('div', class_='review-stack')

    review_list = []

    for review in reviews:
        review_data = {}

        title = review_data['title'] = review.find('h5').get_text(strip=True)
        if title == checkpoint:
            return review_list or None

        review_data['author'] = review.find('h6').get_text(strip=True)
        review_data['url'] = base_url + review.find('a').get('href')

        score_stars = review.find('span').find_all('i')
        score = 0
        for star in score_stars:
            if star.get('title') == 'star-full':
                score +=1
            elif star.get('title') == 'star-half':
                score +=.5

        if score == 0:
            continue

        review_data['score'] = score
        review_list.append(review_data)

    return review_list

def collect_ebert_review_details(url):
    """Collected detailed information from a review on rogerebert.com"""

    try:
        res = requests.get(url)
    except:
        return None

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content)

    details = {}

    article = []
    text_blocks = soup.find_all('section', class_='page-content--block_editor-content')
    for block in text_blocks:
        article.append(block.get_text(strip=True))

    details['review_text'] = ' '.join(article)

    tag_list = []
    tags = soup.find_all('div', class_='tags--tag')
    for tag in tags:
        tag_list.append(tag.get_text(strip=True))

    details['tags'] = tag_list

    return details

def compile_reviews_details(movie_list):
    """Create complete reviews for movies."""

    compiled_reviews = []

    for review_stub in movie_list:
        details = collect_ebert_review_details(review_stub['url'])
        review_stub.update(details)
        compiled_reviews.append(review_stub)

        time.sleep(CRAWL_DELAY)

    return compiled_reviews


##### HOLLYWOOD REPORTER #####

def collect_hr_reviews(checkpoint=None):
    """Collect data on reviews from the hollywood reporter movie blog.

    Params
    ----------
    checkpoint: str
        Title of the most recent article scraped. Stops collecting articles
        when encountered.
    Returns
    ----------
    List[dict] | None
        A list of dicts, each containing details of a review.
        If an error occurs or checkpoint is first item, returns None."""

    url = 'https://www.hollywoodreporter.com/c/movies/movie-reviews/'

    try:
        res = requests.get(url)
    except:
        return None

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content)
    reviews = soup.find_all('div', class_='story')

    reviews_list = []

    for review in reviews:
        details = {}

        title = details['title'] = review.find('a').get_text(strip=True)
        if title == checkpoint:
            return reviews_list or None

        details['url'] = review.find('a').get('href')
        details['blurb'] = review.find('p').get_text(strip=True)
        details['author'] = review.find('div', class_='c-tagline').get_text(strip=True)

        reviews_list.append(details)

    return reviews_list


##### NPR BOOKS #####

def collect_npr_reviews(checkpoint=None):
    """Collect data on reviews from the npr book reviews page.

    Params
    ----------
    checkpoint: str
        Title of the most recent article scraped. Stops collecting articles
        when encountered.
    Returns
    ----------
    List[dict] | None
        A list of dicts, each containing details of a review.
        If an error occurs or checkpoint is first item, returns None."""

    url = 'https://www.npr.org/sections/book-reviews/'

    try:
        res = requests.get(url)
    except:
        return None

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content)
    article_list = []
    reviews = soup.find_all('article', class_='item has-image')

    for review in reviews:
        details = {}

        title = details['title'] = review.find('h2').get_text(strip=True)
        if title == checkpoint:
            return article_list or None
        details['url'] = review.find('a').get('href')
        details['blurb'] = review.find('p').get_text(strip=True).split('\x95')[1]

        article_list.append(details)

    return article_list


##### NYT BOOKS #####


def collect_nyt_reviews(checkpoint=None):
    """Collect data on reviews from the nyt book reviews page.

    Params
    ----------
    checkpoint: str
        Title of the most recent article scraped. Stops collecting articles
        when encountered.
    Returns
    ----------
    List[dict] | None
        A list of dicts, each containing details of a review.
        If an error occurs or checkpoint is first item, returns None."""

    url = 'https://www.nytimes.com/section/books/review'
    base_url = 'https://www.nytimes.com'

    try:
        res = requests.get(url)
    except:
        return None

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content)
    article_list = []
    reviews = soup.find('section', id='stream-panel').select('li a')

    for review in reviews:
        details = {}

        header = review.find('h3')
        if not header:
            continue

        title = details['title'] = header.get_text(strip=True)
        if title == checkpoint:
            return article_list or None
        details['url'] = base_url + review.get('href')
        details['blurb'] = review.find('p').get_text(strip=True)

        article_list.append(details)

    return article_list
