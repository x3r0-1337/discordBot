import aiohttp
import asyncio
from datetime import date
from calendar import month_abbr


class anime:
    """Represents an Anime object.

    ---Arguments---
    `animeEntry` : A `Media` query response in the form of a Python `dict`, received from an AniList GraphQL Query.

    ---Properties---
    `id` : ID of the anime as per AniList.
        Returns an `int`
    
    `title` : Title of the anime in romaji.
        Returns a `string`.
        Returns `Unknown` if not found.
    
    `frmt` : Format of the anime. Possible values are:
        `Tv`, `Tv Short`, `Movie`, `Special`, `Ova`, `Ona`, `Music`.
        Returns a `string`.
    
    `description` : Description of the anime.
        Returns a `string`.
        Returns `Unknown` if not found.
    
    `status` : Status of the anime. Possible values are:
        `Airing`, `Not Yet Aired`, `Finished Airing`.
        Returns a `string`.
        Returns `Unknown` if not found.
    
    `styear` : The year in which the anime is aired.
        Returns an integer as a `string`.
        Returns `Unknown` if not found.

    `stmonth` : The month in which the anime is aired. Possible values are:
        `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`.
        Returns a `string`.
        Returns `Unknown` if not found.

    `stmonthint` : The integer value of `stmonth`. Possible values are from `1-12`.
        Returns an `int`.
        Returns `0` if not found.

    `edyear` : The year in which the anime finished airing.
        Returns a `int`.
        Returns `Unknown` if not found or anime has not finished airing.

    `edmonth` : The month in which the anime finished airing. Possible values are:
        `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`.
        Returns a `string`.
        Returns `Unknown` if not found or anime has not finished airing.
    
    `edmonthint` : The integer value of `edmonth`. Possible values are from `1-12`.
        Returns an `int`.
        Returns `0` if not found.

    `season` : The season in which the anime is aired. Possible values are:
        `Winter`, `Spring`, `Summer`, `Fall`.
        Returns a `string`.
        Returns `Unknown` if not found.

    `episodes` : The number of episodes in the anime.
        Returns an integer as a `string`.
        Returns `Unknown` if not found.

    `source` : The source of the anime. Possible values are:
        `Original`, `Manga`, `Light Novel`, `Visual Novel`, `Video Game`, `Other`.
        Returns a `string`.

    `image` : The URL of the image of the anime.
        Returns a `string`.

    `genres` : The genre(s) of the anime.
        Returns a `list` containing genres of type `string`.
        Returns `Unknown` if not found.

    `synonyms` : The synonym(s) of the anime.
        Returns a `list` containing synonyms of type `string`.
        Returns `None` if `list` is empty.

    `currep` : The current episode being aired of the anime.
        Returns an integer as `string`.
        Returns `Unknown` if anime is not airing or is not found.

    `url` : The URL of the anime site on AniList
        Returns a `string`.
    """
    def __init__(self, animeEntry):
        self.__entry = animeEntry
        self.id = int(self.__entry['id'])
        if str(self.__entry['title']['romaji']) != 'None':
            self.title = self.__entry['title']['romaji']
        else:
            self.title = 'Unknown'
        self.frmt = ' '.join(str(self.__entry['format']).split('_')).capitalize()
        if str(self.__entry['description']) != 'None' and str(self.__entry[
               'description']) != '':
            self.description = self.__entry['description'].replace('<br>', '\n')
            self.description = self.description.replace('</br>', '\n')
            self.description = self.description.replace('<i>', '*')
            self.description = self.description.replace('<I>', '*')
            self.description = self.description.replace('</i>', '*')
            self.description = self.description.replace('</I>', '*')
            self.description = self.description.replace('\n\n\n', '\n')
            self.description = self.description.replace('\n\n', '\n')
        else:
            self.description = 'Unknown'
        if str(self.__entry['status']) == 'RELEASING':
            self.status = 'Airing'
        elif str(self.__entry['status']) == 'NOT_YET_RELEASED':
            self.status = 'Not Yet Aired'
        elif str(self.__entry['status']) == 'FINISHED':
            self.status = 'Finished Airing'
        else:
            self.status = 'Unknown'
        if str(self.__entry['startDate']['year']) != 'None':
            self.styear = str(self.__entry['startDate']['year'])
        else:
            self.styear = 'Unknown'
        if (str(self.__entry['startDate']['year']) != 'None') and (str(self.__entry['startDate']['month']) != 'None'):
            self.stmonth = month_abbr[int(self.__entry['startDate']['month'])]
            self.stmonthint = int(self.__entry['startDate']['month'])
        else:
            self.stmonth = 'Unknown'
            self.stmonthint = 0
        if str(self.__entry['status']) == 'FINISHED':
            self.edyear = self.__entry['endDate']['year']
            if (str(self.__entry['endDate']['year']) != 'None') and (str(self.__entry['endDate']['month']) != 'None'):
                self.edmonth = month_abbr[int(self.__entry['endDate']['month'])]
                self.edmonthint = int(self.__entry['endDate']['month'])
            else:
                self.edmonth = 'Unknown'
                self.edmonthint = 0
        else:
            self.edyear = 'Unknown'
            self.edmonth = 'Unknown'
            self.edmonthint = 0
        if str(self.__entry['season']) != 'None':
            self.season = (self.__entry['season']).capitalize()
        else:
            self.season = 'Unknown'
        if str(self.__entry['episodes']) != 'None':
            self.episodes = str(self.__entry['episodes'])
        else:
            self.episodes = 'Unknown'
        self.source = ' '.join(str(self.__entry['source']).split('_')).capitalize()
        self.image = self.__entry['coverImage']['large']
        if ((str(self.__entry['genres']) != 'None') and (self.__entry['genres'] != [])):
            self.genres = self.__entry['genres']
        else:
            self.genres = 'Unknown'
        if self.__entry['synonyms'] != []:
            self.synonyms = self.__entry['synonyms']
        else:
            self.synonyms = 'None'
        if str(self.__entry['nextAiringEpisode']) != 'None':
            self.currep = str(self.__entry['nextAiringEpisode']['episode'] - 1)
        else:
            self.currep = 'Unknown'
        self.url = self.__entry['siteUrl']


