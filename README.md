# Allotment Wiki Rendering

This is an internal tool used to batch-render all previews of blocks for the Allotment wiki. I though it might be useful to at least one person out there, so I'm publishing it here.

## Requirements

This *should* work on pretty much any OS, although it was only tested on Windows 10.

In terms of software installed, you need:

* Blender 2.93 or newer (tested with Blender 2.93)
* PHP 7.4 or newer (tested with PHP 7.4.1)

Please note that PHP must be in your `%PATH%`/`$PATH`. To verify this, open a command prompt/terminal
and type `php -v`. Alternatively, the script `renderall.bat`/`renderall.sh` has to be changed to
include the full path of PHP.

## Usage

### Setting up Blender path

First of all, open up `vars.php` and edit the definition for `BLENDER_PATH` to point to your Blender executable.

### Executing

On Windows, open a command prompt or PowerShell inside of this folder and execute:

```
>renderall
```

for CMD or

```
PS > .\renderall.bat
```

for PowerShell.

On GNU/Linux and other *NIX systems you probably first have to make the `renderall.sh` script executable by using the following command:

```
$ chmod +x ./renderall.sh
```

You then only have to call the script by using

```
$ ./renderall.sh
```

Alternatively, you can also directly call the PHP script by using

```
php renderall.php
```

### Drivers

This script uses the concept of drivers, with each driver basically providing one type of block.
A good rule of thumb is: One driver for each block model.

All drivers live inside of the `drivers/` folder. Each driver consists of one `blend`file and
one accompanying Python script. The `blend`file contains the block model and node setup for
texturing. The Python script gets run by Blender and populates certain node values and then
renders the scene to a specified output file.

### Block list

All blocks that need to be rendered are listed inside of `blocks.txt`. This file can be easily
opened by any text editor. Please make sure to set your editor to indent using **Tabs** at **8 characters wide**. If you are using a text editor which supports modelines (such as Vim or VSCode with the [Modelines extension](https://marketplace.visualstudio.com/items?itemName=chrislajoie.vscode-modelines)) this should happen automatically.

The file has a pretty straight-forward structure:  
* Lines end with `\n`
* Line comments start with either `#` or `//`
* There are no block comments
* Empty lines are ignored (an empty line is a line with only 0 or more ASCII whitespace characters (namely `SPACE`, `TAB`, `\r` or `\n`))
* Each line contains the following fields, each separated by one or more `TAB`, in the following order:
  * The driver name (for a full list of drivers, see `doc/drivers.txt`)
  * The output file path (including `.png` extension) relative to this folder. These files will be placed inside of an `output/<resolution>` folder. So `allotment/elder_planks.png` for example might result in `output/256/allotment/elder_planks.png`. (More on resolution sub folders below)
  * One or more texture identifiers. These consist of a *texture source* and a *texture name*. The identifier has the following format: `<source>:<name>`. Sources are folders in which textures files can be referenced from and are defined inside of `vars.txt` (see below). In addition to these sources, drivers also should provide a source called `in`, which points to the `input/` folder. This can be used to reference textures which are not part of Minecraft or a mod.

With this in mind, here is an example of how a line in `blocks.txt` might look like:

```
block	minecraft/oak_log.png	mc:oak_log	mc:oak_log	mc:oak_log_top
```

### Settings (aka `vars.txt`)

Settings are stored inside a file called `vars.txt`. This file has a simple key-value pair structure.
* Lines end with `\n`
* Line comments begin with either `#` or `//`
* There are no block comments
* Each line contains one key-value pair
* The beginning of a value is denoted by an equals sign (`=`)
* Keys cannot contain an equals sign, but values can

The settings file must contain the following settings:

* `Resolutions`  
  Default value: `256,32`  
  Type: List  
  
  This contains a list of resolutions (in pixels) which should be output
* `Brightness.RightFace`  
  Default value: `0.396078431372549`  
  Type: Number  
  
  Indicates the brightness of the right block face, where 1.0 is as bright as the texture and 0.0 is fully black.
* `Brightness.LeftFace`  
  Default value: `0.6862745098039216`  
  Type: Number  

  Indicates the brightness of the left block face, where 1.0 is as bright as the texture and 0.0 is fully black.
* `Brightness.TopFace`  
  Default value: `1`  
  Type: Number  

  Indicates the brightness of the top block face, where 1.0 is as bright as the texture and 0.0 is fully black.
* `UseFallbackTexture`
  Default value: `False`  
  Type: Boolean  
  
  If `True` uses a fallback texture (namely `missigno.png` when a texture cannot be found). If `False`, skips the block which has missing textures.

In addition to that, the settings file may also contain the following settings:

* `TextureDir.<Name>`  
  Default value: n/a  
  Type: String
  
  Defines a texture source named `<Name>`.

Some drivers might also define their own settings, which will also be read from `vars.txt`.

It is recommended to point a texture source named `mc` to the blocks folder inside of an unpacked Minecraft installation.
