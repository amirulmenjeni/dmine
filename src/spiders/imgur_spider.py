from imgurpython import ImgurClient
from dmine import Spider, ComponentLoader

class ImgurSpider(Spider):

    name = 'imgur'
    imgur = None

    def setup_filter(self, sf):
        sf.add_com('post', info='A post.')
        sf.add_com('comment', info='A comment in reply to a post.')
        
        sf_post = sf.get('post')
        sf_post.add('title', info='The title of the post.')
        sf_post.add('author', info='The user who submitted the post.')
        sf_post.add('score', info='The score of the post.')
        sf_post.add('points', info='The points of the post.')
        sf_post.add('views', info='The view count of the post.')

        sf_comment = sf.get('comment')
        sf_comment.add('body', info='The body of the comment.')
        sf_comment.add('author', info='The user who submitted the comment.')
        sf_comment.add('score', info='The score of the comment.')

        sf.add_var(
            'sections', type=list, default=['hot', 'new'],
            info="Determine which sections posts are going to be "\
                 "retrieved from. The 'hot' section is labelled as "\
                 "'most viral' "\
                 "in imgur.com, and the 'new' section is labelled as "\
                 "'user submitted'"
        )
        sf.add_var(
            'time', type=str,
            choice=['today', 'this week', 'this month',\
                    'this year', 'all time'],
            default='today',
            info="The time frame of when the post was submitted. Note that "\
                 "this only applies to a 'hot' section with 'top' sorting. "
        )
        sf.add_var(
            'sort', type=str,
            choice=['popularity', 'top', 'newest'],
            default='popularity',
            info="Choose the order in how the posts are to be scanned. "\
                 "Note that the 'top' choice can be configured further "\
                 "with the @time attribute."
        )
        sf.add_var(
            'tags', type=list, default=[],
            info="If this list is not empty, then the spider will ONLY "\
                 "scan for posts with the given tags in this list."
        )
        sf.add_var(
            'skip_comments', type=bool, default=False,
            info='Skip scanning over comments for every scanned post.'
        )

    def start(self, sf):
        client_id = '93814a7ab6dccf6'
        client_secret = 'c9ed8ffe67e553f10f8d587f5d335ae68264fd92'
        self.imgur = ImgurClient(client_id, client_secret)

#        for page in self.page_generator(sf):
#            for item in page:
#                yield item

    def page_generator(self, sf):
        """
        An item list generator containing the items in a page.
        """
        sf_sections = sf.ret('sections')
        sf_time = sf.ret('time')
        sf_sort = sf.ret('sort')
        sf_tags = sf.ret('tags')
        for section in sf_sections:
            page = 0
            while True:
                items = self.imgur.gallery(
                    section=section,
                    sort=sort,
                    page=page,
                    window='day'
                )
                page += 1
                yield items

    def scrape_gallery(self, sf, galleries):
        pass

    def scrape_comments(self, sf, gallery):
        pass

