set -u
A=/opt/mirror/mirrorbits/assets
CDN=https://cdnjs.cloudflare.com/ajax/libs
mkdir -p "$A"/fonts "$A"/font-awesome/4.7.0/css "$A"/font-awesome/4.7.0/fonts \
  "$A"/jquery/3.3.1 "$A"/flot/0.8.3 "$A"/flot.tooltip/0.9.0 \
  "$A"/leaflet/1.3.4/images "$A"/leaflet.markercluster/1.4.1
get(){ if curl -fsSL --max-time 40 "$1" -o "$2"; then echo "OK   $2"; else echo "FAIL $1"; fi; }
# Leaflet
get $CDN/leaflet/1.3.4/leaflet.css "$A/leaflet/1.3.4/leaflet.css"
get $CDN/leaflet/1.3.4/leaflet.js  "$A/leaflet/1.3.4/leaflet.js"
for im in marker-icon.png marker-icon-2x.png marker-shadow.png layers.png layers-2x.png; do
  get $CDN/leaflet/1.3.4/images/$im "$A/leaflet/1.3.4/images/$im"; done
# Marker cluster
get $CDN/leaflet.markercluster/1.4.1/MarkerCluster.css         "$A/leaflet.markercluster/1.4.1/MarkerCluster.css"
get $CDN/leaflet.markercluster/1.4.1/MarkerCluster.Default.css "$A/leaflet.markercluster/1.4.1/MarkerCluster.Default.css"
get $CDN/leaflet.markercluster/1.4.1/leaflet.markercluster.js  "$A/leaflet.markercluster/1.4.1/leaflet.markercluster.js"
# jQuery + Flot
get $CDN/jquery/3.3.1/jquery.min.js               "$A/jquery/3.3.1/jquery.min.js"
get $CDN/flot/0.8.3/excanvas.min.js               "$A/flot/0.8.3/excanvas.min.js"
get $CDN/flot/0.8.3/jquery.flot.min.js            "$A/flot/0.8.3/jquery.flot.min.js"
get $CDN/flot/0.8.3/jquery.flot.pie.min.js        "$A/flot/0.8.3/jquery.flot.pie.min.js"
get $CDN/flot.tooltip/0.9.0/jquery.flot.tooltip.min.js "$A/flot.tooltip/0.9.0/jquery.flot.tooltip.min.js"
# Font Awesome 4.7.0
get $CDN/font-awesome/4.7.0/css/font-awesome.min.css "$A/font-awesome/4.7.0/css/font-awesome.min.css"
for f in fontawesome-webfont.woff2 fontawesome-webfont.woff fontawesome-webfont.ttf fontawesome-webfont.eot fontawesome-webfont.svg FontAwesome.otf; do
  get $CDN/font-awesome/4.7.0/fonts/$f "$A/font-awesome/4.7.0/fonts/$f"; done
# Lato via fontsource (jsDelivr) -> renommé au format attendu par le template
FS=https://cdn.jsdelivr.net/npm/@fontsource/lato/files
get $FS/lato-latin-400-normal.woff2 "$A/fonts/lato-v14-latin-regular.woff2"
get $FS/lato-latin-400-normal.woff  "$A/fonts/lato-v14-latin-regular.woff"
get $FS/lato-latin-900-normal.woff2 "$A/fonts/lato-v14-latin-900.woff2"
get $FS/lato-latin-900-normal.woff  "$A/fonts/lato-v14-latin-900.woff"
# Logo OM (plein, blanc)
get https://wiki.openmandriva.org/logo/openmandriva-wh.svg "$A/openmandriva-wh.svg"
echo "=== FICHIERS ==="; find "$A" -type f | sort
