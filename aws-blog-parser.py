from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys
import json

# Global Variables
siteContent = []  #Array containing the HTML of each blogs paginated blog post titles and previews
blogPosts = []  #Array containing the URLs for each blog post
output = {}  #JSON document containing all posts, author, data published, and tags

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

# Attempt to get the Blog URL to parse
try:
    newBlog = sys.argv[1]
    siteContent.append(str(simple_get(newBlog)))
except IndexError:
    log_error("Please provide a URL of a blog to parse.\nExample:\n\t python3 aws-blog-parser.py http://aws.amazon.com/blogs/database/")
    exit()

# Starting with the second page of Older Post, pull the contents of each subsequent page into an array
pageNumber = 2
siteURL = newBlog + 'page/' + str(pageNumber) + '/'
nextSiteContent = simple_get(siteURL)
while(nextSiteContent != 'None'):
    siteContent.append(nextSiteContent)
    pageNumber += 1
    siteURL = newBlog + 'page/' + str(pageNumber) + '/'
    nextSiteContent = str(simple_get(siteURL))

print("Number of pages found: " + str(len(siteContent)))

# Take each page of the blog contents and parse out the URL for each separate blog post
for page in siteContent:
    html = BeautifulSoup(page, 'html.parser')
    Urls = html.select('h2[class="blog-post-title"] a[href]')
    for url in Urls:
        blogPosts.append(url.get('href'))

print("Number of blog posts found: " + str(len(blogPosts)))
# Using the URLs for each of the posts - contained in blogPosts[] - collect the HTML for the post site
# then parse the contents.  Return Author, Date, Tags, and Post Contents in a JSON.
output['posts'] = [] #declare a new array of posts within the output JSON document.
for post in blogPosts:
    print("Processing post at: " + post)
    postHtml = BeautifulSoup(simple_get(post), 'html.parser')
    Authors = postHtml.select('span[property="author"]')
    Title = postHtml.select('h1[property="name headline"]')
    DatePublished = postHtml.select('time[property="datePublished"]')
    Categories = postHtml.select('span[property="articleSection"]')
    postContent = postHtml.select('section[property="articleBody"]')
    tagArray = []
    authorArray = []
    for tag in Categories:
        tagArray.append(tag.text)
    for auth in Authors:
        authorArray.append(auth.text)
    postJson = {}
    postJson["url"] = post
    postJson["title"] = Title[0].text
    postJson["authors"] = authorArray
    postJson["date"] = DatePublished[0].text
    postJson["tags"] = tagArray
    postJson["post"] = postContent[0].text
    outputfile = open(Title[0].text.replace("/", "_") + '.html','w')
    json.dump(postJson,outputfile)
    outputfile.close()
    output["posts"].append(postJson)


print("Processing Completed!")