from pathlib import Path
import pathlib
import subprocess
import tomllib
import json
import shutil
from config import PYTHON_EMBEDDED_PAKAGE_PATH,GET_PIP_PATH,PYSTAND_PATH,PROJECT_NAME,PROJECT_PATH,PROJECT_ENTRANCE


def CreatRequirements():
    #先读取pyproject.toml，得到dependencies内容，然后
    #读取uv.lock文件，先查找toml里面已经有的，然后再对里面已经有的查找dependencies的包，
    #最后生成一个包名：url的字典
    
    pyprojecttomlPath=Path(__file__).parent.parent.joinpath('pyproject.toml')
    uvlockPath=Path(__file__).parent.parent.joinpath('uv.lock')
    requirementFilePath=Path(__file__).parent.joinpath("Requirements.txt")
    with open(pyprojecttomlPath,'rb') as f:
        pyprojecttomlDict=tomllib.load(f)
    with open(uvlockPath,'rb') as f:
        uvlockDict=tomllib.load(f)
    projectName=pyprojecttomlDict.get("project",{}).get("name",None)
    uv_packageList=uvlockDict.get("package",[]) 
    print(f"uv.lock中有安装包:{len(uv_packageList)}")   
    projectDependList=GetAllPackages(uv_packageList,projectName,[])
    packageDictList=[]
    for name,version,url in projectDependList:
        if url!="" :
            packageDict={
                        'name':f"{name}",
                        'version':f'{version}',
                        'url':f"{url}"
            }
            packageDictList.append(packageDict)    
    uvpackageNameList=[n["name"]for n in uv_packageList]
    requirementNameList=[n["name"]for n in packageDictList]
    hasFilterPackageNameList=[]
    for name in uvpackageNameList:
        if name not in requirementNameList:
            hasFilterPackageNameList.append(name)
    print(f"requirement中有安装包:{len(packageDictList)};未包含的包有:{';'.join(hasFilterPackageNameList)}")

    with open(requirementFilePath,'w') as f:
          json.dump(packageDictList,f,indent=4)  
    

def GetAllPackages(uv_packageList:list[dict],packageName:str,package_name_sourceList:list[tuple])->list[tuple]:
    package=[pk for pk in uv_packageList if pk['name']==packageName][0]
    packSource=package["source"].get("registry","")
    version=package["version"]
    dependList=package.get("dependencies",[])
    if packageName not in [n[0] for n in package_name_sourceList]:            
            package_name_sourceList.append((packageName,version,packSource))
    if len(dependList)>0:    
        dpNameList=[dp["name"] for dp in dependList]
        extraNameList=[]
        optionalDependDict=package.get("optional-dependencies",{})
        if optionalDependDict:
           assert isinstance(optionalDependDict,dict)
           for key,item in optionalDependDict.items():
               extraNameList.extend([n.get("name","") for n in item] ) 
           extraNameList=[n for n in extraNameList if n!=""]
           dpNameList.extend(extraNameList)
        
        allreadyInNameList=[n[0] for n in package_name_sourceList]
        dpNameList_ff=[n for n in dpNameList if n not in allreadyInNameList]
        for name in dpNameList_ff:
            dependList=GetAllPackages(uv_packageList,name,package_name_sourceList)
            # package_name_sourceList.extend(dependList)
    return package_name_sourceList
        
    
    

