# 1.使用步骤：
使用pythonProjectPackage打包程序，执行的步骤如下：
- 1.下载embeddedPackage文件夹下所有文件，并将embeddedPackage文件夹放在项目根目录下；
- 2.在config.py中修改相关配置，其中打包的文件夹及文件要和项目对应，例如PROJECT_PATH对应的是打包的文件夹，下面是入口.py文件。如果配置和项目中的文件路径不对应，则会提示错误
- 3.所有设置好了之后，需要在PyStand.py下着重查看入口的模块是否正确。
- 4.然后运行package.py文件
- 5.程序会在项目根目录下生成一个package-文件名称的文件夹。里面即是打包内容


# 2.注意事项：
- 1.打包文件夹(src)下面必须有一个总包文件夹（testpythonproject）（该文件夹底下必须有一个__init__.py）文件，必须有一个入口的.py文件（mainAA.py）
- 2.不要更改package-文件名称的文件夹下的.pyd文件名称，不然会报模块无法找到的错误
- 3.在uv中添加依赖包的时候，如果只是开发用的，与发布无关的，用uv add 依赖包名 --dev。不然生成的Requirement.txt文档中会将这些包包含进去.
- 4.支持依赖包动态更新，在添加新包后，重新运行package.py，就会生成新的Requirement.txt。在运行打包好的程序，也会将新的依赖包添加进去
- 5.此文件需项目是UV配置的虚拟环境，必须添加nuitka依赖包
- 6.项目的依赖文件，例如PyStand.exe或者嵌入式Python，或者是get-pip.py均可以在packageBaseFile文件夹内部下载，如果版本，内容不合适的话，则在相应的地址下载：
  - 1).python必须是嵌入式文件.下载地址：
https://www.python.org/downloads/windows/中查找带“embedded”字样的版本号
  - 2).下载pystand文件，在github仓库(https://github.com/skywind3000/PyStand)上下载同名文件，需要注意的是要下载cli版本，这样能看到信息;该版本在发布的PyStand-v1.1.4-exe.zip的文件中；