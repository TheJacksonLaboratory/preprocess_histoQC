import openslide
from PIL import Image

def apply_mask(original):
    slide = openslide.OpenSlide(original)
    mask = Image.open(original+"_mask_use.png")
    mask = mask.resize((slide.dimensions[0], slide.dimensions[1]))
    masked = Image.new(mode="RGB", size=slide.dimensions, color=(255,255,255))
    slide_pixels = slide.read_region((0,0), 0, slide.dimensions)
    masked.paste(slide_pixels,(0,0),mask)
    masked.save(original+"_masked.png","PNG", optimize=True)



if __name__ == "__main__":
    import sys
    import glob
    for original in glob.glob(sys.argv[-1]):
        print(original)
        apply_mask(original)
