from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, ReviewReport, Rating
from django.db.models import Avg, Count, Sum
from cart.models import Item
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_hidden=False)
    #avg
    avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    rating_count = Rating.objects.filter(movie=movie).count()

    user_rating = None
    if request.user.is_authenticated:
        user_rating_obj = Rating.objects.filter(movie=movie, user=request.user).first()
        if user_rating_obj:
            user_rating = user_rating_obj.rating
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['avg_rating'] = avg_rating
    template_data['rating_count'] = rating_count
    template_data['user_rating'] = user_rating
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        return redirect('movies.show', id=id)
    if not ReviewReport.objects.filter(review=review, reported_by=request.user).exists():
        report = ReviewReport(review=review, reported_by=request.user)
        if request.method == 'POST' and request.POST.get('reason'):
            report.reason = request.POST.get['reason']
        report.save()
        if ReviewReport.objects.filter(review=review).count() >= 3:
            review.is_hidden = True
            review.save()
    return redirect('movies.show', id=id)

@login_required
def create_rating(request, id):
    if request.method == 'POST':
        movie = Movie.objects.get(id=id)
        rating_value = request.POST.get('rating')
        if rating_value:
            rating, created = Rating.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={'rating': int(rating_value)}
            )
    return redirect('movies.show', id=id)
@staff_member_required
def get_best_movies(request):
    template_data = {}
    template_data['title'] = 'Best Performing Movies'
    most_commented_movie = Movie.objects.annotate(
        review_count=Count('review')
    ).order_by('-review_count').first()
    most_purchased_movie = Movie.objects.annotate(
        total_purchased=Sum('item__quantity')
    ).order_by('-total_purchased').first()
    template_data['most_reviewed'] = {
        'movie': most_commented_movie,
        'count': most_commented_movie.review_count if most_commented_movie else 0
    }
    template_data['most_purchased'] = {
        'movie': most_purchased_movie,
        'count': most_purchased_movie.total_purchased if most_purchased_movie else 0
    }
    return render(request, 'movies/admin_movies.html', {'template_data': template_data})
