from quopri import decodestring

from common.ouw import UnitOfWork
from framework.templator import render
from common.models import CommonEngine, Logger, MapperRegistries
from common.decorators import Routes, Debug
from common.cbv import ListView, CreateView, StateKeeper

common_engine = CommonEngine()
logger = Logger('views')
routes = {}

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistries)

"""
Realize PC pattern in all classes below
"""


@Routes(routes=routes, url='/')
class Index:
    @Debug()
    def __call__(self, request):
        # print(common_engine.student)
        # pprint(common_engine.category)
        # for idx in common_engine.category:
        #     print(idx)
        # pprint(common_engine.courses)
        # for idx in common_engine.courses:
        #     print(idx)
        print(routes)

        return '200 ', render('index.html', active_class='index', list_of_category=common_engine.category)


@Routes(routes=routes, url='/about/')
class About:
    @Debug()
    def __call__(self, request):
        return '200 ', render('about.html', active_class='about')


@Routes(routes=routes, url='/auth/')
class Auth:
    @Debug()
    def __call__(self, request):
        return '200 ', render('auth.html', active_class='auth')


@Routes(routes=routes, url='/contacts/')
class Contact:
    @Debug()
    def __call__(self, request):
        return '200 ', render('contacts.html', active_class='contact')


@Routes(routes=routes, url='/desc_of_course/')
class DescOfCourse:
    @Debug()
    def __call__(self, request):
        return '200 ', render('desc_of_course.html')


class PageNotFound:
    @Debug()
    def __call__(self, request):
        print(request)
        return '404 ', render('pnf_404.html')


@Routes(routes=routes, url='/create-category/')
class CreateCategory:
    sub_cat_id = None

    @Debug()
    def __call__(self, request):
        logger.log('creating a new category')
        logger.log(f'From views {self} ===>>> {request}')
        if request['method of request'] == 'POST':
            temp_val = request['param of request']
            if temp_val.get('category_id'):
                logger.log(f'Category {temp_val["name"]} already exist.')
            else:
                new_category = common_engine.create_category(temp_val['name'], temp_val.get('category_id'))
                common_engine.category.append(new_category)
                new_category.mark_new()
                UnitOfWork.get_current().commit()
                if self.sub_cat_id is not None:
                    sub_category = common_engine.find_category_by_id(self.sub_cat_id)
                    sub_category.main_category = new_category
                    self.sub_cat_id = None
            return '200 ', render('list_of_categories.html', list_of_category=common_engine.fill_categories_sub())
        else:
            try:
                if request['param of request']['main']:
                    self.sub_cat_id = request['param of request']['cat']
            except Exception:
                pass
            return '200 ', render('create-category.html', list_of_category=common_engine.category)


@Routes(routes=routes, url='/create-course/')
class CreateCourse:
    set_id_for_category = -1

    @Debug()
    def __call__(self, request):
        logger.log('creating a new course')
        logger.log(f'From views {self} ===>>> {request}')
        logger.log(self.set_id_for_category)
        if request['method of request'] == 'POST':
            current_category = common_engine.find_category_by_id(self.set_id_for_category)
            current_course = common_engine.create_course(request['param of request']['type_of_course'],
                                                         request['param of request']['name'],
                                                         current_category)
            common_engine.courses.append(current_course)
            return '200 ', render('desc_of_category.html', category=current_category)
        else:
            self.set_id_for_category = int(request['param of request']['id'])
            current_category = common_engine.find_category_by_id(self.set_id_for_category)
            return '200 ', render('create-course.html', category=current_category)


@Routes(routes=routes, url='/copy-course/')
class CopyCourse:
    @Debug()
    def __call__(self, request):
        Logger.log(f'From views {self} ===>>> {request}')
        current_name_of_course = decode_value(request['param of request']['name_of_course'])
        current_course = common_engine.find_course_by_name(current_name_of_course)
        if current_course:
            new_course = current_course.clone_course()
            new_course.name_of_course = f'CLONE_{current_name_of_course}'
            current_category = common_engine.find_category_by_id(current_course.category_of_course.id)
            common_engine.courses.append(new_course)
            current_category.list_of_courses_in_category.append(new_course)
        return '200 ', render('desc_of_category.html', category=current_category)


@Routes(routes=routes, url='/list_of_categories/')
class ListOfCategories:
    @Debug()
    def __call__(self, request):
        Logger.log(f'From views {self} ===>>> {request}')
        # return '200 ', render('list_of_categories.html', list_of_category=common_engine.fill_categories_sub())
        get_current_mapper = MapperRegistries.get_current_mapper('category')
        list_cat = get_current_mapper.find_all()
        return '200 ', render('list_of_categories.html', list_of_category=common_engine.fill_categories_sub_db(
            list_cat))


@Routes(routes=routes, url='/desc_of_category/')
class DescOfCategory:
    @Debug()
    def __call__(self, request):
        Logger.log(f'From views {self} ===>>> {request}')
        if request['method of request'] == 'GET':
            get_current_mapper = MapperRegistries.get_current_mapper('category')
            current_category = get_current_mapper.find_by_id(request['param of request']['id'])
            # current_category = common_engine.find_category_by_id(request['param of request']['id'])
            return '200 ', render('desc_of_category.html', category=current_category)


"""
Realize CBV pattern
"""


@Routes(routes=routes, url='/list-students/')
class ListStudentView(ListView):
    # list_queryset = common_engine.student
    template = 'list-of-students.html'

    def get_queryset(self):
        get_current_mapper = MapperRegistries.get_current_mapper('student')
        return get_current_mapper.find_all()


@Routes(routes=routes, url='/create-student/')
class CreateStudentView(CreateView):
    template = 'create-student.html'

    def create_some_object(self, data_of_object: dict):
        name_of_object = data_of_object['name']
        # current_name = common_engine.decode_value(name_of_object)
        new_object = common_engine.create_user('student', name_of_object)
        common_engine.student.append(new_object)
        new_object.mark_new()
        UnitOfWork.get_current().commit()


@Routes(routes=routes, url='/add-student/')
class AddStudentCourse(CreateView):
    template = 'add-student-to-course.html'

    def get_context(self):
        context = super().get_context()
        context['list_of_students'] = common_engine.student
        context['list_of_courses'] = common_engine.courses
        print(f'len of courses {len(context["list_of_courses"])}')
        return context

    def create_some_object(self, data_of_object):
        course = data_of_object['course_name']
        student = data_of_object['student_name']
        current_course = common_engine.find_course_by_name(course)
        current_student = common_engine.find_student_by_name(student)
        current_course.add_student(current_student)


@Routes(routes=routes, url='/save-api/')
class SaveApi:
    def __call__(self, request):
        if request['param of request']['type'] == 'save_students':
            some_instance = common_engine.student
        return '200 ', StateKeeper(some_instance).save()


"""
Decode cyrillic symbols
"""


def decode_value(val):
    val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
    val_decode_str = decodestring(val_b)
    return val_decode_str.decode('UTF-8')
