# Krita reference plugin

This is a quick and dirty plugin to replace the removed Reference Images Docker in Krita 4.0.0

## A temporary solution

As said at https://krita.org/en/item/krita-4-0-0-released/, the removal is only temporary:

"The Reference Images Docker has been removed. It was too easy to crash it if invalid image files where present. In Krita 4.1 it will be replaced by a new reference images tool."

## How to install

Open Krita, in Settings -> Manage Resources click on the Open Resource Folder button.

Copy-paste all files from https://github.com/antoine-roux/krita-plugin-reference/archive/master.zip in the pykrita folder and restart Krita.

## How to enable

Enable the plugin in Settings -> Configure Krita -> Python Plugin Manager (Reference)

Check Settings -> Dockers -> Reference Docker

## How to use

### Load an image

Click on Open and choose an image. Beware, no verification is done on the format... You've been warned!

### Move the reference and zoom

You can grab the reference to move it (with any mouse button, left/right/middle... don't care).

Use the wheel or press on Ctrl and drag up-down to zoom.

### Pick a color

Just click on the wanted part of the reference, you can shift your selection by some pixels.

A color preview is displayed on the top of the Docker.
