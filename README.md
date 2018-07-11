# aws-blog-parser

This project was developed as a means to extract the contents of each Amazon Web Services (AWS) Blog for the purposes of reusing the contents of the blog posts as sample data within other workloads (i.e. NLP, topic extraction, etc.).

## Getting Started

Use the following instructions for installing and running this script.

### Prerequisites

Before downloading this repo and running the script, you will need to install the following libraries:

```
$ pip install requests BeautifulSoup4
```

### Installation

To use this script, clone a copy of this repo:

```
$ git clone https://github.com/triggan/aws-blog-parser.git
$ cd aws-blog-parser
```

### Running the Script

To run the script, use the following syntax:

```
$ python aws-blog-parser.py <site_URL>
```
Example:
```
$ python aws-blog-parser.py https://aws.amazon.com/blogs/architecture/
```

### Script Output

The script will provide output in the following format via STDOUT.  You can pipe the output of this script to a file to use elsewhere.

```
{
    posts: [
        {
            url: <blog post url>,
            authors: [
                <blog author 1>,
                <blog author 2>,
                ...
                <blog author n>
            ],
            date: <blog published date>,
            tags: [
                <blog category tag 1>,
                <blog category tag 2>,
                ...
                <blog category tag n>
            ],
            post: <blog post text content>
        }
    ]
}
```

## Authors

- Taylor Riggan - @triggan

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgements

- This blog post helped tremendously while I was developing this script: https://realpython.com/python-web-scraping-practical-introduction/