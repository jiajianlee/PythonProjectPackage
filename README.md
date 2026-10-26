#运行时命令pyinstaller main.spec --noconfirm --clean。用spec来运行
#如果是全部从新开始则要用paddleorc官方脚本package.py先运行。
#运行官方脚本时,命令 uv run python package.py --file src/main.py --nvidia。成功后就可以用spec来运行，但是需要在spec中添加hiddenimports=[ 'chardet.models._format__mypyc']。
paddleorc-gpu是必须要用到nvidia的库，如果在UV环境中没装，则在C:\Users\user\AppData\Roaming\Python\Python311\site-packages\nvidia下将整个nvidia文件夹拷到打包中的_internal目录下
paddleorc只支持pyinstaller打包，不支持Nuikta打包


使用自己编写的基于嵌入式python的打包程序，执行的步骤如下：
1.现在embeddedPackage中添加congfig.py;download.py；package.py;PyStand.py
2.在config.py中修改相关配置，其中打包的文件夹及文件要和项目对应，例如PROJECT_PATH对应的是打包的文件夹，下面是入口.py文件。如果配置和项目中的文件路径不对应，则会提示错误
3.打包文件夹(src)下面必须是有一个总包文件夹（testpythonproject）（该文件夹底下必须有一个__init__.py）文件，必须有一个入口的.py文件（mainAA.py）
4.所有设置好了之后，需要在PyStand.py下着重查看入口的模块是否正确。
5.然后运行package.py文件
6.程序会在项目根目录下生成一个package-文件名称的文件夹。里面即是打包内容
7.不要更改package-文件名称的文件夹下的.pyd文件名称，不然会报模块无法找到的错误
8.在uv中添加依赖包的时候，如果只是开发用的，与发布无关的，用uv add 依赖包名 --dev。不然生成的Requirement.txt文档中会将这些包包含进去.
9.支持依赖包动态更新，在添加新包后，重新运行package.py，就会生成新的Requirement.txt。在运行打包好的程序，也会将新的依赖包添加进去