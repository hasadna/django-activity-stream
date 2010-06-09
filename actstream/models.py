from datetime import datetime
from operator import or_
from django.db import models
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince as timesince_
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from actstream.signals import action

class FollowManager(models.Manager):
    def stream_for_user(self, user):
        """
        Produces a QuerySet of most recent activities from actors the user follows
        """
        follows = self.filter(user=user)
        qs = (Action.objects.stream_for_actor(follow.actor) for follow in follows)
        if follows.count():
            return reduce(or_, qs).order_by('-timestamp')
    
class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(User)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() 
    actor = generic.GenericForeignKey()
    
    objects = FollowManager()
    
    def __unicode__(self):
        return u'%s -> %s' % (self.user, self.actor)

class ActionManager(models.Manager):
    def stream_for_actor(self, actor):
        """
        Produces a QuerySet of most recent activities for any actor
        """
        return self.filter(
            actor_content_type = ContentType.objects.get_for_model(actor),
            actor_object_id = actor.pk,
        ).order_by('-timestamp')
        
    def stream_for_model(self, model):
        """
        Produces a QuerySet of most recent activities for any model
        """
        return self.filter(
            target_content_type = ContentType.objects.get_for_model(model)
        ).order_by('-timestamp')
        
class Action(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional target). 
    Nomenclature based on http://martin.atkins.me.uk/specs/activitystreams/atomactivity
    
    Generalized Format::
    
        <actor> <verb> <time>
        <actor> <verb> <target> <time>
    
    Examples::
    
        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        
    Unicode Representation::
    
        justquick reached level 60 1 minute ago
        
    HTML Representation::
    
        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    actor_content_type = models.ForeignKey(ContentType,related_name='actor')
    actor_object_id = models.PositiveIntegerField() 
    actor = generic.GenericForeignKey('actor_content_type','actor_object_id')
    
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    
    target_content_type = models.ForeignKey(ContentType,related_name='target',blank=True,null=True)
    target_object_id = models.PositiveIntegerField(blank=True,null=True) 
    target = generic.GenericForeignKey('target_content_type','target_object_id')
    
    timestamp = models.DateTimeField(default=datetime.now)
    
    public = models.BooleanField(default=True)
    
    objects = ActionManager()
    
    def __unicode__(self):
        if self.target:
            return u'%s %s %s %s ago' % \
                (self.actor, self.verb, self.target, self.timesince())
        return u'%s %s %s ago' % (self.actor, self.verb, self.timesince())
        
    def actor_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current actor
        """
        return reverse('actstream_actor', None,
                       (self.actor_content_type.pk, self.actor_object_id))
        
    def target_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current target
        """        
        return reverse('actstream_actor', None,
                       (self.target_content_type.pk, self.target_object_id))
                
        
    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the current timestamp
        """
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return ('actstream.views.detail', [self.pk])
        

