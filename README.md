* Prepare

`mkdir street_view_images`
`mkdir merged_images`

* Download street view at grid positions

`python3 download.py`
* Merge downloaded views (because each position will have multiple image segments)

`python3 merge_images.py`
