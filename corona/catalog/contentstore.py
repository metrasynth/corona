from django.conf import settings
import hashlib
import os
import re
import shutil

from corona.errors import DataValidationError


SHA1_RE = re.compile(r'^[0-9A-Fa-f]{40}$')


def assert_clean(digest):
    if not SHA1_RE.match(digest):
        raise DataValidationError()


class ContentStore(object):

    def __init__(self, root):
        self.root = root

    def add(self, srcpath):
        h = hashlib.sha1()
        with open(srcpath, 'rb') as f:
            while True:
                block = f.read(32768)
                if block:
                    h.update(block)
                else:
                    break
        digest = h.hexdigest()
        destpath = self.digest_pathname(digest)
        if not os.path.exists(destpath):
            destdir = os.path.dirname(destpath)
            os.makedirs(destdir, exist_ok=True)
            destpath_tmp = '{}.incomplete'.format(destpath)
            shutil.copy(srcpath, destpath_tmp)
            os.rename(destpath_tmp, destpath)
        return digest

    def digest_pathname(self, digest):
        assert_clean(digest)
        filename = '{}/{}/{}'.format(digest[0:2], digest[2:4], digest[4:])
        return os.path.join(self.root, filename)

    def exists(self, digest):
        return os.path.exists(self.digest_pathname(digest))

    def open(self, digest, mode='rb'):
        return open(self.digest_pathname(digest), mode)


content_store = ContentStore(settings.CATALOG_CONTENT_STORE)
