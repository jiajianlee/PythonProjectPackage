
import re
import sys
from pathlib import Path
import subprocess
import importlib
import json
print("\n".join(sys.path))
print("hello")
def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).strip().lower() 
def shouldUpdataDependList():
  shouldUpdata=False
  python_path = Path(sys.exec_prefix).joinpath("python.exe")
  print(f"路径:{str(python_path)}")
  download_script = Path(sys.exec_prefix).joinpath("download.py")
  requirement_path=Path(sys.exec_prefix).joinpath("Requirements.txt")
  try:
    from mainAA import main
  except ModuleNotFoundError:
    print("无法成功导入入口函数，需更新")
    shouldUpdata=True
  if not shouldUpdata:
    result = subprocess.run(
                [str(python_path), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8"
            )
            # 将 JSON 列表转换为 {包名: 版本} 的字典
    installed_data = json.loads(result.stdout) 
    installed_data_namelist=[canonical(d["name"]) for d in installed_data] 
    with open(requirement_path,'r',encoding='utf-8') as f:
            text=f.read()
            requdependList=json.loads(text)
        
    for rd in requdependList:
        name=canonical(rd["name"])
        if name not in installed_data_namelist:
            shouldUpdata=True
            print(f"缺少依赖包{name}，需更新")
            break
   
  
  if shouldUpdata:    
    command =[str(python_path),str(download_script)]
    subprocess.run(command, check=True)
    importlib.invalidate_caches()
     

  






if __name__ == "__main__":
  shouldUpdataDependList()
  from mainAA import main
  main()
