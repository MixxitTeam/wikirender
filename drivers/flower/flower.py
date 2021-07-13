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
        "allTexBasename": fields[2]
    })

lnsVars = strVars.split("\n")
vvars = {}

for ln in lnsVars:
    if (ln.startswith("#") or ln.startswith("//") or ln.strip(" \t\r\n") == ""):
        continue
    fields = ln.split("=", 1)
    vvars[fields[0]] = fields[1]

mat = bpy.data.materials.get("MAIN")
nodeTexAll = mat.node_tree.nodes["TexAll"]
nodeBrRight = mat.node_tree.nodes["BrRight"]
nodeBrLeft = mat.node_tree.nodes["BrLeft"]
nodeBrTop = mat.node_tree.nodes["BrTop"]

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
nodeBrTop.outputs[0].default_value = float(vvars["Brightness.TopFace"])

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
        (texSrcAll, texNameAll) = block["allTexBasename"].split(":", 1)

        imagePathAll = os.path.join(texSources[texSrcAll], texNameAll+ ".png")
        outputPath = block["outputfile"]
        fullOutputPath = os.path.join(cwd, "output", str(resolution), outputPath)
        
        if not os.path.isfile(imagePathAll):
            skip = False
            err = "Could not find texture (all): {}".format(imagePathAll)
            if (useFallbackTex):
                err += " ; A fallback texture will be used"
                imagePathAll = os.path.join(cwd, "missingno.png")
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
                nodeTexAll.image = bpy.data.images.load(imagePathAll)

                bpy.context.scene.render.filepath = fullOutputPath
                bpy.ops.render.render(write_still=True, use_viewport=True)

        print(" Done!")

print("All done!")

if len(errors) > 0:
    print("During operation, {c} error{s} occured:".format(c=len(errors), s=("s" if len(errors) != 1 else "")))
    for err in errors:
        print("  " + err)
