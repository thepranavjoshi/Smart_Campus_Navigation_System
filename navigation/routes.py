"""
Navigation Routes
Navigation endpoints for route finding
"""
from flask import render_template, request, flash, session
from navigation import navigation_bp
from navigation.pathfinder import (
    get_unique_locations, 
    dijkstra_shortest_path, 
    get_alternative_routes,
    generate_directions,
    path_to_text
)
from navigation.accessibility import (
    get_accessible_path, 
    get_accessibility_warnings,
    check_lift_status
)
from auth.permissions import login_required, visitor_allowed
from utils.time_utils import get_timestamp
import os
import config


def log_navigation(user_id, start, end, success):
    """
    Log navigation search for analytics
    """
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        timestamp = get_timestamp()
        status = "SUCCESS" if success else "NO_PATH"
        log_entry = f"[{timestamp}] User {user_id}: {start} -> {end} ({status})\n"
        
        with open(config.ACTIVITY_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing navigation log: {e}")


@navigation_bp.route('/', methods=['GET', 'POST'])
@login_required
def navigate():
    """
    Main navigation page
    """
    locations = get_unique_locations()
    result = None
    alternatives = []
    warnings = []
    
    if request.method == 'POST':
        start = request.form.get('start_location', '')
        end = request.form.get('end_location', '')
        accessible_only = request.form.get('accessible_only') == 'on'
        
        if not start or not end:
            flash('Please select both start and end locations.', 'warning')
        elif start == end:
            flash('Start and end locations are the same. You\'re already there!', 'info')
        else:
            user_id = session.get('user_id', 0)
            
            # Find shortest path
            if accessible_only:
                path, distance, route_ids = get_accessible_path(start, end)
            else:
                path, distance, route_ids = dijkstra_shortest_path(start, end)
            
            if path:
                # Generate directions
                directions = generate_directions(path)
                
                # Check accessibility warnings
                if not accessible_only:
                    warnings = get_accessibility_warnings(path)
                
                result = {
                    'path': path,
                    'distance': distance,
                    'directions': directions,
                    'route_text': path_to_text(path, distance)
                }
                
                # Get alternative routes
                alt_routes = get_alternative_routes(start, end, count=2, accessible_only=accessible_only)
                for alt_path, alt_dist, alt_ids in alt_routes[1:]:  # Skip first (same as shortest)
                    if alt_path != path:
                        alternatives.append({
                            'path': alt_path,
                            'distance': alt_dist,
                            'directions': generate_directions(alt_path)
                        })
                
                log_navigation(user_id, start, end, True)
                flash(f'Route found! Distance: {distance} meters', 'success')
            else:
                log_navigation(user_id, start, end, False)
                flash('No route found between these locations.', 'danger')
                
                # Suggest accessible route if normal route failed
                if not accessible_only:
                    flash('Try enabling "Accessible routes only" option.', 'info')
    
    # Get lift status for display
    lift_status = check_lift_status()
    
    return render_template('navigation.html', 
                         locations=locations,
                         result=result,
                         alternatives=alternatives,
                         warnings=warnings,
                         lift_status=lift_status)


@navigation_bp.route('/quick/<start>/<end>')
@login_required
def quick_navigate(start, end):
    """
    Quick navigation API endpoint
    """
    path, distance, route_ids = dijkstra_shortest_path(start, end)
    
    if path:
        return {
            'success': True,
            'path': path,
            'distance': distance,
            'directions': generate_directions(path)
        }
    else:
        return {
            'success': False,
            'error': 'No route found'
        }