def CreatPackageFolder():
    rootPath=Path(__file__).parent.parent
    #创建打包父目录
    packagePath=rootPath.joinpath(f'package-{PROJECT_NAME}')
    runtimePath=packagePath.joinpath('runtime')
    
    runtimePath.mkdir(parents=True,exist_ok=True)
    


    #embeddedPackage的路径
    downloadPath=Path(__file__).parent.joinpath("download.py")
    requirementsPath=Path(__file__).parent.joinpath("Requirements.txt")
    pystandPath=Path(__file__).parent.joinpath("PyStand.py")

    modulePath=rootPath.joinpath(PROJECT_PATH)
    #校验是否存在PROJECT_PATH文件夹，是否有PROJECT_ENTRANCE入口文件
    if not modulePath.exists():
        print(f"项目根目录下没有{PROJECT_PATH}文件夹，请修改config文件")
        return
    if not modulePath.joinpath(PROJECT_ENTRANCE).exists():
        print(f"项目根目录下没有{PROJECT_ENTRANCE}入口文件，请修改config文件")
        return

    #查找pojectpath下面第一个模块名称
    projectModuleName=None
    for child in sorted(modulePath.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and (child / "__init__.py").is_file():
          projectModuleName=child.name  
    if projectModuleName is None:
        print(f"没有找到{PROJECT_PATH}下总模块的名称,请在总模块文件夹下添加__init__.py文件")
        return

    #复制文件    
    #将文件用nuitka 转换成.pyd格式
    command=['uv','run','python','-m',"nuitka",
        "--python-flag=no_warnings,-O,no_docstrings",
        "--remove-output",
        "--no-pyi-file",
        "--module", f"{PROJECT_PATH}/{PROJECT_ENTRANCE}",
        f"--include-package={projectModuleName}",
        f"--output-dir={str(packagePath)}",
        "--show-modules"

    ]
    result = subprocess.run(
            command,
            cwd=str(rootPath),          # 必须在项目根目录执行，否则 src/main.py 找不到
            capture_output=False,      # True 可以捕获输出；False 直接透传到控制台
            text=True,
            check=False,               # 自己判断 returncode，不抛异常
        )
    print("✅项目文件已打包")    
    #复制python嵌入式解释器
    shutil.copytree(Path(PYTHON_EMBEDDED_PAKAGE_PATH), runtimePath, dirs_exist_ok=True)
    #复制get-pip
    shutil.copy2(Path(GET_PIP_PATH), runtimePath.joinpath("get-pip.py")) 
    #复制pystand.exe
    shutil.copy2(Path(PYSTAND_PATH), packagePath.joinpath(f'{PROJECT_NAME}.exe'))
    #复制download.py
    shutil.copy2(downloadPath, runtimePath.joinpath('download.py'))
    #复制Requirements
    shutil.copy2(requirementsPath, runtimePath.joinpath('Requirements.txt'))
    #复制PyStand.int
    pystandPath_target=packagePath.joinpath(f"{PROJECT_NAME}.py")
    pystandPath_target=pystandPath_target.with_suffix(".int")
    shutil.copy2(pystandPath, pystandPath_target)
    #创建pystand.path文件
    dotPath=packagePath.joinpath(f"{PROJECT_NAME}.pth")
    modified=False
    if dotPath.exists():
        with open(dotPath,"r",encoding='utf-8') as f:
            lines=f.readlines()
        stripped_lines = [line.strip() for line in lines]
        if f"{PROJECT_PATH}" not in stripped_lines:
            if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
            lines.append(f"{PROJECT_PATH}" + "\n")
            modified=True
    else:
        modified=True
        lines=[]
        lines.append(f"{PROJECT_PATH}" + "\n")
    
    if modified:
        with open(dotPath,'w',encoding='utf-8') as f:
            text=''.join(lines)
            f.write(text)
        print(f"✅ 已更新 {PROJECT_NAME}.pth 文件。")  
    else:
        print(f" {PROJECT_NAME}.pth 文件已存在，不用更新。")   

    #修改python内部的.path文件
    python_dotPath=runtimePath.joinpath("python312._pth")
    with open(python_dotPath,'r',encoding='utf-8') as f:
         lines =f.readlines()
    stripped_lines = [line.strip() for line in lines]
    modified = False
    if r"Lib\site-packages" not in stripped_lines:
    # 确保最后一行有换行符，防止追加的内容和最后一行粘在一起
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(r"Lib\site-packages" + "\n")
        modified = True
    if "import site" not in stripped_lines:
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append("import site" + "\n")
        modified = True
    if modified:
        with open(python_dotPath, 'w', encoding='utf-8') as f:
            text=''.join(lines)
            f.write(text)
        print(f"✅ 已更新 {python_dotPath.name} 文件。")
    else:
        print(f"ℹ️ {python_dotPath.name} 已包含所需配置，无需修改。")

    print("-"*20+"已打包完成"+"-"*20) 



if __name__ == "__main__":

    CreatRequirements()
    CreatPackageFolder()