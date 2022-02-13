from jsonpickle import dumps, loads

from framework.templator import render


class TemplateView:
    template = 'template.html'

    def get_context(self):
        return {}

    def get_template(self):
        return self.template

    def render_template_and_context(self):
        current_template = self.get_template()
        current_context = self.get_context()
        return '200 OK', render(current_template, **current_context)

    def __call__(self, request):
        print(f'+++{self.__class__}')
        print(f'+++{dir(self)}')
        return self.render_template_and_context()


class ListView(TemplateView):
    list_queryset = []
    template = 'list.html'
    list_context_name = 'list_context'

    def get_queryset(self):
        print(self.list_queryset)
        return self.list_queryset

    def get_list_context_name(self):
        return self.list_context_name

    def get_context(self):
        current_list_queryset = self.get_queryset()
        current_list_context_name = self.get_list_context_name()
        context = {current_list_context_name: current_list_queryset}
        return context


class CreateView(TemplateView):
    template = 'create.html'

    @staticmethod
    def get_request_details(request):
        return request['param of request']

    def create_some_object(self, data_of_object):
        pass

    def __call__(self, request_data):
        if request_data['method of request'] == 'POST':
            request_data = self.get_request_details(request_data)
            self.create_some_object(request_data)
            return self.render_template_and_context()
        else:
            return super().__call__(request_data)


"""
State keeper pattern
"""


class StateKeeper:
    def __init__(self, some_instance):
        self.instance = some_instance

    def save(self):
        return dumps(self.instance)

    @staticmethod
    def load(data):
        return loads(data)
