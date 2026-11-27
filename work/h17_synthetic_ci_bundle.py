"""Stage a positive, code-only allowlist for the isolated synthetic CI job."""
from pathlib import Path
import argparse
import os
import shutil
import stat
import tempfile

FILES = (
    'h17_ax7782_object_intake.py', 'h17_k04_binary_window_intake.py',
    'h17_ax7782_k08_phrase_intake.py', 'h17_redaction.py',
    'h17_ooxml_text_intake.py', 'h17_photo_caption_metadata.py',
    'h17_k04_image_barcode_intake.py', 'h17_k04_emf_dib_intake.py',
    'h17_k04_pdf_barcode_intake.py', 'h17_k04_pcl_raster_intake.py',
    'h17_emf_text.py', 'h17_xps_text.py', 'h17_xps_glyph_indices.py',
    'h17_k08_teal_bit_image_scan.py', 'h17_biff_officeart.py',
    'h17_biff_officeart_blips.py', 'h17_doc_lo_fallback.py',
    'h17_xls_lo_fallback.py', 'test_h17_biff_officeart.py',
    'test_h17_biff_officeart_blips.py', 'test_h17_emf_text.py',
    'h17_synthetic_transfer_fixture.py', 'test_h17_ax7782_object_intake.py',
    'test_h17_ax7782_k08_phrase_intake.py',
    'h17_synthetic_ci_bundle.py', 'test_h17_synthetic_ci_bundle.py',
)


def stage(root: Path, output: Path) -> int:
    root = root.resolve(strict=True)
    work = root / 'work'
    if work.is_symlink() or not work.is_dir():
        raise ValueError('work must be a real directory')
    output = output.absolute()
    parent = output.parent.resolve(strict=True)
    output = parent / output.name
    if output.exists() or output.is_symlink() or output.is_relative_to(root):
        raise ValueError('output must be new and outside the repository')
    with tempfile.TemporaryDirectory(prefix='h17-stage-', dir=parent) as temp:
        staged = Path(temp) / 'code'
        staged.mkdir(mode=0o755)
        for name in FILES:
            fd = os.open(work / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, 'rb') as src:
                if not stat.S_ISREG(os.fstat(src.fileno()).st_mode):
                    raise ValueError('allowlisted entry must be a regular file')
                with (staged / name).open('xb') as dest:
                    shutil.copyfileobj(src, dest)
                (staged / name).chmod(0o444)
        staged.rename(output)
    return len(FILES)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(f'Staged {stage(args.root, args.output)} allowlisted code files')
