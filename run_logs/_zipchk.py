import zipfile
z=zipfile.ZipFile("share_vre15.zip")
bad=z.testzip()
print("corrupt member:",bad)
n=z.namelist()
print("members:",len(n))
import collections
c=collections.Counter(m.split("/")[0] for m in n)
for k,v in sorted(c.items()): print(f"  {k:20} {v}")
big=[(i.filename,round(i.file_size/1024/1024,1)) for i in z.infolist() if i.file_size>1e7]
print("large files:",big)
