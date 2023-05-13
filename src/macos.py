import os
import ssl
import stat
from pathlib import Path

STAT_0o775 = (
    stat.S_IRUSR | stat.S_IWUSR |
    stat.S_IXUSR | stat.S_IRGRP |
    stat.S_IWGRP | stat.S_IXGRP |
    stat.S_IROTH | stat.S_IXOTH
)


def setup_macos_certs():
    openssl_path = Path(ssl.get_default_verify_paths().openssl_cafile)
    openssl_dir = openssl_path.parent

    # make sure directory exists
    openssl_dir.mkdir(parents=True, exist_ok=True)

    # removing any existing file or link
    openssl_path.unlink(True)

    # creating symlink to certifi certificate bundle
    cert_file = Path(os.environ['REQUESTS_CA_BUNDLE'])
    openssl_path.symlink_to(cert_file)

    # setting permissions
    openssl_path.chmod(STAT_0o775)
