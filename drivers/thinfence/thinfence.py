import bpy
import os
import sys
from contextlib import redirect_stdout
sys.path.insert(1, os.path.abspath("./"))
from drivercommon import *

mat = bpy.data.materials.get("MAIN")
nodeTexAll = mat.node_tree.nodes["TexAll"]
nodeBrRight = mat.node_tree.nodes["BrRight"]
nodeBrLeft = mat.node_tree.nodes["BrLeft"]
nodeBrTop = mat.node_tree.nodes["BrTop"]

render = bpy.data.scenes[0].render

nodeBrRight.outputs[0].default_value = float(vvars["Brightness.RightFace"])
nodeBrLeft.outputs[0].default_value = float(vvars["Brightness.LeftFace"])
nodeBrTop.outputs[0].default_value = float(vvars["Brightness.TopFace"])

errors = []
blocks = []

for bdat in blockData:
    blocks.append({
        "outputfile": bdat[0],
        "allTexBasename": bdat[1]
    })

for resolution in resolutions:
    log("{r}x{r} px".format(r=resolution))

    if not dryRun:
        with redirect_stdout(stdout):
            render.resolution_x = resolution
            render.resolution_y = resolution

    for block in blocks:
        (texSrcAll, texNameAll) = block["allTexBasename"].split(":", 1)

        imagePathAll = os.path.join(texSources[texSrcAll], texNameAll + ".png")
        outputPath = block["outputfile"]
        fullOutputPath = os.path.join(cwd, "output", str(resolution), outputPath)

        if not os.path.isfile(imagePathAll):
            skip = False
            err = "Could not find texture (all): {}".format(imagePathAll)
            if useFallbackTex == True:
                err += " ; A fallback texture will be used"
                imagePathAll = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            log(err)
            errors.append(err)
            if skip:
                continue

        log(outputPath + "...", end="")

        if not dryRun:
            with redirect_stdout(stdout):
                nodeTexAll.image = bpy.data.images.load(imagePathAll)

                bpy.context.scene.render.filepath = fullOutputPath
                bpy.ops.render.render(write_still=True, use_viewport=True)

        log(" Done!")

log("All done!")

if len(errors) > 0:
    log("During operation, {c} error{s} occured:".format(c=len(errors), s=("s" if len(errors) != 1 else "")))
    for err in errors:
        log("  " + err)
