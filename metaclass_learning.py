# coding: utf-8

import numbers


class Field:
    pass


class CharField(Field):
    # 数据描述符
    # 好处在于可以在各方法中校验传入值的合理性
    def __init__(self, col_name, max_length):
        if col_name is None or not isinstance(col_name, str):
            raise ValueError("col_name must be given as str")
        if max_length is None or not isinstance(max_length, numbers.Integral):
            raise ValueError("max_length must be given as int")
        self._col_name = col_name
        self._max_length = max_length

    def __get__(self, instance, owner):
        return instance.fields[self._col_name]

    def __set__(self, instance, value):
        # 这里如果col_name和数据描述符对应的名字一样的话,如name=CharField(col_name="name",10)
        # 用setattr(instance, self._col_name, value)即user.name=value会再次进入此__set__方法,导致无限递归
        instance.fields[self._col_name] = value


class IntField(Field):
    def __init__(self, col_name, min_length, max_length):
        self._col_name = col_name
        self._min_length = min_length
        self._max_length = max_length

    def __get__(self, instance, owner):
        return instance.fields[self._col_name]

    def __set__(self, instance, value):
        print(instance, value)
        if value is None or (not isinstance(value, numbers.Integral)):
            raise ValueError("value must be given as int")
        instance.fields[self._col_name] = value


class ModelMetaClass(type):
    def __new__(cls, cls_name, base_class, attrs):
        print('ModelMetaClass: {}, {}, {}'.format(cls_name, base_class, attrs))
        if cls_name == "Model":
            return super().__new__(cls, cls_name, base_class, attrs)
        fields = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields[k] = v
        attrs["fields"] = fields
        _meta = {}
        attrs_meta = attrs.get("Meta", None)
        if attrs_meta is not None and isinstance(attrs_meta, type):
            _meta["tb_name"] = getattr(attrs_meta, "tb_name", cls_name)
            del attrs["Meta"]
        else:
            _meta["tb_name"] = cls_name.lower()
        attrs["_meta"] = _meta
        return super().__new__(cls, cls_name, base_class, attrs)


class Model(metaclass=ModelMetaClass):
    def __init__(self, **kwargs):
        print('kwargs', kwargs)
        self.fields = {}
        for k, v in kwargs.items():
            setattr(self, k, v)
    # def more_func(self):
    #     pass


class User(Model):
    name = CharField(col_name="name", max_length=10)
    sex = CharField(col_name="sex", max_length=1)
    age = IntField(col_name="age", min_length=1, max_length=10)

    class Meta:
        tb_name = "User"


class Company(Model):
    name = CharField(col_name="name", max_length=10)
    address = CharField(col_name="address", max_length=1)

    # class Meta:
    #     tb_name = "Company"


if __name__ == "__main__":
    user = User(name="boy1", age=5, sex="男")
    user1 = User(name="girl1", age=6, sex="女")
    company = Company(name="com", address="China")
    print(User.__dict__)
    print(user.__dict__)
    print(user1.__dict__)
    print(Company.__dict__)
    print(company.__dict__)

