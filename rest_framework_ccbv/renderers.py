
import json

from inspector import Inspector
from jinja_utils import templateEnv
from config import REST_FRAMEWORK_VERSIONS, VERSION, BASE_URL
from itertools import ifilter


class BasePageRenderer(object):

    def __init__(self, klasses):
        self.klasses = klasses

    def render(self, filename):
        template = templateEnv.get_template(self.template_name)
        context = self.get_context()
        with open(filename, 'w') as f:
            f.write(template.render(context).encode("UTF-8"))

    def get_context(self):
        other_versions = list(REST_FRAMEWORK_VERSIONS)
        other_versions.remove(VERSION)
        return {
            'version_prefix': 'Django REST Framework',
            'version': VERSION,
            'versions': REST_FRAMEWORK_VERSIONS,
            'other_versions': other_versions,
            'klasses': self.klasses}


class DetailPageRenderer(BasePageRenderer):
    template_name = 'detail_view.html'

    def __init__(self, klasses, klass, module):
        super(DetailPageRenderer, self).__init__(klasses)
        self.klass = klass
        self.module = module
        self.inspector = Inspector(self.klass, self.module)

    def get_context(self):
        context = super(DetailPageRenderer, self).get_context()
        available_versions = self.inspector.get_available_versions()

        context['other_versions'] = [
            version
            for version in context['other_versions']
            if version in available_versions]
        context['name'] = self.klass
        context['ancestors'] = self.inspector.get_klass_mro()
        context['direct_ancestors'] = self.inspector.get_direct_ancestors()
        context['attributes'] = self.inspector.get_attributes()
        context['methods'] = self.inspector.get_methods()

        context['this_klass'] = next(
            ifilter(lambda x: x.__name__ == self.klass, self.klasses))

        context['children'] = self.inspector.get_children()
        context['this_module'] = context['this_klass'].__module__
        context['unavailable_methods'] = self.inspector.get_unavailable_methods()
        return context


class IndexPageRenderer(BasePageRenderer):
    template_name = 'index.html'


class LandPageRenderer(BasePageRenderer):
    template_name = 'home.html'


class ErrorPageRenderer(BasePageRenderer):
    template_name = 'error.html'


class SitemapRenderer(BasePageRenderer):
    template_name = 'sitemap.xml'

    def get_context(self):
        context = {}
        with open('.klasses.json', 'r') as f:
            klasses = json.loads(f.read())

        context['klasses'] = klasses
        context['latest_version'] = REST_FRAMEWORK_VERSIONS[-1]
        context['base_url'] = BASE_URL
        return context
