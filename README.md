# This project is part of internship program under [Pixelated Enterprise](http://www.pixelated.asia).

- [About Dmine](https://github.com/amirulmenjeni/dmine/blob/master/README.md#about-dmine)
- [Using Dmine](https://github.com/amirulmenjeni/dmine/blob/master/README.md#using-dmine)

## About Dmine.

Dmine is webscraping tool that extract data from social media and convert the extracted data into something useful. Currently, we are working on supporting widely used social media platform around the globe; [Reddit](http://www.reddit.com), [Twitter](http://www.twitter.com) and [Facebook](http://www.facebook.com). 

## Using Dmine.

### Listing out available spiders.
Dmine have a collection of spiders to choose from. Each spider has its own target site(s). To view the currently available spiders, run the command

    $ dmine -l
    spider_1
    spider_2
    ...
    
You can see that from the output of the command above, `spider_1` and `spider_2` is one of the available spiders. Each line in the output represent the _name_ of each spider. The names are supposed to be unique.
By convention, the spider name intuitively represent the site of its target. Thus, if a spider's name is `reddit`, then you can be fairly sure that the spider target [Reddit](http://www.reddit.com).

### Using a spider.

Suppose you want to run a spider named `spider_1`. Then, you can simply run the spider my executing the
following command.

    $ dmine -s spider_1
    
### Scrap filter.

If you want a spider to filter out the items that it collects, use the [scrap filter](https://github.com/amirulmenjeni/dmine/wiki/Scrap-Filter) that the spider provide. Each spider employ its own scrap filter. Therefore you shouldn't assume that any two spiders share the same scrap filter. Run the following command to find out the detail of a specific spider (e.g. reddit).

    $ dmine -F reddit
    post (p):
    A user submitted content to a subreddit (i.e. submission). Not to be confused with a comment.
        title (t): 
            Value type : STRING_COMPARISON
            Info       : The title of the post.
        score (s): 
            Value type : INT_RANGE
            Info       : The score of the post (i.e. upvotes/downvotes).
        subreddit (r): 
            Value type : STRING_COMPARISON
            Info       : 
        allow-subreddit (A): 
            Value type : LIST
            Info       : Specify which subreddit(s) allowed to be scraped.
        block-subreddit (B): 
            Value type : LIST
            Info       : Specify which subreddit(s) not allowed to be scraped.
    
    comment (c):
    A user submitted comment to a particular post.
        text (t): 
            Value type : STRING_COMPARISON
            Info       : 
        score (s): 
            Value type : INT_RANGE
            Info       : 
    
After we understood the detail of scrap filter for the reddit spider, we can run the spider with its scrap filter as shown below.

    $ dmine -s reddit -f "post{/title: 'fallout' in title /subreddit: subreddit == 'gaming'}"
    
As you may have expected, the scrap filter above will only take posts with the word `fallout` in the title,
and the post is posted from _r/gaming_. The shorter alternative of the above scrap filter is:

    $ dmine -s reddit -f "p{/t:'fallout' in x/s:x == 'gaming'}"

Using this shorter method, we use the scrap component's and scrap option's symbols instead of its names, and
replace each scrap option's placeholder from using its name to use the symbol `x` instead. If you'd like, can also use a mix
of names and symbols like so:

    $ dmine -s reddit -f "p{/title: 'fallout' in x /s: x == 'gaming'}"

You can learn more about scrap filter [here](https://github.com/amirulmenjeni/dmine/wiki/Scrap-Filter).

### Spider Input

While a scrap filter is used to make a 'yes or no' selection as to which component a spider's target website should scrape, a spider input is used to pass information to the spider. What this information is used for is up to the spider's developer to decide. 

To find out what are inputs available for a specfic spider (e.g. `reddit` spider), run the followig comand:

    $ dmine -I reddit
    scan-subreddit (r):
        Input type    : STRING
        Default value : all
        Info          : A comma separated list of subreddits to be scanned.
    limit (l):
        Input type    : INTEGER
        Default value : None
        Info          : The limit on how many posts will be scanned.

Spider input syntax is a bit similar to scrap filter syntax. Use the example above. suppose we want to only scan posts from r/gaming and r/mmorpg, and we want to limit the number of posts scanned to 100 only.We could run the `reddit` command like so:

    $ dmine -s reddit -I "/scan-subreddit: gaming,mmorpg /limit: 100"

Similar to scrap filter, we can use symbols instead of the names of each spider input.

    $ dmine -s reddit -I "/r: gaming,mmorpg /l: 100"



