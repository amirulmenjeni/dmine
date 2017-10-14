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
        sf_post.add('description', info='The description of the post.')
        sf_post.add('author', info='The user who submitted the post.')
        sf_post.add('points', info='The points of the post.')
        sf_post.add('score', info='The score of the post.')
        sf_post.add('ups', info='The number upvotes the post get.')
        sf_post.add('downs', info='The number of downvotes the post get.')
        sf_post.add('views', info='The view count of the post.')
        sf_post.add('tags', info='The tags labelled on the post.')
        sf_post.add('nsfw', info='States whether or not the post is NSFW.')

        sf_comment = sf.get('comment')
        sf_comment.add('body', info='The body of the comment.')
        sf_comment.add('author', info='The user who submitted the comment.')
        sf_comment.add('points', info='The points of the comment.')
        sf_comment.add('ups', info='The upvotes the comment get.')
        sf_comment.add('downs', info='The downvotes the comment get.')

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
            choice=['day', 'week', 'month',\
                    'year', 'all'],
            default='day',
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
            'skip_comments', type=bool, default=False,
            info='Skip scanning over comments for every scanned post.'
        )
        sf.add_var(
            'page_limit', type=int, default=999999,
            info="The limit on how many page will the spider scan before it "\
                 "stops. The default is -1 (no limit)."
        )

    def start(self, sf):
        client_id = '93814a7ab6dccf6'
        client_secret = 'c9ed8ffe67e553f10f8d587f5d335ae68264fd92'
        self.imgur = ImgurClient(client_id, client_secret)

        for item in self.generator(sf):
            yield item

    def generator(self, sf):
        """
        An item list generator containing the items in a page.
        """
        sf_sections = sf.ret('sections')
        sf_time = sf.ret('time')
        sf_sort = sf.ret('sort')
        p = 0
        for section in sf_sections:
            while True:
                if p >= sf.ret('page_limit'):
                    return
                page = self.imgur.gallery(
                    section=section,
                    sort=sf_sort,
                    page=p,
                    window=sf.ret('time')
                )
                p += 1
                for post in self.generate_post(sf, page):
                    yield post

    def generate_post(self, sf, page):
        for post in page:
            sf.get('post').set_attr_values(
                author=post.account_url,
                title=post.title,
                description=post.description,
                views=post.views,
                points=int(post.points),
                score=int(post.score),
                ups=int(post.ups),
                downs=int(post.downs),
                tags=[tag['name'] for tag in post.tags],
                nsfw=bool(post.nsfw)
            )

            if sf.get('post').should_scrape():
                yield ComponentLoader('post', {
                    'post_id': post.id,
                    'author': post.account_url,
                    'title': post.title,
                    'description': post.description,
                    'link': post.link,
                    'topic': post.topic,
                    'points': post.points,
                    'score': post.score,
                    'ups': post.ups,
                    'downs': post.downs,
                    'comment_count': post.comment_count,
                    'tags': ','.join([tag['name'] for tag in post.tags]),
                    'nsfw': post.nsfw
                })
            
            if sf.ret('skip_comments'):
                continue
            for comment in self.generate_comment(sf, post.id):
                yield comment

    def generate_comment(self, sf, post_id):

        for comment in self.imgur.gallery_item_comments(post_id):

            sf.get('comment').set_attr_values(
                body=comment.comment,
                author=comment.author,
                points=comment.points,
                ups=comment.ups,
                downs=comment.downs
            )
            
            if sf.get('comment').should_scrape():
                yield ComponentLoader('comment', {
                    'comment_id': comment.id,
                    'parent_id': comment.parent_id,
                    'body': comment.comment,
                    'author': comment.author,
                    'datetime': comment.datetime,
                    'deleted': comment.deleted,
                    'points': comment.points,
                    'vote': comment.vote,
                    'downs': comment.downs,
                    'ups': comment.ups,
                })
