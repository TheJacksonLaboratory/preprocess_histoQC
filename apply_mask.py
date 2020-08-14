import openslide
from PIL import Image
import numpy as np
from tifffile import *

def apply_mask(original, outdir):
    slide = openslide.OpenSlide(original)
    filename = original.split("/")[-1]
    mask = Image.open(outdir+"/"+filename + "/" +"_mask_use.png")
    mask = mask.resize((slide.dimensions[0], slide.dimensions[1]))
    masked = Image.new(mode="RGB", size=slide.dimensions, color=(255,255,255))
    slide_pixels = slide.read_region((0,0), 0, slide.dimensions)
    masked.paste(slide_pixels,(0,0),mask)
    np_masked = np.asarray(masked)
    with TiffWriter(original+"_masked.tif", bigtiff=True) as tif:
        tif.save(np_masked, compress=6)
    slide.close()
    mask.close()
    masked.close()
    slide_pixels.close()



if __name__ == "__main__":
    import sys
    import glob
    import argparse
    import os
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_pattern',
                        help="input filename pattern (try: *.svs or target_path/*.svs ), or tsv file containing list of files to analyze",
                        nargs="*")
    parser.add_argument('-o', '--outdir', help="outputdir, default ./histoqc_output", default="./histoqc_output_DATE_TIME", type=str, required=True)
    parser.add_argument('-p', '--basepath',
                        help="base path to add to file names, helps when producing data using existing output file as input",
                        default="", type=str)
    parser.add_argument('-c', '--config', help="config file to use", type=str)
    parser.add_argument('-f', '--force', help="force overwriting of existing files", action="store_true")
    parser.add_argument('-b', '--batch', help="break results file into subsets of this size", type=int,
                        default=float("inf"))
    parser.add_argument('-n', '--nthreads', help="number of threads to launch", type=int, default=1)
    parser.add_argument('-s', '--symlinkoff', help="turn OFF symlink creation", action="store_true")


    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    basepath = args.basepath  #
    basepath = basepath + os.sep if len(
        basepath) > 0 else ""  # if the user supplied a different basepath, make sure it ends with an os.sep
    files = []
    if len(args.input_pattern) > 1:  # bash has sent us a list of files
        files = args.input_pattern
    elif args.input_pattern[0].endswith("tsv"):  # user sent us an input file
        # load first column here and store into files
        with open(args.input_pattern[0], 'r') as f:
            for line in f:
                if line[0] == "#":
                    continue
                files.append(basepath + line.strip().split("\t")[0])
    else:  # user sent us a wildcard, need to use glob to find files
        files = glob.glob(args.basepath + args.input_pattern[0])
    print(files)

    # now do analysis of files
    for filei, fname in enumerate(files):
        fname = os.path.realpath(fname)
        apply_mask(fname, args.outdir)
