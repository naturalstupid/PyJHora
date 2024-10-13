import os
import sys
path_root = os.path.dirname('../../')
if path_root not in sys.path:
    sys.path.append(str(path_root))
    print(path_root,'added to system path',sys.path)