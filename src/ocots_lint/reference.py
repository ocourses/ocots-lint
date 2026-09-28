"""L'état du dépôt à une autre révision git, pour comparer (S3.8).

`git archive <réf>` extrait la révision dans un dossier temporaire, où l'on
rejoue la même analyse depuis le même chemin relatif : les empreintes des
deux états se comparent directement.
"""

import contextlib
import io
import os
import subprocess
import tarfile
import tempfile


class ErreurReference(Exception):
    pass


def _git(*args, binaire=False, dossier=None):
    prefixe = ["-C", dossier] if dossier else []
    try:
        r = subprocess.run(["git", *prefixe, *args], capture_output=True,
                           check=True)
    except OSError as e:
        raise ErreurReference(f"git introuvable : {e}") from e
    except subprocess.CalledProcessError as e:
        raise ErreurReference(
            f"git {' '.join(args[:2])} : {e.stderr.decode(errors='replace').strip()}"
        ) from e
    return r.stdout if binaire else r.stdout.decode().strip()


@contextlib.contextmanager
def dans(dossier):
    avant = os.getcwd()
    os.chdir(dossier)
    try:
        yield
    finally:
        os.chdir(avant)


@contextlib.contextmanager
def extraire(ref):
    """Le dossier, dans une copie de la révision `ref`, qui correspond au
    dossier courant. Les sous-modules ne sont pas extraits."""
    racine = _git("rev-parse", "--show-toplevel")
    relatif = os.path.relpath(os.getcwd(), racine)
    archive = _git("archive", "--format=tar", ref, binaire=True, dossier=racine)
    with tempfile.TemporaryDirectory(prefix="ocots-lint-ref-") as tmp:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            if hasattr(tarfile, "data_filter"):     # Python ≥ 3.12, et correctifs
                tar.extractall(tmp, filter="data")
            else:                                   # archive de notre propre dépôt
                tar.extractall(tmp)
        base = os.path.normpath(os.path.join(tmp, relatif))
        os.makedirs(base, exist_ok=True)
        yield base


def empreintes_actives(ref, racines, noms, analyser):
    """Empreintes des trouvailles non exemptées à la révision `ref`."""
    with extraire(ref) as base, dans(base):
        presentes = [r for r in racines if os.path.exists(r)]
        if not presentes:
            return set()
        trouvailles, _ = analyser(presentes, noms)
    return {t.empreinte for t in trouvailles if not t.exemption}
