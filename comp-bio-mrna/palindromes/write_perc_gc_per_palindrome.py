
#usage: .py infilepath outfilepath
#or: .py infilepath (in which the outfile will be in a folder called gc-per-palind in the infile folder)
#infile format: a csv with the format start_nt, sequence, source_transcript_info(can have many so long as consistent)
#outfile format: a csv with the format start_nt, sequence, source_transcript_info, percent_gc (0-1)
import sys
import os
import pfind

infile = open(sys.argv[1],'r')
if len(sys.argv) < 3:
    infilefolder = '\\'.join(sys.argv[1].split('\\')[:-1])
    #print(infilefolder)
    infilename = sys.argv[1].split('\\')[-1]
    infileprefix = '.'.join(infilename.split('.')[:-1]) #everything before .csv or .txt
    #print(infileprefix)
    outfilepath = infilefolder + '\\gc-per-palind\\' + infileprefix + '-gc.csv' #only for windows path!!!
    os.makedirs(infilefolder + '\\gc-per-palind\\', exist_ok=True)
else:
    outfilepath = sys.argv[2]
outfile = open(outfilepath,'w')

data = infile.readlines()
infile.close()

for line in data:
    line_contents = line.split(',')
    #176,GTGCAC,FBtr0084567,FBgn0011725\n
    pGC = pfind.perc_gc_content(line_contents[1])
    outfile.write(line[:-1]+','+str(pGC)+'\n')

outfile.close()

