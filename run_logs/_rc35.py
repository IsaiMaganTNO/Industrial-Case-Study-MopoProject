import sqlite3
for tag,p in [("OLD",r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite"),("NEW",r".spinetoolbox\items\ines_db\ines_db.sqlite")]:
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    for t in ("bio-gasif-metha+CC","bio-gasif-metha","harber-bosch","bioST+CC","DAC"):
        n=c.execute("SELECT count(*) FROM entity WHERE name LIKE ?",(t+"%",)).fetchone()[0]
        print(tag,t,n)
    c.close()
