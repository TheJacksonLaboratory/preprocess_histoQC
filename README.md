# preprocess_histoQC
Container for preprocessing slides using HistoQC

# Structure
---
This repo contains a Singularity recipe for a container that runs HistoQC and then uses its output for an extra step (apply_mask.py) that masks out all parts of the original slides that were deemed "bad" by HistoQC. It reads each input file using openslide, the corresponding mask using PIL, then it upscales the mask to the same dimensions of the original slide. Finally, it creates a new empty image (white background), pastes the original slide on it in the areas allowed by the mask, generates a numpy array from this result and saves it as a BigTiff.

I have not done any optimization on this, both in terms of performance and compression - it is relatively slow and the output files are large. The researchers working on the downstream pipeline are certainly in a much better position to do these steps, given their knowledge of the requisites from the next processing steps.

The container recipe clones this very repository for apply_mask.py - feel free to fork the repo, pin the repo to a particular commit (which is what I did to HistoQC for reproducibility), do whatever you want with it! I have tried to pin everything to specific versions and commits when building the container, so as long as this repo and the HistoQC repo exist (and the ubuntu/packages/python libs are still accessible), the recipe will always build exactly the same thing.

# Usage
---

```  
./preprocess_histoqc.sif --help
usage:  preprocess_histoqc.sif [-h] [-o OUTDIR] [-p BASEPATH] [-c CONFIG] [-f]
                      [-b BATCH] [-n NTHREADS] [-s]
                      [input_pattern [input_pattern ...]]

positional arguments:
  input_pattern         input filename pattern (try: *.svs or
                        target_path/*.svs ), or tsv file containing list of
                        files to analyze

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        outputdir, default ./histoqc_output
  -p BASEPATH, --basepath BASEPATH
                        base path to add to file names, helps when producing
                        data using existing output file as input
  -c CONFIG, --config CONFIG
                        config file to use
  -f, --force           force overwriting of existing files
  -b BATCH, --batch BATCH
                        break results file into subsets of this size
  -n NTHREADS, --nthreads NTHREADS
                        number of threads to launch
  -s, --symlinkoff      turn OFF symlink creation

```

I have replicated the argument structure of HistoQC and all arguments are passed to both HistoQC and the step that applies the masks to the slides. A few important points:

- The output dir argument is required; without outdir, HistoQC generates timestamped output directories that are much harder to retrieve programatically than a specified directory.
- The default config from HistoQC requires annotations and templates; you might need to specify a custom config file.
- I have been using this with the --symlinkoff option; symlinking can be problematic given the read-only nature of Singularity containers.

For full disclosure, this is the exact setup I just ran to get it working: 

- build this recipe, container image is in current dir
- put all SVS files into a folder named input_data on current dir
- create empty output_data folder on current dir
- create custom config.ini on current dir without the modules requiring annotation (ClassificationModule.byExampleWithFeatures:pen_markings, ClassificationModule.byExampleWithFeatures:coverslip_edge, HistogramModule.compareToTemplates)
- run ./preprocess_histoqc.sif -s --config config.ini -o ./output_data/ input_data/*.svs