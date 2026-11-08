from pathlib import Path
import shutil, subprocess, os, gzip
repo=Path(__file__).resolve().parents[1]
base=Path(os.environ.get('OUTPUT_DIR', str(repo / 'dist')))
base.mkdir(parents=True, exist_ok=True)
stage=base/'deb-stage-2.2'
if stage.exists(): shutil.rmtree(stage)
def put(path,content,mode=0o644):
 p=stage/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content); p.chmod(mode)
put('DEBIAN/control','''Package: gold-silber-rechner
Version: 2.2-2
Section: utils
Priority: optional
Architecture: all
Maintainer: Volker Andreas Müller <gsr@linuga.org>
Depends: python3 (>= 3.9), python3-tk, libstartup-notification0, python3-requests (>= 2.25), tzdata, ca-certificates
Homepage: https://linuga.org/gsr/
Description: Materialwert von Gold und Silber berechnen
 Grafischer Rechner fuer Gewicht, Feinheit und Materialwert mit
 automatischem Abruf aktueller Edelmetallkurse und manueller Preiseingabe.
''')
put('usr/bin/gold-silber-rechner','#!/bin/sh\nexec /usr/bin/python3 /usr/share/gold-silber-rechner/gold-silver-value-calculator-german-v2.2.py "$@"\n',0o755)
for name in ['gold-silver-value-calculator-german-v2.2.py','gold-silber-icon.png']:
 p=stage/'usr/share/gold-silber-rechner'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/name,p);p.chmod(0o644)
p=stage/'usr/share/icons/hicolor/256x256/apps/gold-silber-rechner.png';p.parent.mkdir(parents=True,exist_ok=True)
# Preserve the original icon without relabelling its dimensions.
p=stage/'usr/share/pixmaps/gold-silber-rechner.png';p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/'gold-silber-icon.png',p);p.chmod(0o644)
put('usr/share/applications/gold-silber-rechner.desktop','''[Desktop Entry]
Name=Gold- und Silberrechner
Comment=Materialwert von Gold und Silber berechnen
Exec=gold-silber-rechner
Icon=gold-silber-rechner
Terminal=false
Type=Application
Categories=Office;Finance;
StartupNotify=false
''')
put('usr/share/doc/gold-silber-rechner/copyright','Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: Gold- und Silberrechner\nSource: https://github.com/media-vm/gold-silber-rechner\n\nFiles: *\nCopyright: 2026 Volker Andreas Müller\nLicense: MIT\n'+''.join(' '+line+'\n' for line in (repo/'LICENSE').read_text().splitlines()))
put('usr/share/doc/gold-silber-rechner/README.md',(repo/'README.md').read_text())
changelog='gold-silber-rechner (2.2-2) stable; urgency=medium\n\n  * Complete inherited X11 startup notification; unify desktop launchers.\n\n -- Volker Andreas Müller <gsr@linuga.org>  Sun, 08 Nov 2026 12:00:00 +0100\n'
p=stage/'usr/share/doc/gold-silber-rechner/changelog.Debian.gz';p.write_bytes(gzip.compress(changelog.encode(),mtime=0))
size=sum(p.stat().st_size for p in (stage/'usr').rglob('*') if p.is_file())
with (stage/'DEBIAN/control').open('a') as f:f.write(f'Installed-Size: {(size+1023)//1024}\n')
for p in stage.rglob('*'):
 if p.is_dir():p.chmod(0o755)
env=dict(os.environ,SOURCE_DATE_EPOCH='1794135600')
subprocess.run(['dpkg-deb','--root-owner-group','--build',str(stage),str(base/'gold-silber-rechner_2.2-2_all.deb')],check=True,env=env)
