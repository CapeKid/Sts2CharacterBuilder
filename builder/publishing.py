"""Offline preparation for the pinned official uploader; never executes uploads."""
import os
from pathlib import Path
import re
import stat
import zipfile

from .contracts import BuilderError, check_schema, contained, digest, encoded, read_json, validate
from .project import atomic
from .verification import compare_delivery, record, stage


def uploader_release(toolkit):
    return read_json(toolkit / 'builder/uploader-release.json')


def workspace_path(root, name):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name):
        raise BuilderError('Workspace name must be a short letter-led ID, not a path')
    return contained(root, 'private/workshop/' + name)


def publication(toolkit, root, existing_item=None):
    config, _, assets, _ = validate(toolkit, root)
    data = read_json(contained(root, 'publishing.json'))
    check_schema(data, read_json(toolkit / 'builder/publishing.schema.json'), '$publishing')
    target = data.get('existing_item_id')
    if existing_item != target:
        raise BuilderError('Update requires --existing-item matching publishing.json; a new item must omit both')
    dependencies = [data['baselib_workshop_id'], *data.get('dependencies', [])]
    for values in (dependencies, data.get('tags', []), data.get('content_descriptors', [])):
        if len(values) != len(set(values)):
            raise BuilderError('Publication lists must not contain duplicate entries')
    if target in dependencies:
        raise BuilderError('A Workshop item cannot depend on itself')
    preview = data['preview']
    if preview not in {a['path'] for a in assets}:
        raise BuilderError('Publication preview must be an exact declared PNG asset')
    image = contained(root, preview).read_bytes()
    if len(image) >= 1_000_000:
        raise BuilderError('Workshop preview must be smaller than 1 MB')
    workshop = dict(title=config['name'], description=data['description'], visibility='private',
                    changeNote=data.get('change_note', ''), tags=data.get('tags', []),
                    dependencies=dependencies, contentDescriptors=data.get('content_descriptors', []))
    return data, workshop, image


def official_archive(toolkit, archive):
    release = uploader_release(toolkit)
    payload = Path(archive).read_bytes()
    sha = digest(payload)
    name = next((n for n, h in release['archives'].items() if h == sha), None)
    if name is None:
        raise BuilderError('Uploader archive is not a pinned official release; verify the download or review a toolkit upgrade')
    import io
    files = {}
    names = set()
    try:
        package = zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile as error:
        raise BuilderError('Pinned uploader archive is not a valid ZIP') from error
    with package:
        for entry in package.infolist():
            path = entry.filename.rstrip('/')
            if not path or '\\' in path or ':' in path or path.startswith('/') or any(p in ('', '.', '..') for p in path.split('/')):
                raise BuilderError('Unsafe official uploader archive path')
            if path.casefold() in names or stat.S_ISLNK(entry.external_attr >> 16):
                raise BuilderError('Unsafe or duplicate official uploader archive entry')
            names.add(path.casefold())
            if not entry.is_dir():
                files[path] = (package.read(entry), bool(entry.external_attr >> 16 & 0o111))
    executable = 'ModUploader.exe' if '-win-' in name else 'ModUploader'
    if not {executable, 'template/workshop.json', 'template/README.md'} <= files.keys():
        raise BuilderError('Pinned uploader archive is missing its executable or workspace template')
    return release, name, sha, executable, files, payload


