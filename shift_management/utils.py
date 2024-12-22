from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    def decorator(view_func):
        @user_passes_test(lambda user: user.groups.filter(name=group_name).exists())
        def wrapped_view(*args, **kwargs):
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator