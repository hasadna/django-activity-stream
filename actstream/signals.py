from datetime import datetime
from django.dispatch import Signal
from django.contrib.contenttypes.models import ContentType

action = Signal(providing_args=['actor', 'verb', 'target',
                                'description', 'timestamp'])

def action_handler(sender, verb, **kwargs):
    from actstream.models import Action

    target = kwargs.get('target', None)
    public = kwargs.get('public', True)
    description = kwargs.get('description', None)
    timestamp = kwargs.get('timestamp', datetime.now())
    action = Action(actor_content_type=ContentType.objects.get_for_model(sender),
                    actor_object_id=sender.pk,
                    verb=unicode(verb),
                    public=public,
                    timestamp = timestamp,
                    description = description)
    if target:
        action.target_object_id = target.pk
        action.target_content_type = ContentType.objects.get_for_model(target)

    action.save()
action.connect(action_handler, dispatch_uid="actstream.models")
