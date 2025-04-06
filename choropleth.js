const map = L.map('map', {
  center: [25, 0],
  zoom: 2,
  minZoom: 2,
  maxZoom: 5,
  maxBounds: [[-60, -180], [85, 180]],
  maxBoundsViscosity: 1.0,
  worldCopyJump: false,
  zoomControl: true,
  attributionControl: true
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

const dataSelect = document.getElementById("dataSelect");
const yearSlider = document.getElementById("yearSlider");
const yearValue = document.getElementById("yearValue");

let cropData = [];
let geoLayer;

Papa.parse("final_crop_data.csv", {
  download: true,
  header: true,
  complete: function(results) {
    cropData = results.data.map(d => ({
      region: d.region,
      year: parseInt(d.year),
      yield_hg_ha: parseFloat(d.yield_hg_ha),
      yield_t_ha: parseFloat(d.yield_t_ha),
      rainfall_mm: parseFloat(d.rainfall_mm),
      avg_temp_c: parseFloat(d.avg_temp_c),
      pesticide_t: parseFloat(d.pesticide_t)
    })).filter(d => d.region && !isNaN(d.year));
    drawMap();
  }
});

function drawMap() {
  if (geoLayer) geoLayer.remove();

  fetch("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
    .then(res => res.json())
    .then(geojson => {
      geojson.features = geojson.features.filter(
        feature => feature.properties.name !== "Antarctica"
      );

      const year = parseInt(yearSlider.value);
      const metric = dataSelect.value;
      yearValue.textContent = year;

      const regionMetricMap = {};
      cropData.forEach(row => {
        if (row.year === year && !isNaN(row[metric])) {
          regionMetricMap[row.region] = row[metric];
        }
      });

      function getColor(val, min, max) {
        const percent = (val - min) / (max - min);
        return percent < 0.2 ? '#ffffcc'
             : percent < 0.4 ? '#a1dab4'
             : percent < 0.6 ? '#41b6c4'
             : percent < 0.8 ? '#2c7fb8'
             : '#253494';
      }

      const values = Object.values(regionMetricMap);
      const min = Math.min(...values);
      const max = Math.max(...values);

      geoLayer = L.geoJson(geojson, {
        style: feature => {
          const region = feature.properties.name;
          const val = regionMetricMap[region];
          return {
            fillColor: val !== undefined ? getColor(val, min, max) : '#ccc',
            weight: 1,
            color: '#000',
            fillOpacity: 0.8
          };
        },
        onEachFeature: (feature, layer) => {
          const region = feature.properties.name;
          const val = regionMetricMap[region];
          layer.bindPopup(`<strong>${region}</strong><br>${dataSelect.options[dataSelect.selectedIndex].text}: ${val ?? 'No data'}`);
        }
      }).addTo(map);

      map.fitBounds(geoLayer.getBounds(), {
        padding: [20, 20],
        maxZoom: 4
      });
    });
}

dataSelect.addEventListener("change", drawMap);
yearSlider.addEventListener("input", drawMap);
