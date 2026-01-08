"""
Analytics Visualizations
Chart generation using matplotlib and plotly
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import os
import config
from analytics.metrics import (
    get_user_stats, 
    get_notification_stats, 
    get_popular_locations,
    get_peak_times,
    get_accessibility_stats,
    get_building_stats
)


def ensure_static_dir():
    """
    Ensure static images directory exists
    """
    images_dir = os.path.join(config.STATIC_DIR, 'images', 'charts')
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def generate_user_distribution_chart():
    """
    Generate pie chart of user distribution by role
    """
    stats = get_user_stats()
    
    if not stats:
        return None
    
    labels = list(stats.keys())
    values = list(stats.values())
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)], startangle=90)
    ax.set_title('User Distribution by Role', fontsize=14, fontweight='bold')
    
    chart_path = os.path.join(ensure_static_dir(), 'user_distribution.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return 'images/charts/user_distribution.png'


def generate_notification_chart():
    """
    Generate bar chart of notification delivery status
    """
    stats = get_notification_stats()
    
    categories = ['Delivered', 'Pending']
    values = [stats['delivered'], stats['pending']]
    colors = ['#4CAF50', '#FF5722']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(categories, values, color=colors)
    ax.set_ylabel('Count')
    ax.set_title('Notification Delivery Status', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                str(val), ha='center', fontsize=12)
    
    chart_path = os.path.join(ensure_static_dir(), 'notification_status.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return 'images/charts/notification_status.png'


def generate_popular_locations_chart():
    """
    Generate horizontal bar chart of popular locations
    """
    locations = get_popular_locations()
    
    if not locations:
        return None
    
    names = [loc[0] for loc in locations[:8]]
    counts = [loc[1] for loc in locations[:8]]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(names, counts, color='#2196F3')
    ax.set_xlabel('Number of Routes')
    ax.set_title('Most Connected Locations', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    chart_path = os.path.join(ensure_static_dir(), 'popular_locations.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return 'images/charts/popular_locations.png'


def generate_peak_times_chart():
    """
    Generate line chart of activity by hour
    """
    hourly_data = get_peak_times()
    
    hours = list(hourly_data.keys())
    counts = list(hourly_data.values())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(hours, counts, marker='o', linewidth=2, markersize=6, color='#673AB7')
    ax.fill_between(hours, counts, alpha=0.3, color='#673AB7')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Activity Count')
    ax.set_title('Campus Activity by Hour', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    chart_path = os.path.join(ensure_static_dir(), 'peak_times.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return 'images/charts/peak_times.png'


def generate_accessibility_chart():
    """
    Generate accessibility statistics chart
    """
    stats = get_accessibility_stats()
    
    categories = ['Locations', 'Routes']
    accessible = [stats['accessible_locations'], stats['accessible_routes']]
    total = [stats['total_locations'], stats['total_routes']]
    not_accessible = [t - a for t, a in zip(total, accessible)]
    
    x = range(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar([i - width/2 for i in x], accessible, width, label='Accessible', color='#4CAF50')
    bars2 = ax.bar([i + width/2 for i in x], not_accessible, width, label='Not Accessible', color='#F44336')
    
    ax.set_ylabel('Count')
    ax.set_title('Accessibility Overview', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    
    chart_path = os.path.join(ensure_static_dir(), 'accessibility.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return 'images/charts/accessibility.png'


def generate_plotly_dashboard():
    """
    Generate interactive Plotly dashboard HTML
    """
    # User distribution pie chart
    user_stats = get_user_stats()
    fig1 = go.Figure(data=[go.Pie(
        labels=list(user_stats.keys()),
        values=list(user_stats.values()),
        hole=0.4,
        marker_colors=['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']
    )])
    fig1.update_layout(title='User Distribution by Role')
    
    # Notification delivery gauge
    notif_stats = get_notification_stats()
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=notif_stats['delivery_rate'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Notification Delivery Rate (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4CAF50"},
            'steps': [
                {'range': [0, 50], 'color': "#FFEB3B"},
                {'range': [50, 80], 'color': "#8BC34A"},
                {'range': [80, 100], 'color': "#4CAF50"}
            ]
        }
    ))
    
    # Building statistics
    building_stats = get_building_stats()
    buildings = list(building_stats.keys())
    locations_count = [building_stats[b]['total_locations'] for b in buildings]
    accessible_count = [building_stats[b]['accessible_locations'] for b in buildings]
    
    fig3 = go.Figure(data=[
        go.Bar(name='Total Locations', x=buildings, y=locations_count, marker_color='#2196F3'),
        go.Bar(name='Accessible', x=buildings, y=accessible_count, marker_color='#4CAF50')
    ])
    fig3.update_layout(barmode='group', title='Locations by Building')
    
    return {
        'user_chart': fig1.to_html(full_html=False, include_plotlyjs='cdn'),
        'notification_gauge': fig2.to_html(full_html=False, include_plotlyjs=False),
        'building_chart': fig3.to_html(full_html=False, include_plotlyjs=False)
    }


def generate_all_charts():
    """
    Generate all static charts
    """
    charts = {}
    charts['user_distribution'] = generate_user_distribution_chart()
    charts['notification_status'] = generate_notification_chart()
    charts['popular_locations'] = generate_popular_locations_chart()
    charts['peak_times'] = generate_peak_times_chart()
    charts['accessibility'] = generate_accessibility_chart()
    return charts
