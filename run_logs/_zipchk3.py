import zipfile, os
z = zipfile.ZipFile("share_vre15.zip")
zn = {n.replace("\\", "/") for n in z.namelist() if not n.endswith("/")}
root = "share_vre15"
dn = set()
for dp, _, fs in os.walk(root):
    for f in fs:
        rel = os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
        dn.add(rel)
print("in_zip", len(zn), "on_disk", len(dn))
print("MISSING_FROM_ZIP:")
for x in sorted(dn - zn):
    print("   ", x)
print("EXTRA_IN_ZIP:")
for x in sorted(zn - dn):
    print("   ", x)
print("DOCS in zip:")
for x in sorted(n for n in zn if n.startswith("docs/")):
    print("   ", x)
bad = []
for n in sorted(zn & dn):
    if z.getinfo(n).file_size != os.path.getsize(os.path.join(root, n)):
        bad.append(n)
print("SIZE_MISMATCH", len(bad), bad[:10])
z.close()
