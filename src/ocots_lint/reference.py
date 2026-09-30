"""L'état du dépôt à une autre révision git, pour comparer (S3.8).

`git archive <réf>` extrait la révision dans un dossier temporaire, où l'on
rejoue la même analyse depuis le même chemin relatif : les empreintes des
deux états se comparent directement.

Les sous-modules (`template/`, `conventions/`) sont extraits aussi, au commit
que la révision épingle, quand ce commit est disponible dans le sous-module
local : l'analyse de la révision voit alors le même template que le cours
(S5.0). Un sous-module non initialisé, ou dont le commit n'a pas été
récupéré, est laissé vide : `sous_modules()` le dit.
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


def _dispo(racine, chemin, sha):
    """Vrai si `racine/chemin` est un sous-module initialisé qui a `sha`."""
    dossier = os.path.join(racine, chemin)
    if not os.path.isdir(dossier):
        return False
    try:        # un dossier vide ferait répondre le dépôt parent
        if os.path.realpath(_git("rev-parse", "--show-toplevel", dossier=dossier)) \
                != os.path.realpath(dossier):
            return False
        _git("cat-file", "-e", f"{sha}^{{commit}}", dossier=dossier)
    except ErreurReference:
        return False
    return True


def sous_modules(ref, depot=None):
    """[(chemin, commit épinglé, disponible)] des sous-modules de `ref`."""
    racine = _git("rev-parse", "--show-toplevel", dossier=depot)
    arbre = _git("ls-tree", "-r", "-z", ref, dossier=racine)
    liens = []
    for entree in filter(None, arbre.split("\0")):
        meta, chemin = entree.split("\t", 1)
        mode, _, sha = meta.split()
        if mode == "160000":
            liens.append((chemin, sha, _dispo(racine, chemin, sha)))
    return liens


def _deballer(archive, dossier):
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        if hasattr(tarfile, "data_filter"):     # Python ≥ 3.12, et correctifs
            tar.extractall(dossier, filter="data")
        else:                                   # archive de nos propres dépôts
            tar.extractall(dossier)


@contextlib.contextmanager
def extraire(ref, depot=None):
    """Le dossier, dans une copie de la révision `ref`, qui correspond au
    dossier courant — ou à la racine de `depot` s'il est donné. Les
    sous-modules disponibles sont extraits à leur commit épinglé."""
    racine = _git("rev-parse", "--show-toplevel", dossier=depot)
    relatif = "." if depot else os.path.relpath(os.getcwd(), racine)
    archive = _git("archive", "--format=tar", ref, binaire=True, dossier=racine)
    with tempfile.TemporaryDirectory(prefix="ocots-lint-ref-") as tmp:
        _deballer(archive, tmp)
        for chemin, sha, dispo in sous_modules(ref, depot=racine):
            if dispo:
                _deballer(_git("archive", "--format=tar", sha, binaire=True,
                               dossier=os.path.join(racine, chemin)),
                          os.path.join(tmp, chemin))
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
