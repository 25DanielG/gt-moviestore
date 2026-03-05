from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import json

from accounts.models import UserProfile
from cart.models import Item

# Latitude and longitude for each region
REGION_DATA = {
    'NA': {'name': 'North America', 'lat': 40.0, 'lon': -100.0},
    'EU': {'name': 'Europe', 'lat': 50.0, 'lon': 10.0},
    'AS': {'name': 'Asia', 'lat': 34.0479, 'lon': 100.6197},
    'SA': {'name': 'South America', 'lat': -8.7832, 'lon': -55.4915},
    'AF': {'name': 'Africa', 'lat': 5.0, 'lon': 20.0},
    'OC': {'name': 'Oceania', 'lat': -22.7359, 'lon': 140.0188},
    'ME': {'name': 'Middle East', 'lat': 26.3351, 'lon': 50.1313},
}

@login_required
def index(request):
    template_data = {}
    template_data['title'] = 'Popularity Map'
    try:
        user_profile = request.user.userprofile
        template_data['user_region'] = user_profile.region
    except UserProfile.DoesNotExist:
        template_data['user_region'] = 'NA' # default to north america
    
    return render(request, 'popularity_map/index.html', {'template_data': template_data})

def api_regions(request):
    try:
        user_profile = request.user.userprofile
        user_region = user_profile.region
    except UserProfile.DoesNotExist:
        user_region = None
    
    # get the sum of quantities per region, movie
    results = (
        Item.objects
        .filter(order__user__userprofile__isnull=False)
        .values(
            'movie__id',
            'movie__name',
            'order__user__userprofile__region'
        )
        .annotate(total=Sum('quantity'))
        .order_by('total')
    )
    
    region_data = {}
    for result in results:
        region_code = result['order__user__userprofile__region']
        if region_code not in region_data:
            region_data[region_code] = {'total_purchases': 0, 'movies': []}
        count = result['total']
        region_data[region_code]['total_purchases'] += count
        region_data[region_code]['movies'].append({
            'movie_id': result['movie__id'],
            'movie_name': result['movie__name'],
            'total': count
        })
    
    regions = []
    for region_code, region_info in REGION_DATA.items():
        region_movies = region_data.get(region_code, {'total_purchases': 0, 'movies': []})
        top_movies = sorted(region_movies['movies'], key=lambda x: x['total'], reverse=True)[:5]
        regions.append({
            'code': region_code,
            'name': region_info['name'],
            'lat': region_info['lat'],
            'lon': region_info['lon'],
            'total_purchases': region_movies['total_purchases'],
            'top_movies': top_movies
        })

    return JsonResponse({'user_region': user_region, 'regions': regions}, safe=False)