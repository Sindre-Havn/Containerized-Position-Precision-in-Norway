import { useMap } from 'react-leaflet';
import { useEffect } from 'react';
import L from 'leaflet';

const FitMapToGeoJson = ({ geoJsonData }) => {
  const map = useMap();

  useEffect(() => {
    if (!Array.isArray(geoJsonData) || geoJsonData.length === 0) return;

    try {
      const validFeatures = geoJsonData.filter(feature =>
        feature &&
        feature.geometry &&
        Array.isArray(feature.geometry.coordinates) &&
        feature.geometry.coordinates.length > 0
      );

      if (validFeatures.length === 0) {
        console.warn("Ingen gyldige geometrier i geoJsonData.");
        return;
      }

      const featureCollection = {
        type: "FeatureCollection",
        features: validFeatures,
      };

      const layer = L.geoJSON(featureCollection);
      const bounds = layer.getBounds();

      if (!bounds.isValid()) {
        console.warn("Bounds er ikke gyldige.");
        return;
      }

      map.fitBounds(bounds, {
        padding: [50, 50],
        maxZoom: 15,
        animate: true,
      });
    } catch (err) {
      console.error("Failed to fit map to geoJson:", err);
    }

  }, [geoJsonData, map]);

  return null;
};

export default FitMapToGeoJson;