import bpy
import os
import sys
from contextlib import redirect_stdout
sys.path.insert(1, os.path.abspath("./"))
from drivercommon import *

mat = bpy.data.materials.get("MAIN")
nodeTexTop = mat.node_tree.nodes["TexTop"]
nodeTexBottom = mat.node_tree.nodes["TexBottom"]
nodeBrRight = mat.node_tree.nodes["BrRight"]
nodeBrLeft = mat.node_tree.nodes["BrLeft"]

render = bpy.data.scenes[0].render

nodeBrRight.outputs[0].default_value = float(vvars["Brightness.RightFace"])
nodeBrLeft.outputs[0].default_value = float(vvars["Brightness.LeftFace"])

errors = []
blocks = []

for bdat in blockData:
    blocks.append({
        "outputfile": bdat[0],
        "topTexBasename": bdat[1],
        "bottomTexBasename": bdat[2]
    })

for resolution in resolutions:
    log("{r}x{r} px".format(r=resolution))

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
            if useFallbackTex == True:
                err += " ; A fallback texture will be used"
                imagePathTop = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            log(err)
            errors.append(err)
            if skip:
                continue

        if not os.path.isfile(imagePathBottom):
            skip = False
            err = "Could not find texture (bottom): {}".format(imagePathBottom)
            if useFallbackTex == True:
                err += " ; A fallback texture will be used"
                imagePathBottom = os.path.join(cwd, "missingno.png")
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
                nodeTexTop.image = bpy.data.images.load(imagePathTop)
                nodeTexBottom.image = bpy.data.images.load(imagePathBottom)

                bpy.context.scene.render.filepath = fullOutputPath
                bpy.ops.render.render(write_still=True, use_viewport=True)

        log(" Done!")

log("All done!")

if len(errors) > 0:
    log("During operation, {c} error{s} occured:".format(c=len(errors), s=("s" if len(errors) != 1 else "")))
    for err in errors:
        log("  " + err)
