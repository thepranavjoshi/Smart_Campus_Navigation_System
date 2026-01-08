"""
Pathfinder - Navigation Logic
Shortest path and alternative routes using Dijkstra's algorithm
"""
import config
from utils.csv_handler import read_csv
from collections import defaultdict
import heapq


def get_locations():
    """
    Get all campus locations from CSV
    """
    locations = read_csv(config.LOCATIONS_CSV)
    return locations


def get_unique_locations():
    """
    Get unique location names from routes
    """
    routes = read_csv(config.ROUTES_CSV)
    locations = set()
    for route in routes:
        locations.add(route.get('start_location', ''))
        locations.add(route.get('end_location', ''))
    return sorted([loc for loc in locations if loc])


def build_graph(accessible_only=False):
    """
    Build adjacency graph from routes CSV
    Returns: dict of {location: [(neighbor, distance, route_id, accessible), ...]}
    """
    routes = read_csv(config.ROUTES_CSV)
    graph = defaultdict(list)
    
    for route in routes:
        start = route.get('start_location', '')
        end = route.get('end_location', '')
        distance = int(route.get('distance_m', 0))
        accessible = route.get('accessible', '').lower() == 'true'
        route_id = route.get('id', '')
        
        # Skip non-accessible routes if filter is on
        if accessible_only and not accessible:
            continue
        
        # Add bidirectional edges
        graph[start].append((end, distance, route_id, accessible))
        graph[end].append((start, distance, route_id, accessible))
    
    return graph


def dijkstra_shortest_path(start, end, accessible_only=False):
    """
    Find shortest path using Dijkstra's algorithm
    Returns: (path, total_distance, route_details) or (None, None, None) if no path
    """
    graph = build_graph(accessible_only)
    
    if start not in graph and start != end:
        return None, None, None
    
    # Priority queue: (distance, current_node, path, route_ids)
    heap = [(0, start, [start], [])]
    visited = set()
    
    while heap:
        distance, current, path, route_ids = heapq.heappop(heap)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == end:
            return path, distance, route_ids
        
        for neighbor, edge_dist, route_id, accessible in graph.get(current, []):
            if neighbor not in visited:
                new_distance = distance + edge_dist
                new_path = path + [neighbor]
                new_route_ids = route_ids + [route_id]
                heapq.heappush(heap, (new_distance, neighbor, new_path, new_route_ids))
    
    return None, None, None


def get_alternative_routes(start, end, count=3, accessible_only=False):
    """
    Get multiple alternative routes
    Returns list of (path, distance, route_details)
    """
    alternatives = []
    graph = build_graph(accessible_only)
    
    # Use modified Dijkstra to find multiple paths
    # Priority queue: (distance, current_node, path, route_ids, used_edges)
    heap = [(0, start, [start], [], frozenset())]
    found_paths = set()
    
    while heap and len(alternatives) < count:
        distance, current, path, route_ids, used_edges = heapq.heappop(heap)
        
        if current == end:
            path_tuple = tuple(path)
            if path_tuple not in found_paths:
                found_paths.add(path_tuple)
                alternatives.append((path, distance, route_ids))
            continue
        
        for neighbor, edge_dist, route_id, accessible in graph.get(current, []):
            edge = frozenset([current, neighbor])
            if edge not in used_edges:
                new_distance = distance + edge_dist
                new_path = path + [neighbor]
                new_route_ids = route_ids + [route_id]
                new_used = used_edges | {edge}
                heapq.heappush(heap, (new_distance, neighbor, new_path, new_route_ids, new_used))
    
    return alternatives


def generate_directions(path, start_name=None, end_name=None):
    """
    Generate textual walking directions from path
    """
    if not path or len(path) < 2:
        return ["You are already at your destination."]
    
    directions = []
    directions.append(f"Start at {path[0]}")
    
    for i in range(1, len(path)):
        prev = path[i-1]
        current = path[i]
        
        if i == len(path) - 1:
            directions.append(f"Arrive at your destination: {current}")
        else:
            directions.append(f"Continue to {current}")
    
    return directions


def path_to_text(path, distance):
    """
    Convert path and distance to readable text
    """
    if not path:
        return "No path found."
    
    text = f"Route: {' -> '.join(path)}\n"
    text += f"Total distance: {distance} meters"
    return text


def check_route_blockages():
    """
    Check for any route blockages (for future expansion)
    Currently returns empty list - would integrate with notification system
    """
    # This could be expanded to check notifications for blocked routes
    return []
