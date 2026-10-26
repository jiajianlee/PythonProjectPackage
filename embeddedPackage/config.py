#嵌入式python的文件夹路径，嵌入式python版本必须和uv环境中的版本一致。在UV中查询python版本命令:python --version。python必须是嵌入式文件.下载地址
#https://www.python.org/downloads/windows/中查找带“embedded”字样的版本号
PYTHON_EMBEDDED_PAKAGE_PATH=r"D:\01CompanyWorkArea\00WorkFile\04MyKnowledgeRepository\C#test\python打包程序\base\python-3.12.7-embed-amd64"
#get_pip文件路径
GET_PIP_PATH=r"D:\01CompanyWorkArea\00WorkFile\04MyKnowledgeRepository\C#test\python打包程序\base\get-pip.py"
#pystand文件路径，在github上下载同名文件，需要注意的是要下载cli版本，这样能看到信息;该版本在发布的PyStand-v1.1.4-exe.zip的文件中
PYSTAND_PATH=r"D:\01CompanyWorkArea\00WorkFile\04MyKnowledgeRepository\C#test\python打包程序\base\PyStand-x64-CLI\PyStand.exe"
#需要打包的文件夹路径，程序会将该文件夹及下面内容全部打包,以项目根目录为准的相对路径
PROJECT_PATH="src"
#项目入口文件名称
PROJECT_ENTRANCE="mainAA.py"
#项目名称
PROJECT_NAME="testAA"