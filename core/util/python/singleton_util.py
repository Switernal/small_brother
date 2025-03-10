__doc__='单例模式'
__author__='Li Qingyun'
__date__='2025-03-07'


def Singleton(cls):
    """
    单例模式修饰类, 用这个来修饰需要单例模式的类
    :param cls: 类型
    :return:
    """
    # 创建一个字典用来保存被装饰类的实例对象
    _instance = {}

    def _singleton(*args, **kwargs):
        # 判断这个类有没有创建过对象，没有新创建一个，有则返回之前创建的
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton