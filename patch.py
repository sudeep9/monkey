import sys
from types import MethodType, ModuleType, FunctionType, InstanceType, ClassType

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

    def patch_function(self, old_func, new_func):
        func_name = old_func.__name__
        setattr(self.cls, func_name + '_', old_func)
        setattr(self.cls, func_name, MethodType(new_func, self.cls))

    def patch_classmethod(cls, old_func, new_func):
        func_name = old_func.__name__
        setattr(cls, func_name + '_', old_func)
        setattr(cls, func_name, new_func)

class ObjectPatcher:
    def __init__(self, obj):
        self.obj = obj

    def patch_function(self, old_func, new_func):
        func_name = old_func.__name__
        setattr(self.obj, func_name + '_', old_func)
        setattr(self.obj, func_name, MethodType(new_func, self.obj))

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


    import mod


    def my_add(a,b):
        return a*b

    class MyPerson:
        def __init__(self):
            self.name = "B"

        def greet(self):
            print "Hello", self.name

    p = MyPerson()
    plist = [Patcher(mod), Patcher(MyPerson), Patcher(p)]

        

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
