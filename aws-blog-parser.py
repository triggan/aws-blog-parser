from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys
import json
import argparse

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
    parser = argparse.ArgumentParser(description='Extract contents of an AWS blog.  As of July 12th, 2018.')
    parser.add_argument('-f', action='store_true', help='Output each blog post to a separate .json file.')
    parser.add_argument('blogurl', help='URL of AWS blog. Ex: http://aws.amazon.com/blogs/database/')
    args = vars(parser.parse_args())
    print(args)
    newBlog = args['blogurl']
    siteContent.append(str(simple_get(newBlog)))
except IndexError:
    parser.print_help()
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
    # If the -f flag is set when the script is launched via command line, then output each file to a .json file
    if('f' in args.keys()):
        outputfile = open(Title[0].text.replace("/", "_") + '.json','w')
        json.dump(postJson,outputfile)
        outputfile.close()
    output["posts"].append(postJson)

#If the -f flag is not set, then output all of the contents of the blog and every post to a single JSON to STDOUT.
if('f' not in args.keys()):
    print(json.dumps(output))

print("Processing Completed!")