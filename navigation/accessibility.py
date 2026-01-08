"""
Accessibility - Lift and Disability Route Checks
Accessible routing and lift status management
"""
import config
from utils.csv_handler import read_csv
from navigation.pathfinder import dijkstra_shortest_path, get_alternative_routes


# Simulated lift status (would be dynamic in production)
_lift_status = {
    'Main': True,
    'Science': True,
    'Engineering': True,
    'Arts': True,
    'Commons': True,
    'Recreation': False  # Example: Recreation building lift is down
}


def get_accessible_locations():
    """
    Get all accessible locations
    """
    locations = read_csv(config.LOCATIONS_CSV)
    accessible = []
    for loc in locations:
        if loc.get('accessible', '').lower() == 'true':
            accessible.append(loc)
    return accessible


def filter_accessible_routes(routes):
    """
    Filter routes to only include accessible ones
    """
    return [r for r in routes if r.get('accessible', '').lower() == 'true']


def check_lift_status(building=None):
    """
    Check lift status for building(s)
    """
    if building:
        return _lift_status.get(building, True)
    return _lift_status.copy()


def set_lift_status(building, status):
    """
    Update lift status (admin function)
    """
    if building in _lift_status:
        _lift_status[building] = status
        return True
    return False


def get_accessible_path(start, end):
    """
    Find path using only accessible routes
    """
    return dijkstra_shortest_path(start, end, accessible_only=True)


def get_building_accessibility(building):
    """
    Get accessibility info for a building
    """
    locations = read_csv(config.LOCATIONS_CSV)
    building_locs = [loc for loc in locations if loc.get('building', '') == building]
    
    if not building_locs:
        return None
    
    accessible_count = sum(1 for loc in building_locs if loc.get('accessible', '').lower() == 'true')
    
    return {
        'building': building,
        'total_locations': len(building_locs),
        'accessible_locations': accessible_count,
        'lift_working': check_lift_status(building),
        'accessibility_percentage': round(accessible_count / len(building_locs) * 100, 1)
    }


def needs_lift(path, locations_data=None):
    """
    Check if a path requires lift usage (crossing floors)
    """
    if not path or len(path) < 2:
        return False
    
    if locations_data is None:
        locations_data = {loc['name']: loc for loc in read_csv(config.LOCATIONS_CSV)}
    
    floors = []
    for loc in path:
        loc_data = locations_data.get(loc, {})
        floor = loc_data.get('floor', 1)
        try:
            floors.append(int(floor))
        except ValueError:
            floors.append(1)
    
    # Check if there's a floor change
    return len(set(floors)) > 1


def get_accessibility_warnings(path):
    """
    Generate accessibility warnings for a path
    """
    warnings = []
    locations_data = {loc['name']: loc for loc in read_csv(config.LOCATIONS_CSV)}
    
    # Check each location in path
    for loc in path:
        loc_data = locations_data.get(loc, {})
        building = loc_data.get('building', '')
        
        # Check if location is not accessible
        if loc_data.get('accessible', '').lower() != 'true':
            warnings.append(f"Warning: {loc} may not be wheelchair accessible")
        
        # Check lift status for building
        if building and not check_lift_status(building):
            warnings.append(f"Warning: Lift in {building} building is currently not working")
    
    return list(set(warnings))  # Remove duplicates
