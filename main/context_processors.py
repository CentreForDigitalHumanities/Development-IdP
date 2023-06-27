from django.conf import settings


def hosted(request):
    """
    Returns if the app is set to hosted mode
    """
    context_extras = {}
    if hasattr(settings, 'HOSTED'):
        context_extras['hosted'] = settings.HOSTED
    else:
        context_extras['hosted'] = False

    return context_extras