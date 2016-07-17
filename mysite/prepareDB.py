import django, os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import csv
from movie.models import Genre, Director, Type, Entry, Archive, Season, Episode, Log
from prepareDB_utils import prepare_date_csv, prepare_date_xml, prepare_date_json, getRSS, getOMDb, downloadPosters, \
    downloadPoster


def getSeasonsInfo(entry, totalSeasons):
    # collects for given entry (tv-show) info about episodes and seasons
    for i in range(1, totalSeasons + 1):
        api = 'http://www.omdbapi.com/?i={}&Season='.format(entry.const) + str(i)
        json = getOMDb(entry.const, api)
        if json and json['Response'] and 'Season' in json:
            # if Season.objects.filter(entr=entry, number=i).exists():
            #     print('{} season already exists'.format(api))
            #     continue
            # if updated:     # DO NOT UPDATE SEASONS FOR NOW AT LEAST
            #     continue
            season, updated = Season.objects.update_or_create(entry=entry, number=i)
            for ep in json['Episodes']:
                # if Episode.objects.filter(const=ep['imdbID']).exists():
                #     print('{} {} already exists'.format(api, ep['imdbID']))
                #     continue
                ep, updated = Episode.objects.update_or_create(season=season, const=ep['imdbID'], number=ep['Episode'],
                                                               name=ep['Title'], release_date=ep['Released'],
                                                               rate_imdb=ep['imdbRating'])
        else:
            print('season {} {}'.format(i, api))
# add to getEntry


def getTV(single_update=False, const='not_single'):
    if not single_update:
        entry_series = Entry.objects.filter(type=Type.objects.get(name='series').id)
    else:
        entry_series = Entry.objects.filter(const=const)
    for e in entry_series:
        json = getOMDb(e.const)
        if not (json and json['Response']):
            print('\t\t\tgetTV json error')
            return
        try:
            totals = int(json['totalSeasons'])
        except ValueError:
            print('\t\t\tvalue error', json['totalSeasons'])
            continue
        print('\t {} seasons {}'.format(totals, e.name))
        getSeasonsInfo(e, totals)
    if not entry_series:
        print('not found any tvshows', const)


# getTV()


def getEntryInfo(const, rate, rate_date, log, is_updated=False, exists=False):
    json = getOMDb(const)
    if not (json and json['Response']):
        return
    elif is_updated and exists:  # if entry exists, updater must be sure that can delete and archive it
        entry = Entry.objects.get(const=const)
        archive = Archive.objects.create(const=entry.const, rate=entry.rate, rate_date=entry.rate_date)
        print('updater. exists ' + entry.name, '\t...and deleted')
        entry.delete()
        log.updated_archived += 1
        log.save()
    typ_e, created = Type.objects.get_or_create(name=json['Type'].lower())
    url_imdb = 'http://www.imdb.com/title/{}/'.format(const)
    rel_date = prepare_date_json(json['Released']) if json['Released'] != "N/A" else 'N/A'
    entry = Entry(const=const, name=json['Title'], type=typ_e, rate=rate, rate_imdb=json['imdbRating'],
                  rate_date=rate_date, runtime=json['Runtime'][:-4], year=json['Year'][:4], votes=json['imdbVotes'],
                  release_date=rel_date, url_imdb=url_imdb,
                  url_poster=json['Poster'], tomato_user_meter=json['tomatoUserMeter'],
                  tomato_user_rate=json['tomatoUserRating'], tomato_user_reviews=json['tomatoUserReviews'],
                  tomatoConsensus=json['tomatoConsensus'], url_tomato=json['tomatoURL'], plot=json['Plot'],
                  inserted_by_updater=is_updated
                  )
    entry.save()
    downloadPoster(entry.const, entry.url_poster)
    for g in json['Genre'].split(', '):
        genre, created = Genre.objects.get_or_create(name=g.lower())
        entry.genre.add(genre)
    for d in json['Director'].split(', '):
        director, created = Director.objects.get_or_create(name=d)
        entry.director.add(director)
    log.new_inserted += 1
    log.save()

    if json['Type'] == 'series':
        getTV(single_update=True, const=const)


def csvToDatabase():  # fname.isfile()
    fname = 'ratings.csv'
    log = Log.objects.create()
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if Entry.objects.filter(const=row['const']).exists():
                print('exists ' + row['Title'])
                continue
            rate_date = prepare_date_csv(row['created'])
            print(row['Title'])
            getEntryInfo(row['const'], row['You rated'], rate_date, log)


# csvToDatabase()


def update():
    # from rss xml: const, rate and rate_date. Then use const to get info from omdbapi json
    itemlist = getRSS()
    log = Log.objects.create()
    if not itemlist:
        return
    i = 0
    for num, obj in enumerate(itemlist):
        i += 1
        if i > 10:
            return
        const = obj.find('link').text[-10:-1]
        rate = obj.find('description').text.strip()[-2:-1]
        rate_date = prepare_date_xml(obj.find('pubDate').text)
        if Entry.objects.filter(const=const).exists():
            if Archive.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its already Archived')
                i += 1
                continue
            elif Entry.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its the same entry')
                i += 1
                continue
            getEntryInfo(const, rate, rate_date, log, is_updated=True, exists=True)
            continue
        else:
            print('updater. ' + obj.find('title').text)
            getEntryInfo(const, rate, rate_date, log, is_updated=True)
            # time.sleep( 5 )

if len(sys.argv) > 1:
    if sys.argv[1] == 'fromCSV':
        csvToDatabase()
    if sys.argv[1] == 'seasons':
        getTV()
    if sys.argv[1] == 'posters':
        downloadPosters()
    sys.exit(0)

# downloadPoster('tt2975590', u)
update()
# downloadPosters()
# u = 'http://ia.media-imdb.com/images/M/MV5BNTE5NzU3MTYzOF5BMl5BanBnXkFtZTgwNTM5NjQxODE@._V1_SX300.jpg'

e = Entry.objects.get(const='tt0844441')
if e.type.id == Type.objects.get(name='series').id:
    s = Season.objects.filter(entry=e)
    print(s.count())
    for seas in s:
        print(seas.number)
        ep = Episode.objects.filter(season=seas)
        for epis in ep:
            print('\t', epis.number)
    print()