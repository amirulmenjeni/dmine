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

To start scraping a spider, use the `-s` argument and 
pass the name of the spider that you want to use.

```
$ dmine -s my_spider
```

### Scrape Filter Language (SFL)

The Scrape Filter Language (SFL) revolves around the idea that a 
website is made up of different components having one or more
attributes. It is therefore a requirement to know beforehand
which components a spider can "see" on its target
website.

To find out the SFL components and arguments defined by 
*my_spider*, run the following command.

```
$ dmine -F my_spider
```

Then we pass the SFL script to `-f` argument, as shown in the following example.

```
$ dmine -s my_spider -f "component_1 { 0 < attr_1 < 100 and 'some_string' in attr_2}"
```

If you have a lengthy SFL script, you can save the SFL script in a file with a `.sfl` extension 
and then pass it to `-f` option. SFL ignores all whitespaces and newlines.

Suppose you have an SFL script saved in the file called `my_spider_filter.sfl`, 
for a spider called *my_spider*, you can simply pass the file name to
`-f` argument.

```
$ dmine -s my_spider -f my_spider_filter.sfl
```

You can learn more about SFL [here](Scrape-Filter-Language).

### Example: Using Reddit Spider

Only collect posts with positive scores and
submitted from the subreddit  [r/gaming](https://www.reddit.com/r/gaming)
and [r/linuxmemes](https://www.reddit.com/r/linuxmemes) with
all comments collected:

```
$ dmine -s reddit -f "@subreddits = 'gaming, linuxmemes' post { score > 0 }"
```

Make the spider skips trodding the comments in each treaded post:

```
$ dmine -s reddit -f "@skip_comments = True"
```

To see more scrape filter components and arguments for the *reddit*
spider, execute the following.

```
$ dmine -F reddit2
```

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

The above example will store the data from *all* components in one
file. If you want to store the collected data separately per
component, run:

```
$ dmine -s reddit -w jsonl -O my_dir
```

This will make the data written on separate files inside the 
`my_dir` directory.

Simply execute `$ dmine -h` to know more.
