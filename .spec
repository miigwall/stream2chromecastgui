# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import install_hooks
install_hooks(globals())

def filter_binaries(all_binaries):
    '''Exclude binaries provided by system packages, and rely on .deb dependencies
    to ensure these binaries are available on the target machine.

    We need to remove OpenGL-related libraries so we can distribute the executable
    to other linux machines that might have different graphics hardware. If you
    bundle system libraries, your application might crash when run on a different
    machine with the following error during kivy startup:

    Fatal Python Error: (pygame parachute) Segmentation Fault

    If we strip all libraries, then PIL might not be able to find the correct _imaging
    module, even if the `python-image` package has been installed on the system. The
    easy way to fix this is to not filter binaries from the python-imaging package.

    We will strip out all binaries, except libpython2.7, which is required for the
    pyinstaller-frozen executable to work, and any of the python-* packages.
    '''

    print 'Excluding system libraries'
    import subprocess
    excluded_pkgs  = set()
    excluded_files = set()
    whitelist_prefixes = ('libpython2.7', 'python-')
    binaries = []

    for b in all_binaries:
        try:
            output = subprocess.check_output(['dpkg', '-S', b[1]], stderr=open('/dev/null'))
            p, path = output.split(':', 2)
            if not p.startswith(whitelist_prefixes):
                excluded_pkgs.add(p)
                excluded_files.add(b[0])
                print ' excluding {f} from package {p}'.format(f=b[0], p=p)
        except Exception:
            pass

    print 'Your exe will depend on the following packages:'
    print excluded_pkgs

    inc_libs = set(['libpython2.7.so.1.0'])
    binaries = [x for x in all_binaries if x[0] not in excluded_files]
    return binaries


a = Analysis(['scribe.py'],
             pathex=['.'],
             hiddenimports=[],
            )
pyz = PYZ(a.pure)

binaries = filter_binaries(a.binaries)

exe = EXE(pyz,
          [('scribe.kv', 'scribe.kv', 'DATA')],
          a.scripts,
          binaries, #a.binaries,
          a.zipfiles,
          a.datas,
          name='ia-scribe',
          debug=False,
          strip=None,
          upx=True,
          console=False )