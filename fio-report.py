# molu@gmail.com
# 17.06.2019 - version 0.02
# Fio tests plots

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import os
import argparse

RESAMPLE_VALUE='5s'
DEBUG = 1
X_LABEL = 'time (* 100s)'


# parse the command line arguments
argParser = argparse.ArgumentParser()
argParser.add_argument('-f', type=str, help='the input file with the FIO log', required=True)
#argParser.add_argument('-d', type=str, help='description of the chart. If missing the file name is used', required=False)
argParser.add_argument('-t', type=str, help='Type of log. Accepted values "bw" for bandwidth and "iops" for "IOPS"', required=False)
argParser.add_argument('-b', type=str, help='Block size. E.g. 4K, 32K, 128K', required=True)
# argParser.add_argument('-f', type=str, help='the format of the output')

passedArgs = vars(argParser.parse_args())

inputFileName = passedArgs['f']
#chartDescription = passedArgs['d']
logType = passedArgs['t']
blockSize = passedArgs['b']
print('inputFileName :', inputFileName)
#print('chartDescription :', chartDescription)
print('logType :', logType)
print('*' * 50)
logTypes = ['iops', 'bw']

fullPath, fileName = os.path.split(inputFileName)

if 'logtype' in locals() and 'logtype' in logTypes:
    pass
else:
    logType = (fileName.split('.')[1]).split('_')[-1]
print('logType :', logType)

volType = fileName.split('.')[0].split('-')[1].upper()
accessType = fileName.split('.')[0].split('-')[2]

print('logType :', logType)


if logType in "bw":
    Y_LABEL = 'Bandwidth - KB/s'
    G_TITLE = 'TEMP bandwidth rw=read sequential vol=ephemeral bs=4k'
    # G_TITLE = 'bandwidth rw=read sequential vol=ephemeral bs=4k'
    # G_TITLE = 'Bandwidth rw=randrw rwmixread=70 vol=ephemeral bs=128k'
    G_TITLE = 'Bandwidth rw={0} vol={1} bs={2}'.format(accessType, volType, blockSize)
elif logType in "iops":
    Y_LABEL = 'IOPS - I/O Operations per second'
    #G_TITLE = 'IOPS rw=randrw rwmixread=70 vol=EBS bs=128k'
    G_TITLE = 'IOPS rw={0} vol={1} bs={2}'.format(accessType, volType, blockSize)
else:
    print('Not able to recognize type of logfile . Provide -b parameter')
    Y_LABEL = 'unknown'
    G_TITLE = 'unknown'
    print('Graph wont be generated. Exiting ...')
    exit(0)

print('Y_LABEL :', Y_LABEL)
print('G_TITLE :', G_TITLE)

pd.options.display.max_rows = 10

df = pd.read_table(inputFileName, sep=',',nrows=992400, header=None, names=['msec', 'value', 'readwrite','blocksize'])

describes=[]

df1 = df.copy()
describes.append([df1['value'].mean().round(), df1['value'].min().round(), df1['value'].max().round()])
df1['msec'] = df1['msec'] / 1000
df1.msec = df1.msec.round()
df1['value'] = df1.groupby(['msec'])['value'].transform('mean')
df1.index = df1['msec']
df1.sort_index(inplace=True)
df1.drop_duplicates(subset=['msec'], inplace=True)
df1.set_index('msec')

df2 = df[df['readwrite'] == 0].copy()
if not df2.empty:
    describes.append([df2['value'].mean().round(), df2['value'].min().round(), df2['value'].max().round()])
    df2['msec'] = pd.to_timedelta(df2['msec'], unit='ms')
    df2.index = df2['msec']
    df2.sort_index(inplace=True)
    df2.drop_duplicates(subset=['msec'], inplace=True)
    #del df2['msec']
else:
    describes.append([0,0,0])


df3 = df[df['readwrite'] == 1].copy()
if not df3.empty:
    describes.append([df3['value'].mean().round(), df3['value'].min().round(), df3['value'].max().round()])
    df3['msec'] = pd.to_timedelta(df3['msec'], unit='ms')
    df3.index = df3['msec']
    #del df3['msec']
    df3.sort_index(inplace=True)
    df3.drop_duplicates(subset=['msec'], inplace=True)
else:
    describes.append([0,0,0])


pds1 = pd.Series(df1['value'])
pds1.index = pd.to_timedelta(pds1.index, unit='s')
a5 = pds1.resample(RESAMPLE_VALUE).mean()

pds2 = pd.Series(df2['value'])
pds3 = pd.Series(df3['value'])
pds2.index = pd.to_timedelta(pds2.index, unit='s')
pds3.index = pd.to_timedelta(pds3.index, unit='s')
a6 = pds2.resample(RESAMPLE_VALUE).mean()
a7 = pds3.resample(RESAMPLE_VALUE).mean()


fig = plt.figure()
#fig.set_size_inches(18,11)
fig.set_size_inches(15,9)
ax3 = fig.add_subplot(2, 2, 3)
ax3.set(xlabel=X_LABEL, ylabel=Y_LABEL, title=G_TITLE)
ax3.plot(df1['msec'], df1['value'], 'g-')

ax4 = fig.add_subplot(2, 2, 4)
ax4.set(xlabel=X_LABEL, ylabel=Y_LABEL, title=G_TITLE)
ax4.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(['','0','1','2', '3', '4', '5', '6', '7', '8', '9', '10', '11']))


# Generating the legend
desclab1=(describes[0])
desclab2=(describes[1])
desclab3=(describes[2])
lab1 = "readrw :  avg: {0}".format(*desclab1)
lab2 = "read    : avg: {0}, min: {1}, max: {2}".format(*desclab2)
lab3 = "write  :  avg: {0}, min: {1}, max: {2}".format(*desclab3)
labeltab = [lab2, lab3, lab1]

la1,=ax4.plot(a5)
lr2,=ax4.plot(a6)
lw3,=ax4.plot(a7)

ax4.set_ylim(bottom=0)
ax4.legend([lr2, lw3, la1],labeltab, loc="lower right")

fullPath, filename = os.path.split(inputFileName)
baseFilename = os.path.splitext(filename)[0]
fileFormat = '.png'
imgFilename = os.path.join(fullPath, baseFilename +fileFormat)


extent = ax4.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
print('Saving chart as:', imgFilename)
fig.savefig(imgFilename, bbox_inches=extent.expanded(1.3, 1.4), dpi=80)
