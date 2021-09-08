import os
import shutil
from pathlib import Path
import tarfile
tar = tarfile.open("test.tar.gz",mode='r')
tar.extractall()
tar.close()
files = sorted(Path('.').glob('**/*.h5'))
for file in files:
    