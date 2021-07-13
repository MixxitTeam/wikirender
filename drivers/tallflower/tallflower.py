import bpy
import re
import os
import io
from contextlib import redirect_stdout

dryRun = False

stdout = io.StringIO()

strBlocks = ""
strVars = ""

THISDRIVER = os.path.splitext(os.path.basename(__file__))[0]
print("Driver name: " + THISDRIVER + "-"*20)

if dryRun:
    print("="*20 + " Dry run " + "="*20)

def list_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

with open("blocks.txt", "r") as f:
    strBlocks = f.read()

with open("vars.txt", "r") as f:
    strVars = f.read()

lnsBlocks = strBlocks.split("\n")
blocks = []

for ln in lnsBlocks:
    if (ln.startswith("#") or ln.startswith("//") or ln.strip(" \t\r\n") == ""):
        continue
    fields = re.split(r"\t+", ln)
    if fields[0] != THISDRIVER:
        continue
    blocks.append({
        "outputfile": fields[1],
        "topTexBasename": fields[2],
        "bottomTexBasename": fields[3]
    })

lnsVars = strVars.split("\n")
vvars = {}

for ln in lnsVars:
    if (ln.startswith("#") or ln.startswith("//") or ln.strip(" \t\r\n") == ""):
        continue
    fields = ln.split("=", 1)
    vvars[fields[0]] = fields[1]

mat = bpy.data.materials.get("MAIN")
nodeTexTop = mat.node_tree.nodes["TexTop"]
nodeTexBottom = mat.node_tree.nodes["TexBottom"]
nodeBrRight = mat.node_tree.nodes["BrRight"]
nodeBrLeft = mat.node_tree.nodes["BrLeft"]

texSources = {
    "in": os.path.join(os.getcwd(), "input")
}

for key, value in vvars.items():
    if key.startswith("TextureDir."):
        srcname = key[11:]
        texSources[srcname] = value

resolutions = [int(x) for x in vvars["Resolutions"].split(",")]
useFallbackTex = [vvars["UseFallbackTexture"] == "True"]

render = bpy.data.scenes[0].render

subdirs = list_unique(["/".join(block["outputfile"].split("/")[:-1]) for block in blocks])
cwd = os.getcwd()

nodeBrRight.outputs[0].default_value = float(vvars["Brightness.RightFace"])
nodeBrLeft.outputs[0].default_value = float(vvars["Brightness.LeftFace"])

errors = []

for res in [str(r) for r in resolutions]:
    for subdir in subdirs:
        dirn = os.path.join(cwd, "output", res, subdir)
        if not os.path.isdir(dirn):
            if not dryRun:
                os.makedirs(dirn)

for resolution in resolutions:
    print("{r}x{r} px".format(r=resolution))
    
    if not dryRun:
        with redirect_stdout(stdout):
            render.resolution_x = resolution
            render.resolution_y = resolution

    for block in blocks:
        (texSrcTop, texNameTop) = block["topTexBasename"].split(":", 1)
        (texSrcBottom, texNameBottom) = block["bottomTexBasename"].split(":", 1)

        imagePathTop = os.path.join(texSources[texSrcTop], texNameTop + ".png")
        imagePathBottom = os.path.join(texSources[texSrcBottom], texNameBottom + ".png")
        outputPath = block["outputfile"]
        fullOutputPath = os.path.join(cwd, "output", str(resolution), outputPath)
        
        if not os.path.isfile(imagePathTop):
            skip = False
            err = "Could not find texture (top): {}".format(imagePathTop)
            if (useFallbackTex):
                err += " ; A fallback texture will be used"
                imagePathTop = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            print(err)
            errors.append(err)
            if skip:
                continue
        
        if not os.path.isfile(imagePathBottom):
            skip = False
            err = "Could not find texture (bottom): {}".format(imagePathBottom)
            if (useFallbackTex):
                err += " ; A fallback texture will be used"
                imagePathBottom = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            print(err)
            errors.append(err)
            if skip:
                continue

        print(outputPath + "...", end="")

        if not dryRun:
            with redirect_stdout(stdout):
                nodeTexTop.image = bpy.data.images.load(imagePathTop)
                nodeTexBottom.image = bpy.data.images.load(imagePathBottom)

                bpy.context.scene.render.filepath = fullOutputPath
                bpy.ops.render.render(write_still=True, use_viewport=True)

        print(" Done!")

print("All done!")

if len(errors) > 0:
    print("During operation, {c} error{s} occured:".format(c=len(errors), s=("s" if len(errors) != 1 else "")))
    for err in errors:
        print("  " + err)