async def query(choice, var=0):
    pages = []
    pagedict, lastpage = await fetch(choice, var)
    for i in range(1, lastpage+1):
        pages = pages + pagedict[i]['data']['Page']['media']
    entries = []
    for entry in pages:
        entries.append(anime(entry))
    return entries


async def fetch(choice, var=0):
    if 'airing' in choice:
        var = date.today().year - 1
        filename = 'airing-query.txt'
    elif 'search' in choice:
        filename = 'search-query.txt'
    with open(filename, 'r') as file:
        query = file.read().replace('\n', '')
    pagedict, lastpage = await collectPages(query, var)
    return pagedict, lastpage


async def collectPages(query, var):
    pagedict = {}
    pending = []
    if isinstance(var, int):
        var = int(str(var) + '0000')
    async with aiohttp.ClientSession() as session:
        res = await fetchPage(query, 1, var, session)
        if res == 'error':
            return res
        lstpage = res['data']['Page']['pageInfo']['lastPage']
        pagedict[1] = res
        for i in range(2, lstpage + 1):
            pendingPage = asyncio.ensure_future(fetchPage(query, i, var, session))
            pending.append(pendingPage)
        gatheredPages = await asyncio.gather(*pending)
    for i in range(0, len(gatheredPages)):
        pagedict[(i+2)] = gatheredPages[i]
    return pagedict, lstpage


async def fetchPage(query, page, var, session):
    url = 'https://graphql.anilist.co'
    jvar = {'page': page, 'var':var}
    async with session.post(url, json={'query': query, 'variables': jvar}) as response:
        respcode = response.status
        if respcode != 200:
            print('Error: Code: ' + str(respcode) + '\n' + 'Full Error Code: ' + str(await response.json()))
            return 'error'
        return await response.json()
