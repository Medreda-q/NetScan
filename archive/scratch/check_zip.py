import zipfile

with zipfile.ZipFile(r"C:\Users\DevLab\Desktop\Rapport_Soutenance_QIYAOUI.docx", "r") as z:
    for name in z.namelist():
        if "media/" in name or "header" in name or "footer" in name or "settings" in name:
            info = z.getinfo(name)
            print(f"{name} ({info.file_size} bytes)")
