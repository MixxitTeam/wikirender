import bpy
import os
import sys
from contextlib import redirect_stdout
sys.path.insert(1, os.path.abspath("./"))
from drivercommon import *

mat = bpy.data.materials.get("MAIN")
nodeTexRight = mat.node_tree.nodes["TexRight"]
nodeTexLeft = mat.node_tree.nodes["TexLeft"]
nodeTexTop = mat.node_tree.nodes["TexTop"]
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
        "rightTexBasename": bdat[1],
        "leftTexBasename": bdat[2],
        "topTexBasename": bdat[3]
    })

for resolution in resolutions:
    log("{r}x{r} px".format(r=resolution))

    if not dryRun:
        with redirect_stdout(stdout):
            render.resolution_x = resolution
            render.resolution_y = resolution

    for block in blocks:
        (texSrcRight, texNameRight) = block["rightTexBasename"].split(":", 1)
        (texSrcLeft, texNameLeft) = block["leftTexBasename"].split(":", 1)
        (texSrcTop, texNameTop) = block["topTexBasename"].split(":", 1)

        imagePathRight = os.path.join(texSources[texSrcRight], texNameRight + ".png")
        imagePathLeft = os.path.join(texSources[texSrcLeft], texNameLeft + ".png")
        imagePathTop = os.path.join(texSources[texSrcTop], texNameTop + ".png")
        outputPath = block["outputfile"]
        fullOutputPath = os.path.join(cwd, "output", str(resolution), outputPath)

        if not os.path.isfile(imagePathRight):
            skip = False
            err = "Could not find texture (right): {}".format(imagePathRight)
            if useFallbackTex == True:
                err += " ; A fallback texture will be used"
                imagePathRight = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            log(err)
            errors.append(err)
            if skip:
                continue

        if not os.path.isfile(imagePathLeft):
            skip = False
            err = "Could not find texture (left): {}".format(imagePathLeft)
            if useFallbackTex == True:
                err += " ; A fallback texture will be used"
                imagePathLeft = os.path.join(cwd, "missingno.png")
            else:
                err += " ; Skipping this block"
                skip = True
            log(err)
            errors.append(err)
            if skip:
                continue

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

        log(outputPath + "...", end="")

        if not dryRun:
            with redirect_stdout(stdout):
                nodeTexRight.image = bpy.data.images.load(imagePathRight)
                nodeTexLeft.image = bpy.data.images.load(imagePathLeft)
                nodeTexTop.image = bpy.data.images.load(imagePathTop)

                bpy.context.scene.render.filepath = fullOutputPath
                bpy.ops.render.render(write_still=True, use_viewport=True)

        log(" Done!")

log("All done!")

if len(errors) > 0:
    log("During operation, {c} error{s} occured:".format(c=len(errors), s=("s" if len(errors) != 1 else "")))
    for err in errors:
        log("  " + err)
