# Camino Francés Geocoding Project

This project contains the geocoded data and visualization for the Camino Francés pilgrimage route.

## Files

- `camino_frances_geocoded.json` - Original geocoded data with some coordinate errors
- `camino_frances_geocoded_corrected.json` - Corrected data with manually verified coordinates
- `camino_frances_map.html` - Interactive map visualization
- `geocode_camino_frances.py` - Script to geocode the original JSON data
- `visualize_camino.py` - Script to create the interactive map
- `fix_coordinates.py` - Script to apply manual coordinate corrections

## Manual Coordinate Corrections

During the visual review of the geocoded data, several coordinate errors were identified and manually corrected. The following stops had incorrect coordinates that were replaced with verified correct coordinates from Google Maps:

### Stage 14: Hornillos del Camino to Castrojeriz
- **San Bol**: 
  - Old: (42.28057926813867, -3.982742810767702)
  - New: (42.32365504328446, -3.990781695387196)

### Stage 26: Villafranca del Bierzo to O Cebreiro
- **La Laguna**: 
  - Old: (42.0552873, -2.4244226)
  - New: (42.70126950462187, -7.021868063322811)

### Stage 27: O Cebreiro to Triacastela
- **Linares**: 
  - Old: (42.4942476, -7.39674)
  - New: (42.69913272721601, -7.073770644328744)

### Stage 28A: Triacastela to Sarria (via San Xil)
- **A Balsa**: 
  - Old: (43.1285555, -8.8311072)
  - New: (42.766042678503005, -7.2537276139561895)

### Stage 29: Sarria to Portomarin
- **Marzan**: 
  - Old: (42.5989736, -7.506281199999999)
  - New: (42.76879522844872, -7.476308531127457)
- **Vilacha**: 
  - Old: (42.4688033, -7.3926187)
  - New: (42.79547043777973, -7.603233068665937)

### Stage 30: Portomarin to Palas de Rei
- **O Hospital**: 
  - Old: (41.9296711, -7.3627974)
  - New: (42.840954441423214, -7.734579480863954)
- **Lestedo**: 
  - Old: (42.7972751, -8.469101)
  - New: (42.872145522854524, -7.814158843458301)

### Stage 31: Palas de Rei to Arzua
- **Casanova**: 
  - Old: (42.8731875, -8.1579975)
  - New: (42.87874591813561, -7.928150317049294)

### Stage 32: Arzua to O Pedrouzo
- **A Brea**: 
  - Old: (42.875793, -7.8360304)
  - New: (42.91860389918316, -8.305194057330725)
- **A Rua**: 
  - Old: (42.3952985, -7.1141153)
  - New: (42.914572344387096, -8.350234844778358)

## Total Corrections Made

**11 coordinate corrections** were applied to fix geocoding mistakes that placed stops in incorrect locations (often hundreds of kilometers away from their actual positions along the Camino Francés route).

## Usage

1. **Use the corrected data**: `camino_frances_geocoded_corrected.json` contains the accurate coordinates
2. **View the map**: Open `camino_frances_map.html` in a web browser to see the corrected route
3. **Regenerate the map**: If needed, run `visualize_camino.py` on the corrected data to update the visualization

## Notes

- The original geocoding was performed using Google Maps API with the search format "place_name, town, country"
- Some locations had similar names in different regions, causing the API to return incorrect coordinates
- All corrected coordinates were manually verified using Google Maps to ensure accuracy
- The corrected data maintains the exact same JSON structure with only the coordinate values updated
