import zipfile, os, hashlib
p = "share_vre15.zip"
print("size_bytes", os.path.getsize(p))
z = zipfile.ZipFile(p)
names = z.namelist()
print("members", len(names))
print("testzip", z.testzip())
print("uncompressed_bytes", sum(i.file_size for i in z.infolist()))
want = ["docs/PLAN_mixed_resolution_run.md",
        "docs/ASSESSMENT_scope_NLBE_IC1_plus_NO_DE_DK_UK.md"]
for w in want:
    hits = [n for n in names if n.replace("\\", "/").endswith(w)]
    print("LOOKFOR", w, "->", hits)
    for h in hits:
        d = z.read(h)
        print("   bytes", len(d), "md5", hashlib.md5(d).hexdigest()[:12])
tops = sorted({n.replace("\\", "/").split("/")[0] for n in names})
for t in tops:
    c = [n for n in names if n.replace("\\", "/").split("/")[0] == t]
    print("TOP", t, len(c))
z.close()
