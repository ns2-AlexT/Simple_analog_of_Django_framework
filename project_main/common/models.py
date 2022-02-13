from copy import deepcopy
from quopri import decodestring
from sqlite3 import connect
from common.ouw import DomainObject


class User:
    def __init__(self, name):
        self.name = name


class Student(User, DomainObject):
    def __init__(self, name):
        self.list_of_courses = []
        super().__init__(name)


class Lecturer(User):
    pass


class FactoryUser:
    type_of_user = {
        'student': Student,
        'lecturer': Lecturer,
    }

    @classmethod
    def create_user(cls, type_of_user, name):
        return cls.type_of_user[type_of_user](name)


class Category(DomainObject):
    # id = 0

    def __init__(self, id, name_of_category, main_category):
        self.id = id
        # Category.id += 1
        self.name_of_category = name_of_category
        self.main_category = main_category
        self.list_of_courses_in_category = []

    def get_count_of_courses_in_category(self):
        count_courses_in_category = len(self.list_of_courses_in_category)
        return count_courses_in_category

    def get_list_subcategories(self, sub_category):
        sub_list = []
        while sub_category.main_category:
            sub_list.insert(0, sub_category)
            sub_list.insert(0, sub_category.main_category)
            sub_category = sub_category.main_category
        return sub_list


class CoursePrototype:
    def clone_course(self):
        return deepcopy(self)


class Course(CoursePrototype):
    def __init__(self, name_of_course, category_of_course):
        self.name_of_course = name_of_course
        self.category_of_course = category_of_course
        self.category_of_course.list_of_courses_in_category.append(self)
        self.list_of_students = []
        super().__init__()

    def __getitem__(self, item):
        return self.list_of_students[item]

    def add_student(self, student: Student):
        self.list_of_students.append(student)
        student.list_of_courses.append(self)


class RecordCourse(Course):
    pass


class OfflineCourse(Course):
    pass


class OnlineCourse(Course):
    pass


class FactoryCourses:
    type_of_course = {
        'record': RecordCourse,
        'offline': OfflineCourse,
        'online': OnlineCourse,
    }

    @classmethod
    def create_course(cls, type_of_course, name_of_course, category_of_course):
        return cls.type_of_course[type_of_course](name_of_course, category_of_course)


class CommonEngine:
    def __init__(self):
        self.student = []
        self.category = []
        self.courses = []

    @staticmethod
    def create_user(type_of_user, name):
        return FactoryUser.create_user(type_of_user, name)

    @staticmethod
    def create_category(name_of_category, main_category=None):
        return Category(id, name_of_category, main_category)

    @staticmethod
    def create_course(type_of_course, name_of_course, category_of_course):
        return FactoryCourses.create_course(type_of_course, name_of_course, category_of_course)

    def find_category_by_id(self, current_category_id):
        for idx in self.category:
            if idx.id == int(current_category_id):
                return idx
        raise Exception(f'Was no found category with id = {current_category_id}')

    def find_course_by_name(self, current_course_name):
        for idx in self.courses:
            if idx.name_of_course == current_course_name:
                return idx
        raise Exception(f'Was no found course with name = {current_course_name}')

    def fill_categories_sub(self):
        list_sub = []
        for item in self.category:
            result = item.get_list_subcategories(item)
            if result:
                list_sub.append(result)
            else:
                try:
                    list_sub.append([item])
                except Exception:
                    pass
        return list_sub

    @staticmethod
    def fill_categories_sub_db(some_object):
        list_sub = []
        for item in some_object:
            result = item.get_list_subcategories(item)
            if result:
                list_sub.append(result)
            else:
                try:
                    list_sub.append([item])
                except Exception:
                    pass
        return list_sub

    def find_student_by_name(self, current_student_name):
        for idx in self.student:
            if idx.name == current_student_name:
                return idx
        raise Exception(f'Was no found student with name = {current_student_name}')

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, ):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('Add log:\n', text)


class StudentMapper:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.current_table = 'student'

    def find_all(self):
        stat_request = f'SELECT * FROM {self.current_table}'
        self.cursor.execute(stat_request)
        res_of_request = []
        for item in self.cursor.fetchall():
            id, name = item
            make_instance = Student(name)
            make_instance.id = id
            res_of_request.append(make_instance)
        return res_of_request

    def find_by_id(self, id):
        stat_request = f'SELECT id, name FROM {self.current_table} WHERE id=?'
        self.cursor.execute(stat_request, (id,))
        res_of_request = self.cursor.fetchone()
        if res_of_request:
            return Student(*res_of_request)

    def insert(self, some_object):
        stat_request = f'INSERT INTO {self.current_table} (name) VALUES (?)'
        self.cursor.execute(stat_request, (some_object.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitError(e.args)

    def update(self, some_object):
        statement = f"UPDATE {self.current_table} SET name=? WHERE id=?"
        self.cursor.execute(statement, (some_object.name, some_object.id))
        try:
            self.connection.commit()
        except Exception as e:
            pass

    def delete(self, some_object):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (some_object.id,))
        try:
            self.connection.commit()
        except Exception as e:
            pass


class CategoryMapper:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.current_table = 'category'

    def find_all(self):
        stat_request = f'SELECT * FROM {self.current_table}'
        self.cursor.execute(stat_request)
        res_of_request = []
        for item in self.cursor.fetchall():
            id, name, cat = item
            make_instance = Category(id, name, None)
            make_instance.id = id
            res_of_request.append(make_instance)
        return res_of_request

    def find_by_id(self, id):
        stat_request = f'SELECT id, name_of_category, main_category FROM {self.current_table} WHERE id=?'
        self.cursor.execute(stat_request, (id,))
        res_of_request = self.cursor.fetchone()
        if res_of_request:
            return Category(*res_of_request)

    def insert(self, some_object):
        stat_request = f'INSERT INTO {self.current_table} (name_of_category) VALUES (?)'
        self.cursor.execute(stat_request, (some_object.name_of_category,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitError(e.args)



connection = connect('db_local.sqlite')


class MapperRegistries:
    mappers = {
        'student': StudentMapper,
        'category': CategoryMapper,
    }

    @staticmethod
    def get_mapper(some_object):
        if isinstance(some_object, Student):
            return StudentMapper(connection)
        elif isinstance(some_object, Category):
            return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name_of_current_mapper):
        return MapperRegistries.mappers[name_of_current_mapper](connection)


class DbCommitError(Exception):
    def __init__(self, request):
        super().__init__(f'Db commit error: {request}')
