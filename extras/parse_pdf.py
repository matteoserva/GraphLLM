#!/usr/bin/python3
"""A command line tool for extracting text and images from PDF and
output it to plain text, html, xml or tags."""
import argparse
import logging
import sys
from typing import Any, Container, Iterable, List, Optional

import pdfminer.high_level
from pdfminer.layout import LAParams
from pdfminer.utils import AnyIO
from pdfminer.pdfexceptions import PDFValueError

logging.basicConfig()

OUTPUT_TYPES = ((".htm", "html"), (".html", "html"), (".xml", "xml"), (".tag", "tag"))


def float_or_disabled(x: str) -> Optional[float]:
    if x.lower().strip() == "disabled":
        return None
    try:
        return float(x)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid float value: {x}")


def extract_text(
    files: Iterable[str] = [],
    outfile: str = "-",
    laparams: Optional[LAParams] = None,
    output_type: str = "text",
    codec: str = "utf-8",
    strip_control: bool = False,
    maxpages: int = 0,
    page_numbers: Optional[Container[int]] = None,
    password: str = "",
    scale: float = 1.0,
    rotation: int = 0,
    layoutmode: str = "normal",
    output_dir: Optional[str] = None,
    debug: bool = False,
    disable_caching: bool = False,
    **kwargs: Any,
) -> AnyIO:
    if not files:
        raise PDFValueError("Must provide files to work upon!")

    if outfile == "-":
        outfp: AnyIO = sys.stdout
        if sys.stdout.encoding is not None:
            codec = "utf-8"
    else:
        outfp = open(outfile, "wb")

    with open("/tmp/parsed_pdf.txt", "wb") as log_fp:

        for fname in files:
            with open(fname, "rb") as fp:
                #pdfminer.high_level.extract_text_to_fp(fp, **locals())
                res = pdfminer.high_level.extract_text(fp, codec=codec )
                sys.stdout.buffer.write(res.encode('utf8'))
                log_fp.write(res.encode('utf8'))
            #print()
    print("pdf parsed and saved in /tmp/parsed_pdf.txt" , file=sys.stderr)
    return outfp





def main(args: Optional[List[str]] = None) -> int:

    outfp = extract_text(files=sys.argv[1:],laparams=LAParams())
    outfp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
