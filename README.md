# This project is part of internship program under [Pixelated Enterprise](http://www.pixelated.asia).

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
By convention, the spider name intuitively represent the site of its target. Thus, if a spider's name is `reddit`, then you can be fairly sure that it target [Reddit](http://www.reddit.com) site.

### Using a spider.

Suppose you want to run a spider named `spider_1`. Then, you can simply run the spider my executing the
following command.

    $ dmine -s spider_1
    
### Scrap filter.

If you want a spider to filter out the items that it collects, use the [scrap filter](https://github.com/amirulmenjeni/dmine/wiki/Scrap-Filter) that the spider provide. Each spider employ its own scrap filter. Therefore you shouldn't assume that any two spiders share the same scrap filter. Run the following command
to find out the detail of a specific spider (not yet implemented).

    $ dmine -s reddit -F
   	post (p): /title (t) [STRING_COMPARISON], /subreddit (s) [STRING_COMPARISON], ...
    comment (c): /text (t) [STRING_COMPARISON], /score (s) [INT_RANGE], ...
    
From the output executed above, we can now read the detail of the scrap filter for a spider named `reddit`.
The part `post (p)` and `comment (c)` represent its scrap filter components, where `post` and `comment` is the 
component name, and `(p)` and `(c)` is their respective symbol. Furthermore, the names of the scrap option for each scrap component are prefixed with `/`. The all capitalized string enclosed in the square braces `[...]` represent the type of input that a scrap option is expected to get.

After we understood the detail of scrap filter for the reddit spider, we can run the spider with its scrap filter as shown below.

    $ dmine -s reddit -f "post{/title: 'fallout' in title /subreddit: subreddit == 'gaming'}"
    
As you may have expected, the scrap filter above will only take posts with the word `fallout` in the title,
and the post is posted from _r/gaming_. The shorter alternative of the above scrap filter is:

    $ dmine -s reddit -f "p{/t:'fallout' in x/s:s == 'gaming'}"

In the shorter alternatives, we use the scrap component's and scrap option's symbols instead of its names, and
replace each scrap option's placeholder from using its name to use the symbol `x` instead.

You can learn more about scrap filter [here](https://github.com/amirulmenjeni/dmine/wiki/Scrap-Filter).

## Coding style convention.

You can read about our coding style convention [here](Coding-Convention).

