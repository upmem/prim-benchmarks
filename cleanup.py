import os
import shutil

target = "."

for d in os.scandir(target):
    if os.path.isdir(d):
        if os.path.isdir(os.path.join(d, "profile")) : 
            print(f"removing {os.path.join(d, 'profile')}")
            shutil.rmtree(os.path.join(d, "profile"))
           