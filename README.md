# About

**dmine** is a webscraping tool that aims to trivialize the process of extracting data from target websites. 
It make use of a simple scripting language called 
[Scrape Filter Language (SFL)](Scrape-Filter-Language) to help you easily filter out unwanted data.


**NOTE:** This project is part of internship program under [Pixelated Enterprise](http://www.pixelated.asia).


# Quick Guide

### Listing Available Spiders

**dmine** comes with built-in spiders, each specifically named after its target website. You can also
[create your own spider](Createing-A-Spider) to allow it take advantage of SFL for easy filtering.

```
$ dmine -l
reddit
twitter
my_spider
...
```

### Using A Spider

To start scraping a spider, use the `-s` argument and pass the name of the spider you want to use.
For example, to run a spider named *reddit*, execute the following command.

```
$ dmine -s reddit
```

### Filtering data using Scrape Filter Language (SFL)

SFL revolves around the idea that a website is made up of different components composed of different
attributes. Every spider that want to scrape a target website must first determine and defines the 
components of the website it is targeting.

To find out the components defined by *reddit* spider, for example, run the following command.

```
$ dmine -F reddit
COMPONENTS:

 post: A user post or submission.
     score: The upvote/downvote score of the post.
     title: The title of the post.
     subreddit: The subreddit to which the post is uploaded.
     author: The redditor who posted this post.

 comment: A user comment with respect to a post.
     score: The upvote/downvote score of the comment.
     body: The comment text body.
     author: The redditor who posted this comment.

ARGUMENT VARIABLES:

 subreddits: The list of subreddits to scan, seperated by comma.
 sections: Get submissions that only presents in this list.
 skip_comments: Skip comments for each scanned post if set to True.
```

From the above output we know that the *reddit* spider scrape the components
called *post* and *comment*. We also understand that *score*, *title*, *subreddit*,
and *author* are the attributes of the *post* component.

Also note that we know some arguments that the spider can take in order to change its behaviour.
For example, the *subreddits* argument variable allow us to determine which subreddit(s)
to scrape from.

Finally, we can get into the filtering part. Suppose we want to only collect user submissions
that has positive a score, and the word 'awesome' must be present in its title, but not 'gore'. 
Also, we want to skip scanning over the comments from each post, and only scan the
posts in *gaming* and *videos* subreddits. We pass the SFL script to `-f` option,
as shown in the following example.

```
$ dmine -s reddit -f "@subreddits = 'gaming, videos' @skip_comments = True post {score > 0 and ('awesome' in title and not 'gore' in title)}"
```

If you have a lengthy SFL script, you can save the SFL script in a file with a `.sfl` extension 
and then pass it to `-f` option. The following SFL have the same filtering effect as the one
shown above.

```
@subreddits = 'gaming, videos'
@skip_comments = True

post {
    score > 0
    and
    ('awesome' in title and not 'gore' in title)
}
```

You can learn more about SFL [here](Scrape-Filter-Language).

### Other Useful Features

**dmine** comes with several useful features to control the running spiders and its output,
such as a timer to limit the duration of how long the spider will run and
specifying its output format.

The following example will run the *reddit* spider for a maximum 3 of 
hours, and save the scraped data as `jsonlines` format in a 
file called `data.jsonl`.

```
$ dmine -s reddit -w jsonl -o data.jsonl
```

Simply execute `$ dmine -h` to know more.
