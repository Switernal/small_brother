from .const import ExtensionType

from .impl import proxy

from .impl.proxy import *  # 暴露 impl/proxy 下的所有内容
# from .impl.proxy.impl.mihomo import *  # 暴露 impl/proxy 下的所有内容

from .interface import Extension