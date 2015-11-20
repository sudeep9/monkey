import sys
from types import MethodType, ModuleType, FunctionType, InstanceType, ClassType

class Dummy: pass

class Patcher:
    def __init__(self, entity):
        self.ent_type = None
        self.entity = entity
        self.__determine_type()

    def __determine_type(self):
        if isinstance(self.entity, ClassType):
            self.ent_type = 'C'
        elif isinstance(self.entity, InstanceType):
            self.ent_type = 'I'
        elif isinstance(self.entity, ModuleType):
            self.ent_type = 'M'
        else:
            raise Exception("Un-supported entity type %s" % type(self.entity))


    def patch_class(self, old_class, new_class):
        if self.ent_type != 'M':
            raise Exception("Entity should be a module for patching a class")


class ModulePatcher:
    def __init__(self, module):
        self.module = module
        self.patched = []

    def __patch_class(self, old_class, new_class, name):
        class_name = name
        setattr(self.module, class_name + '_', old_class)
        setattr(self.module, class_name , new_class)

    def patch_class(self, old_class, new_class):
        name = old_class.__name__
        self.__patch_class(old_class, new_class, name)
        self.patched.append(('C', name))

    def __patch_function(self, old_func, new_func, old_name):
        func_name = old_name
        self.module.__dict__[func_name + '_'] = old_func
        self.module.__dict__[func_name ] = new_func

    def patch_function(self, old_func, new_func):
        func_name = old_func.__name__
        self.__patch_function(old_func, new_func, func_name)
        self.patched.append(('F', func_name))

    def rollback(self):
        for objtype, name in self.patched:
            if objtype == 'F':
                self.rollback_function(name)
            elif objtype == 'C':
                self.rollback_class(name)

    def rollback_function(self, name):
        new_func = getattr(self.module, name)
        old_func = getattr(self.module, name + '_')
        self.__patch_function(new_func, old_func, name)

    def rollback_class(self, name):
        new_class = getattr(self.module, name)
        old_class = getattr(self.module, name + '_')
        self.__patch_class(new_class, old_class, name)

class ClassPatcher:
    def __init__(self, cls):
        self.cls = cls

    def patch_method(self, old_func, new_func):
        func_name = old_func.__name__
        setattr(self.cls, func_name + '_', old_func)
        setattr(self.cls, func_name, MethodType(new_func, None, self.cls))

    def patch_classmethod(self, old_func, new_func):
        func_name = old_func.__name__
        setattr(self.cls, func_name + '_', old_func)
        setattr(self.cls, func_name, MethodType(new_func, self.cls))


    def patch_ctor(self, new_func):
        self.patch_method(self.cls.__init__, new_func)

    def patch_ctor_empty(self):
        def empty(self, *args, **kargs): pass

        self.patch_ctor(empty)

    def patch_method_empty(self, old_func):
        def empty(self, *args, **kargs): pass
        
        self.patch_classmethod(old_func, MethodType(empty, self.cls))

    def add_method_empty(self, func_name):
        def empty(self, *args, **kargs): pass
        setattr(self.cls, func_name, MethodType(empty, None,  self.cls))

    def add_function(self, func_name, func):
        setattr(self.cls, func_name, MethodType(func, None, self.cls))



class ObjectPatcher:
    def __init__(self, obj):
        self.obj = obj

    def patch_method(self, old_func, new_func):
        func_name = old_func.__name__
        setattr(self.obj, func_name + '_', old_func)
        setattr(self.obj, func_name, MethodType(new_func, self.obj))

    def patch_method_empty(self, old_func):
        def empty(self, *args, **kargs): pass
        self.patch_method(old_func, empty)

    def add_method_empty(self, func_name):
        def empty(self, *args, **kargs): pass
        setattr(self.obj, func_name, empty)

def multi_setattr(obj, attr_str, value):
    var_list = attr_str.split('.')
    prev_dummy = None

    for var_name in var_list[:-1]:
        dummy = Dummy()

        if prev_dummy:
            if not hasattr(prev_dummy, var_name):
                setattr(prev_dummy, var_name, dummy)
                prev_dummy = dummy
            else:
                prev_dummy = getattr(prev_dummy, var_name)
        else:
            if not hasattr(obj, var_name):
                setattr(obj, var_name, dummy)
                prev_dummy = dummy
            else:
                prev_dummy = getattr(obj, var_name)

    setattr(prev_dummy, var_list[-1], value)


def multi_setattr_empty_function(obj, attr_str):
    def empty(self, *args, **kargs): pass
    multi_setattr(obj, attr_str, MethodType(empty, obj))

def create_function(rpc, attr_str, value):
    multi_setattr(rpc, attr_str, MethodType(value, rpc))


#def patch_module_function(module, old_func, new_func):
#    func_name = old_func.__name__
#    module.__dict__[func_name + '_'] = old_func
#    module.__dict__[func_name ] = new_func
#
#
#def patch_instance_method(obj, old_func, new_func):
#    func_name = old_func.__name__
#    setattr(obj, func_name + '_', old_func)
#    setattr(obj, func_name, MethodType(new_func, obj))
#
#
#def patch_class_method(cls, old_func, new_func):
#    func_name = old_func.__name__
#    setattr(cls, func_name + '_', old_func)
#    setattr(cls, func_name, new_func)
#
#
#def patch_module_class(module, old_class, new_class):
#    class_name = old_class.__name__
#    setattr(module, class_name + '_', old_class)
#    setattr(module, class_name , new_class)



if __name__ == "__main__":




    def my_add(a,b):
        return a*b

    class MyPerson:
        def __init__(self):
            print "orig ctor"
            self.name = "B"

        def __getattr__(self, name):
            return 1

        def greet(self):
            print type(self)
            print "Hello", self.name

    def g(self, name):
        return 2

    pt = ClassPatcher(MyPerson)
    #pt.add_function('__getattr__', g)
    p = MyPerson()
    print p.abc
    p.greet()
        

    exit(0)

    def test_mod():
        print mod.add(10,20)
        p = mod.Person()
        p.greet()
        print "-" * 10

    mp = ModulePatcher(mod)
    mp.patch_function(mod.add, my_add)
    mp.patch_class(mod.Person, MyPerson)

    test_mod()

    mp.rollback()
    test_mod()

    mp.rollback()
    test_mod()
