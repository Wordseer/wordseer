from app import app
from inflect import engine as inflect_engine

inflect = inflect_engine()

def register_rest_view(view, blueprint, endpoint, name, parents=[], pk='',
    pk_type='int'):
    view_func = view.as_view(endpoint)

    if pk == '':
        pk = '%s_id' % name

    url = '/%s/' % inflect.plural(name)

    if parents and isinstance(parents, list):
        for parent in parents:

            parent_pk  = '%s_id' % parent
            parent_url = '/%s/' % inflect.plural(parent)
            list_url = '%s<%s:%s>%s' % (parent_url, pk_type, parent_pk, url)
            blueprint.add_url_rule(
                list_url,
                defaults={pk: None},
                view_func=view_func,
                methods=['GET',]
            )
            blueprint.add_url_rule('%s<%s:%s>%s<%s:%s>' %
                (parent_url, pk_type, parent_pk, url, pk_type, pk),
                view_func=view_func,
                methods=['GET', 'PUT', 'DELETE'])

    blueprint.add_url_rule(url, defaults={pk: None},
             view_func=view_func, methods=['GET',])
    blueprint.add_url_rule(url, view_func=view_func, methods=['POST',])
    blueprint.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
             methods=['GET', 'PUT', 'DELETE'])