def prepare_publish(toolkit, root, name, archive, existing_item=None):
    destination = workspace_path(root, name)
    if destination.exists():
        raise BuilderError('Publication workspace already exists; preserve it and choose a new workspace name')
    data, workshop, image = publication(toolkit, root, existing_item)
    release, archive_name, archive_sha, executable, tools, archive_bytes = official_archive(toolkit, archive)
    report = stage(toolkit, root)
    # Read the closed archive, never a caller-supplied source directory. Avoid
    # extractall so every payload name and hash is checked before destination writes.
    with zipfile.ZipFile(report['archive']) as package:
        expected = dict(report['files'])
        inspection = report['id'] + '/package-inspection.json'
        expected[inspection] = digest(encoded(read_json(contained(root, 'dist/package-inspection.json'))))
        if len(package.namelist()) != len(expected) or set(package.namelist()) != set(expected):
            raise BuilderError('Staged ZIP inventory differs')
        content = {p: package.read(p) for p in expected}
        if any(digest(content[p]) != sha for p, sha in expected.items()):
            raise BuilderError('Staged ZIP bytes differ')
    files = {'content/' + p: value for p, value in content.items()}
    files.update({'tools/uploader/' + p: value[0] for p, value in tools.items()})
    files['tools/uploader-release.zip'] = archive_bytes
    files.update({'workshop.json': encoded(workshop), 'image.png': image})
    if existing_item is not None:
        files['mod_id.txt'] = (str(existing_item) + '\n').encode()
    receipt = dict(kind='publication-preparation', status='prepared', id=report['id'],
        publishing_sha256=digest(contained(root, 'publishing.json').read_bytes()),
        package_sha256=report['sha256'], uploader=dict(repository=release['repository'], tag=release['tag'],
            commit=release['commit'], archive=archive_name, sha256=archive_sha, executable=executable),
        existing_item_id=existing_item, visibility='private', uploaded=False, release_ready=False,
        files={p: digest(value) for p, value in sorted(files.items())},
        gaps=['Publication authorization and authenticated item owner/visibility checks remain required',
              'Upload and downloaded-byte verification unperformed; review package/native/device/balance gaps'])
    files['publication-preparation.json'] = encoded(receipt)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # Exclusive claim. On I/O failure retain partial work for inspection.
    for relative, payload in files.items():
        atomic(contained(destination, relative), payload)
    if os.name != 'nt':
        for relative, (_, executable_flag) in tools.items():
            if executable_flag:
                contained(destination, 'tools/uploader/' + relative).chmod(0o755)
        contained(destination, 'tools/uploader/' + executable).chmod(0o755)
    evidence = ['publishing.json', *[(destination / p).relative_to(root).as_posix() for p in files]]
    record(toolkit, root, 'publish', 'ready', evidence, 'Private official-uploader workspace prepared; upload unperformed')
    return dict(workspace=str(destination), **receipt,
        upload_argv=[str(destination / 'tools/uploader' / executable), 'upload', '-w', str(destination)],
        upload_cwd=str(destination / 'tools/uploader'))


def check_publish(toolkit, root, name, existing_item=None):
    directory = workspace_path(root, name)
    _, workshop, image = publication(toolkit, root, existing_item)
    receipt = read_json(contained(directory, 'publication-preparation.json'))
    report = stage(toolkit, root)
    if (receipt.get('kind') != 'publication-preparation' or receipt.get('id') != report['id']
            or receipt.get('package_sha256') != report['sha256']
            or receipt.get('publishing_sha256') != digest(contained(root, 'publishing.json').read_bytes())
            or receipt.get('existing_item_id') != existing_item):
        raise BuilderError('Publication preparation is stale or belongs to another project/item')
    pinned, archive_name, archive_sha, executable, tools, _ = official_archive(toolkit, contained(directory, 'tools/uploader-release.zip'))
    uploader = receipt['uploader']
    if (uploader.get('repository') != pinned['repository'] or uploader.get('commit') != pinned['commit'] or uploader.get('tag') != pinned['tag']
            or uploader.get('archive') != archive_name or uploader.get('sha256') != archive_sha
            or uploader.get('executable') != executable
            or any(contained(directory, 'tools/uploader/' + p).read_bytes() != value[0] for p, value in tools.items())):
        raise BuilderError('Publication uploader pin differs')
    actual = {}
    for path in directory.rglob('*'):
        relative = path.relative_to(directory).as_posix()
        safe = contained(directory, relative)
        if safe.is_file() and relative != 'publication-preparation.json':
            actual[relative] = digest(safe.read_bytes())
    expected = {'tools/uploader/' + p: digest(value[0]) for p, value in tools.items()}
    expected.update({'tools/uploader-release.zip': archive_sha, 'workshop.json': digest(encoded(workshop)), 'image.png': digest(image)})
    expected.update({'content/' + p: sha for p, sha in report['files'].items()})
    expected['content/' + report['id'] + '/package-inspection.json'] = digest(encoded(read_json(contained(root, 'dist/package-inspection.json'))))
    if existing_item is not None:
        expected['mod_id.txt'] = digest((str(existing_item) + '\n').encode())
    if actual != expected or receipt['files'] != expected:
        raise BuilderError('Publication workspace files changed, including content, tool or item marker')
    if (contained(directory, 'workshop.json').read_bytes() != encoded(workshop)
            or contained(directory, 'image.png').read_bytes() != image
            or (contained(directory, 'mod_id.txt').exists() != (existing_item is not None))
            or (existing_item is not None and contained(directory, 'mod_id.txt').read_bytes() != (str(existing_item) + '\n').encode())):
        raise BuilderError('Publication metadata or item marker differs')
    compare_delivery(root, directory / 'content')
    return dict(kind='publication-preflight', status='match', workspace=str(directory),
                visibility='private', existing_item_id=existing_item, uploaded=False, release_ready=False,
                package_sha256=report['sha256'], gaps=receipt['gaps'])
