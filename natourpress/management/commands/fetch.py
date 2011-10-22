# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from natourpress.models import Feed, Atom, Update, FeedImage, Tag, Post, Media, Link
import feedparser, time, datetime
import socket

def maketime(ttime):
    return datetime.datetime.fromtimestamp(time.mktime(ttime))

class SaveEntry:
    def __init__(self, feed, entry, postdict, frep):
        self.feed = feed
        self.entry = entry
        self.postdict = postdict
        self.frep = frep

    def get_tags(self):
        fcat = []
        if self.entry.has_key('tags'):
            for tcat in self.entry.tags:
                if tcat.label != None:
                    term = tcat.label
                else:
                    term = tcat.term
                qcat = term.strip()
                if ',' in qcat or '/' in qcat:
                    qcat = qcat.replace(',', '/').split('/')
                else:
                    qcat = [qcat]
                for zcat in qcat:
                    tagname = zcat.lower()
                    while '  ' in tagname:
                        tagname = tagname.replace('  ', ' ')
                    tagname = tagname.strip()
                    if not tagname or tagname == ' ':
                        continue
                    if not Tag.objects.filter(name=tagname):
                        cobj = Tag(name=tagname)
                        cobj.save()
                    fcat.append(Tag.objects.get(name=tagname))
        return fcat

    def get_entry_data(self):
        """ Retrieves data from a post and returns it in a tuple.
        """
        try:
            link = self.entry.link
        except AttributeError:
            link = self.feed.link
        try:
            title = self.entry.title
        except AttributeError:
            title = link
        guid = self.entry.get('id', title)

        if self.entry.has_key('author_detail'):
            author = self.entry.author_detail.get('name', '')
            author_email = self.entry.author_detail.get('email', '')
        else:
            author, author_email = '', ''

        if not author:
            author = self.entry.get('author', self.entry.get('creator', ''))
        
        try:
            content = self.entry.content[0].value
        except:
            content = self.entry.get('summary',
                                     self.entry.get('description', ''))
        
        if self.entry.has_key('modified_parsed'):
            date_modified = maketime(self.entry.modified_parsed)
        else:
            date_modified = None

        fcat = self.get_tags()
        comments = self.entry.get('comments', '')
        description = self.entry.get('description','')

        return (link, title, guid, author, author_email, content, 
                date_modified, fcat, comments,description[0:250])

    def savePost(self):
        """ Process a post in a feed and saves it in the DB if necessary.
        """

        (link, title, guid, author, author_email, content, date_modified,
         fcat, comments,description) = self.get_entry_data()
        
        if guid in self.postdict:
            tobj = self.postdict[guid]
            if tobj.content != content or (date_modified and
                    tobj.date_modified != date_modified):
                if not date_modified:
                    date_modified = tobj.date_modified
                tobj.title = title
                tobj.link = link
                tobj.content = content
                tobj.guid = guid
                tobj.date_modified = date_modified
                tobj.author = author
                tobj.author_email = author_email
                tobj.comments = comments
                tobj.description = description
                tobj.tags.clear()
                [tobj.tags.add(tcat) for tcat in fcat]
                tobj.save()
        else:
            if not date_modified and self.frep:
                # if the feed has no date_modified info, we use the feed
                # mtime or the current time
                if self.frep.feed.has_key('modified_parsed'):
                    date_modified = maketime(self.frp.feed.modified_parsed)
                elif self.frep.has_key('modified'):
                    date_modified = maketime(self.fpf.modified)
                else:
                    date_modified = datetime.datetime.now()
            tobj = Post(feed=self.feed, title=title, link=link,
                content=content, guid=guid, date_modified=date_modified,
                author=author, author_email=author_email,
                comments=comments, description=description)
            tobj.save()
            [tobj.tags.add(tcat) for tcat in fcat]
            

def savefeed(frep,djangofeed):
    if hasattr(frep, 'status'):
        if frep.status == 304:
	# feed is unchanged. No point in saving it
            return
        if frep.status >= 400:
            print "HTTP ERROR %d in feed %s" % (frep.status, frep.feed_url)
            return
    #At this point we can save the feed in our django database    
#    print frep.feed.get('description')
    djangofeed.etag = frep.get('etag', '')
    try:
        djangofeed.last_modified = maketime(frep.modified)
    except:
        pass

    djangofeed.title = frep.feed.get('title', '')[0:200]
    djangofeed.description = frep.feed.get('description', '')[0:250]
    djangofeed.link = frep.feed.get('link', '')
    djangofeed.last_checked = datetime.datetime.now()
    djangofeed.language = frep.feed.get('language','')[0:10]
    djangofeed.ttl = frep.feed.get('ttl',15)
    
#    djangofeed.save()
    guids = []
    for entry in frep.entries:
        if entry.get('id', ''):
            guids.append(entry.get('id', ''))
        elif entry.title:
            guids.append(entry.title)
        elif entry.link:
            guids.append(entry.link)

    djangofeed.save()

    if guids:
        postdict = dict([(post.guid, post)
            for post in Post.objects.filter(feed=djangofeed.id).filter(guid__in=guids)])
    else:
        postdict = {}

    for entry in frep.entries:
        entry = SaveEntry(djangofeed, entry, postdict, frep)
        entry.savePost()
    djangofeed.save()
 
def main():
    socket.setdefaulttimeout(10)
    feed_objects = Feed.objects.all();

    for feed in feed_objects:
        try:
            frep = feedparser.parse(feed.feed_url,etag=feed.etag)
        except:
            print('! ERROR: feed cannot be parsed')
            return
        savefeed(frep,feed)

if __name__ == "__main__":
    main()    


######################################################################################################
class Command(BaseCommand):
    """ """
    help = "Fetch info from feeds"
    requires_model_validation = True

    #=================================================================================================
    def handle(self, *app_labels, **options):
        """ """
        main()
