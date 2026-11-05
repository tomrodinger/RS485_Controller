# RS485 Controller product photography

Four views selected from the owner's SharePoint archive, downloaded 2026-10-26. The views originate from photographs of the actual product. On 2026-11-04, all four views received AI-assisted background edits using the built-in imagegen tool. Their JPEG and WebP versions now have white backgrounds.

For each view, `.jpg` is a high-quality, metadata-free derivative; `.webp` is the full-resolution web version; `-800.webp` fits within 800 × 800 pixels. Orientation is normalized. `with-antenna-white.png` is the lossless edited antenna-view master at 1380 × 1140 pixels. The other three views have lossless `*-cutout.png` masters at 1254 × 1254 pixels with genuine alpha transparency. ImageMagick composites these cutouts onto pure white for the JPEG/WebP derivatives consumed by the datasheet and product documentation. The antenna view's near-white backdrop is normalized to pure white too. Original photo filenames and source hashes remain in the manifest, alongside edit provenance and derivative hashes.

The exact built-in imagegen prompts are retained beside the images:

- [Antenna-connected view](with-antenna-background-prompt.txt)
- [Component-side cover view](component-side-background-prompt.txt)
- [Ports view](ports-background-prompt.txt)
- [Label-side view](label-side-background-prompt.txt)

Recommended primary image for showing the supplied antenna: `with-antenna.webp`. The datasheet cover uses `component-side.jpg` as its single detailed board-only view; its final photo page shows the antenna-connected, ports and label-side views.

To recreate the published derivatives from the retained masters, run from the repository root with ImageMagick installed. This does not require another image-generation request:

```sh
photo_root=images/rs485-controller
for view in with-antenna component-side ports label-side; do
  if [ "$view" = with-antenna ]; then
    master="$photo_root/with-antenna-white.png"
  else
    master="$photo_root/$view-cutout.png"
  fi
  magick "$master" -background white -alpha remove -alpha off -strip -sampling-factor 4:4:4 -quality 96 "$photo_root/$view.jpg"
  magick "$master" -background white -alpha remove -alpha off -strip -quality 94 "$photo_root/$view.webp"
  magick "$master" -background white -alpha remove -alpha off -resize '800x800>' -strip -quality 90 "$photo_root/$view-800.webp"
done
```

The edited dimensions differ from the original archive photos; use `manifest.json` rather than assuming the old sizes. Original full-resolution JPEG derivatives remain in Git history, including commit `ec4ad6f69b8118686cfa3072b01a84e20ae843a9`. Use those originals as the source if a future edit needs to start over.

Example immutable URL pattern:

`https://raw.githubusercontent.com/tomrodinger/RS485_Controller/<commit>/images/rs485-controller/with-antenna.webp`

Replace `<commit>` with the desired full commit SHA. Use the manifest alt text for accessible product images.
