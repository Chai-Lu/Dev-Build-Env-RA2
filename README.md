# Dev-Build-Env-RA2
自用的较为便捷的Mod配置操作Tools

# Symlink Make
创建硬链接使得在检索文件时更便捷

"#Symlink.py"
Using symlink.ini 作为配置文件
Before Use 需要管理员权限
import os,sys,ctypes,msvcrt,configparser,re

其配置内容为：
```ini
[Path]
#作为当AutoCreat不启用时的处理行为
Files=""
#处理文件所在路径（绝对）
ExName=xml,ini
#检测文件类型（以,为分隔符）
Output=""
#生成链接放置的路径，当为空或者不存在时默认为Py所在路径
[AutoCreat]
#自动创建某文件类型的文件和链接
Files=""
#文件所在路径（绝对）
ExName=ini
#文件的类型
Output=
##生成链接放置的路径，当为空或者不存在时默认为Py所在路径
BeWrite=
#预填充文字利用/n作为换行符 可为空
Use=1
#赋值为1时自动创建类型，为0时非创建文件类型
Name=
#所创建文件的名称
```

#Spawn Test

便于更方便的测试
Using Path.in 作为配置文件
Before Use 确认有Syinge.exe
import os,shutil,subprocess,time,configparser,psutil,msvcrt

其配置内容为：
```ini
[Ext]
ClientPath=""
#指向gamemd.exe所在路径
```

