import pandas as pd
import plorts
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
import os
import gzip
from collections import defaultdict
plt.style.use(['plorts','plorts-print'])

if len(sys.argv) < 2:
    print>>sys.stderr, "Usage: %s path/to/queue/info.csv"%(sys.argv[0])

path = sys.argv[1]

dirname = os.path.dirname(path)
filename = os.path.basename(path)

df = pd.read_csv(path)
df['queue_depth_packets'] = df.queue_depth_cells*80/9000
plt.figure(figsize=(15,10))
for i,(port,port_df) in enumerate(df.groupby('egress_port')):
    plt.subplot(3,1,i+1)
    plorts.scatter(data=port_df, x="queue_depth_packets", y="num_packets")
    plt.title(port)
    plt.axis(ymin=0)
    plorts.style_axis()
plt.tight_layout()
plorts.savefig(os.path.join(dirname, 'plots', filename + '.png'))
plt.close()
