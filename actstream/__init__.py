from django.contrib.contenttypes.models import ContentType
from signals import action
from models import Follow, Action

__version__ = '0.2'

def follow(user, actor, send_action=True):
    """
    Creates a ``User`` -> ``Actor`` follow relationship such that the actor's activities appear in the user's stream.
    Also sends the ``<user> started following <actor>`` action signal.
    Returns the created ``Follow`` instance
    
    Syntax::
    
        follow(<user>, <actor>)
    
    Example::
    
        follow(request.user, group)
    
    """
    ret_val, created = Follow.objects.get_or_create(user = user, object_id = actor.pk,
        content_type = ContentType.objects.get_for_model(actor))
    if created and send_action:
        action.send(user, verb='started following', target=actor)
    return ret_val
    
def unfollow(user, actor, send_action=False):
    """
    Removes ``User`` -> ``Actor`` follow relationship. 
    Optionally sends the ``<user> stopped following <actor>`` action signal.
    
    Syntax::
    
        unfollow(<user>, <actor>)
    
    Example::
    
        unfollow(request.user, other_user)
    
    """
    Follow.objects.filter(user = user, object_id = actor.pk, 
        content_type = ContentType.objects.get_for_model(actor)).delete()
    if send_action:
        action.send(user, verb='stopped following', target=actor)
    
def actor_stream(actor):
    return Action.objects.stream_for_actor(actor)
actor_stream.__doc__ = Action.objects.stream_for_actor.__doc__
    
def user_stream(user):
    return Follow.objects.stream_for_user(user)
user_stream.__doc__ = Follow.objects.stream_for_user.__doc__
    
def model_stream(model):
    return Action.objects.stream_for_model(model)
model_stream.__doc__ = Action.objects.stream_for_model.__doc__

