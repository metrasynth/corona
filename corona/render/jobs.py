from django_rq import job


@job('render')
def render_sunvox_to_wav():
    pass
