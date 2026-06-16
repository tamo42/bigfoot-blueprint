const fs = require('fs');
const https = require('https');
const d3 = require('d3-geo');

const url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json';

https.get(url, (res) => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => {
    const geojson = JSON.parse(body);
    // Filter for Georgia (STATE FIPS code 13)
    const gaFeatures = geojson.features.filter(f => f.properties.STATE === '13');
    
    // Fit projection to Georgia bounding box
    const projection = d3.geoMercator()
                         .fitSize([800, 800], { type: "FeatureCollection", features: gaFeatures });
    const pathGenerator = d3.geoPath().projection(projection);

    let svgPaths = '';
    
    gaFeatures.forEach(feature => {
      const name = feature.properties.NAME;
      const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      const d = pathGenerator(feature);
      
      svgPaths += `
        <a href={\`/\${'${slug}'}-county\`}>
          <path 
            d="${d}" 
            class="county-path" 
            data-name="${name}"
          >
            <title>${name} County</title>
          </path>
        </a>`;
    });

    const astroComponent = `---
// Generated Georgia County Map SVG component
---
<div class="county-map-container">
  <svg viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg" class="georgia-map" role="group" aria-label="Interactive map of Georgia counties">
    ${svgPaths}
  </svg>
</div>

<style>
  .county-map-container {
    width: 100%;
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
    background: var(--bg-primary, #0f172a);
    border-radius: 8px;
    border: 1px solid var(--border-color, #334155);
  }
  .georgia-map {
    width: 100%;
    height: auto;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
  }
  .county-path {
    fill: hsla(218, 28%, 25%, 0.8);
    stroke: var(--border-color, #1e293b);
    stroke-width: 1;
    transition: all 0.2s ease;
    cursor: pointer;
  }
  .county-path:hover {
    fill: var(--accent-emerald, #10b981);
    stroke: #ffffff;
    stroke-width: 2;
  }
  a:focus .county-path {
    fill: var(--accent-emerald, #10b981);
    stroke: #ffffff;
    outline: none;
  }
</style>
`;

    // Ensure directory exists or write to the file
    const targetFile = 'c:\\\\Users\\\\tamo4\\\\git\\\\bigfoot-sites\\\\macongreasetrap.com\\\\src\\\\components\\\\GeorgiaCountyMap.astro';
    fs.writeFileSync(targetFile, astroComponent);
    console.log('Successfully generated GeorgiaCountyMap.astro with ' + gaFeatures.length + ' counties.');
  });
}).on('error', (e) => {
  console.error(e);
});
