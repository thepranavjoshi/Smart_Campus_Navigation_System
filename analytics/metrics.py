"""
Analytics Metrics
Usage statistics and data analysis for admin dashboard
"""
import config
from utils.csv_handler import read_csv
from collections import Counter, defaultdict
import os


def get_usage_stats():
    """
    Get overall system usage statistics
    """
    users = read_csv(config.USERS_CSV)
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    routes = read_csv(config.ROUTES_CSV)
    locations = read_csv(config.LOCATIONS_CSV)
    
    return {
        'total_users': len(users),
        'total_notifications': len(notifications),
        'total_routes': len(routes),
        'total_locations': len(locations)
    }


def get_user_stats():
    """
    Get user statistics by role
    """
    users = read_csv(config.USERS_CSV)
    role_counts = Counter()
    
    for user in users:
        role = user.get('role', 'unknown').lower()
        if role == 'staff':
            role = 'faculty'
        role_counts[role] += 1
    
    return dict(role_counts)


def get_notification_stats():
    """
    Get notification delivery statistics
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    
    total = len(notifications)
    delivered = sum(1 for n in notifications if n.get('delivered', '').lower() == 'true')
    
    # Message type breakdown
    message_types = Counter(n.get('message', 'Unknown') for n in notifications)
    
    return {
        'total': total,
        'delivered': delivered,
        'pending': total - delivered,
        'delivery_rate': round(delivered / total * 100, 1) if total > 0 else 0,
        'by_type': dict(message_types)
    }


def get_popular_routes():
    """
    Get most frequently used routes (based on route data)
    """
    routes = read_csv(config.ROUTES_CSV)
    
    # Count routes by start-end pairs
    route_counts = Counter()
    for route in routes:
        start = route.get('start_location', '')
        end = route.get('end_location', '')
        route_counts[f"{start} -> {end}"] += 1
    
    return route_counts.most_common(10)


def get_popular_locations():
    """
    Get most connected/popular locations
    """
    routes = read_csv(config.ROUTES_CSV)
    location_counts = Counter()
    
    for route in routes:
        location_counts[route.get('start_location', '')] += 1
        location_counts[route.get('end_location', '')] += 1
    
    return location_counts.most_common(10)


def get_accessibility_stats():
    """
    Get accessibility statistics
    """
    locations = read_csv(config.LOCATIONS_CSV)
    routes = read_csv(config.ROUTES_CSV)
    
    accessible_locations = sum(1 for loc in locations if loc.get('accessible', '').lower() == 'true')
    accessible_routes = sum(1 for r in routes if r.get('accessible', '').lower() == 'true')
    
    return {
        'accessible_locations': accessible_locations,
        'total_locations': len(locations),
        'location_accessibility_rate': round(accessible_locations / len(locations) * 100, 1) if locations else 0,
        'accessible_routes': accessible_routes,
        'total_routes': len(routes),
        'route_accessibility_rate': round(accessible_routes / len(routes) * 100, 1) if routes else 0
    }


def get_building_stats():
    """
    Get statistics by building
    """
    locations = read_csv(config.LOCATIONS_CSV)
    building_data = defaultdict(lambda: {'count': 0, 'accessible': 0, 'floors': set()})
    
    for loc in locations:
        building = loc.get('building', 'Unknown')
        building_data[building]['count'] += 1
        if loc.get('accessible', '').lower() == 'true':
            building_data[building]['accessible'] += 1
        try:
            building_data[building]['floors'].add(int(loc.get('floor', 1)))
        except ValueError:
            pass
    
    result = {}
    for building, data in building_data.items():
        result[building] = {
            'total_locations': data['count'],
            'accessible_locations': data['accessible'],
            'floors': len(data['floors']),
            'max_floor': max(data['floors']) if data['floors'] else 1
        }
    
    return result


def get_peak_times():
    """
    Analyze activity logs for peak usage times
    Returns hourly distribution of activity
    """
    hourly_counts = {str(h).zfill(2): 0 for h in range(24)}
    
    try:
        if os.path.exists(config.ACTIVITY_LOG):
            with open(config.ACTIVITY_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('['):
                        # Extract hour from timestamp like [2024-12-30T17:00:00]
                        try:
                            timestamp = line.split(']')[0].strip('[')
                            if 'T' in timestamp:
                                time_part = timestamp.split('T')[1]
                                hour = time_part.split(':')[0]
                                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                        except (IndexError, ValueError):
                            pass
    except Exception as e:
        print(f"Error analyzing peak times: {e}")
    
    return hourly_counts


def get_route_distance_stats():
    """
    Get route distance statistics
    """
    routes = read_csv(config.ROUTES_CSV)
    
    distances = []
    for route in routes:
        try:
            distances.append(int(route.get('distance_m', 0)))
        except ValueError:
            pass
    
    if not distances:
        return {'min': 0, 'max': 0, 'avg': 0, 'total': 0}
    
    return {
        'min': min(distances),
        'max': max(distances),
        'avg': round(sum(distances) / len(distances), 1),
        'total': len(distances)
    }
