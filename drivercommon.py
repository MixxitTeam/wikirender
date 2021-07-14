import re
import os
import io
import sys
import inspect

def log(msg, end="\n"):
    print(msg, end=end, file=sys.stderr)

def get_caller_info():
    caller_filename_full = False
    if __name__ != '__main__':
        for frame in inspect.stack()[1:]:
            # HACK Breaks if this whole thing is contained
            # inside of a folder which contains the
            # word "drivers". I need to come up with a
            # better solution
            if "drivers" in frame.filename:
                caller_filename_full = frame.filename
                break

    if caller_filename_full == False:
        return None

    caller_filename_only = os.path.splitext(os.path.basename(caller_filename_full))[0]

    return caller_filename_only

THISDRIVER = get_caller_info()
log("Driver name: " + THISDRIVER + "-"*20)

__onlygroup = sys.argv[-1] if len(sys.argv) >= 2 and sys.argv[-2] == "--only-group" else False

def list_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

dryRun = False

stdout = io.StringIO()

strBlocks = ""
strVars = ""

if dryRun:
    log("="*20 + " Dry run " + "="*20)

with open("blocks.txt", "r") as f:
    strBlocks = f.read()

with open("vars.txt", "r") as f:
    strVars = f.read()

lnsBlocks = strBlocks.split("\n")
blockData = []

currGroupName = None

# TODO Groups!
for ln in lnsBlocks:
    if (ln.startswith("#") or ln.startswith("//") or ln.strip(" \t\r\n") == ""):
        continue
    if ln.startswith("[begin: ") and ln.endswith("]"):
        if __onlygroup != False and currGroupName == None:
            # start of group
            currGroupName = ln[8:-1]
        continue
    if ln.startswith("[end: ") and ln.endswith("]"):
        if __onlygroup != False and currGroupName != None and ln == "[end: " + currGroupName + "]":
            # end of group
            currGroupName = None
        continue
    fields = re.split(r"\t+", ln)
    if fields[0] != THISDRIVER:
        continue

    if (__onlygroup == False) or (__onlygroup != False and currGroupName == __onlygroup):
        blockData.append(fields[1:])

lnsVars = strVars.split("\n")
vvars = {}

for ln in lnsVars:
    if (ln.startswith("#") or ln.startswith("//") or ln.strip(" \t\r\n") == ""):
        continue
    fields = ln.split("=", 1)
    vvars[fields[0]] = fields[1]

texSources = {
    "in": os.path.join(os.getcwd(), "input")
}

for key, value in vvars.items():
    if key.startswith("TextureDir."):
        srcname = key[11:]
        texSources[srcname] = value

resolutions = [int(x) for x in vvars["Resolutions"].split(",")]
useFallbackTex = vvars["UseFallbackTexture"] == "True"
subdirs = list_unique(["/".join(block[0].split("/")[:-1]) for block in blockData])
cwd = os.getcwd()

for res in [str(r) for r in resolutions]:
    for subdir in subdirs:
        dirn = os.path.join(cwd, "output", res, subdir)
        if not os.path.isdir(dirn):
            if not dryRun:
                os.makedirs(dirn)

if dryRun:
    log("="*20 + " Dry run " + "="*20)

log("Settings: ")
log("     resolutions: {}".format(";".join([str(x) for x in resolutions])))
log("  useFallbackTex: {}".format(useFallbackTex))
