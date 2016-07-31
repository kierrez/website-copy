from django.shortcuts import render, get_object_or_404

from .models import Entry, Genre, Archive, Season, Episode, Type, Director
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from django.db.models import Count


def home(request):
    all_movies = Entry.objects.filter(type=Type.objects.get(name='movie').id)
    all_series = Entry.objects.filter(type=Type.objects.get(name='series').id)
    context = {
        'ratings': Entry.objects.all().order_by('-rate_date')[:10],
        'info': {
            'last_movie': all_movies.order_by('-rate_date')[0],
            'last_series': all_series.order_by('-rate_date')[0],
            'last_good': all_movies.filter(rate__gte=9).order_by('-rate_date')[0],
            'movie_count': all_movies.count(),
            'series_count': all_series.count(),
        }
    }
    return render(request, 'home.html', context)


def explore(request):
    entries = Entry.objects.all().order_by('-rate_date', '-inserted_date')
    query = request.GET.get('q')
    if query:
        entries = entries.filter(
            Q(name__startswith=query) |
            Q(year__startswith=query)
            ).distinct()
            # https://docs.djangoproject.com/en/1.9/topics/db/queries/#complex-lookups-with-q-objects

    paginator = Paginator(entries, 50)
    page = request.GET.get('page')
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    context = {
        'ratings': ratings,
        'archive': Archive.objects.all(),
    }
    return render(request, 'entry.html', context)


def book(request):
    return render(request, 'book.html')


def about(request):
    return render(request, 'about.html', {'archive': Archive.objects.all()})


def entry_details(request, slug):
    # MyModel.objects.extra(select={'length':'Length(name)'}).order_by('length')
    # def get_seasons(imdb_id):
    #     entry = Entry.objects.get(const=imdb_id)
    #     seasons = Season.objects.filter(entry=entry)
    #     season_episodes = []
    #     for s in seasons:
    #         episodes = Episode.objects.filter(season=s)
    #         season_episodes.append([s.number, episodes])
    #     return season_episodes
    requested_obj = get_object_or_404(Entry, slug=slug)
    context = {
        'entry': requested_obj,
        'archive': Archive.objects.filter(const=requested_obj.const).order_by('-rate_date'),
        'now': {
            'day': str(timezone.now().day),
            'month': str(timezone.now().month),
            'year': str(timezone.now().year),
        }
    }
    # if context['entry'].type.name == 'series':
    #     context['episodes'] = get_seasons(const)

    return render(request, 'entry_details.html', context)


def entry_groupby_year(request):
    from django.db.models import Count
    from chart.charts import distribution_by_year
    context = {
        'year_count': Entry.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
        'chart': distribution_by_year()
    }
    return render(request, 'entry_groupby_year.html', context)


def entry_show_from_year(request, year):
    context = {
        'year': Entry.objects.filter(year=year).order_by('-rate', '-rate_imdb', '-votes'),
        'what_year': year,
    }
    return render(request, 'entry_show_from_year.html', context)


def entry_show_rated_in_month(request, year, month):
    import calendar
    context = {
        'year': Entry.objects.filter(rate_date__year=year, rate_date__month=month),
        'what_month_year': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'entry_show_rated_in_month.html', context)


def entry_groupby_genre(request):
    # from chart.views import chart_genres
    context = {
        'genre': Genre.objects.all().annotate(num=Count('entry')).order_by('-num'),
        # 'chart': chart_genres(),
    }
    return render(request, 'entry_groupby_genre.html', context)


def entry_show_from_genre(request, genre):
    context = {
        'titles_from_genre': Genre.objects.get(name=genre).entry_set.all(),
        'genre_name': genre,
    }
    return render(request, 'entry_show_from_genre.html', context)


def entry_show_from_rate(request, rate):
    context = {
        'entry': Entry.objects.filter(rate=rate).order_by('-rate_date'),
        'rate': rate,
    }
    return render(request, 'entry_show_from_rate.html', context)


def entry_groupby_director(request):
    context = {
        # directors of movies with counter of titles, top50 most watched
        'director': Director.objects.filter(entry__type=Type.objects.get(name='movie')
                                            ).annotate(num=Count('entry')).order_by('-num')[:50],
    }
    return render(request, 'entry_groupby_director.html', context)


def entry_show_from_director(request, id):
    context = {
        'titles_from_director': Director.objects.get(id=id).entry_set.all().order_by('-rate_date'),
        'director_name': Director.objects.get(id=id).name,
    }
    return render(request, 'entry_show_from_director.html', context)