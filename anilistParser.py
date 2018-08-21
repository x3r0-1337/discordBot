import aiohttp
import asyncio
from datetime import date
from calendar import month_abbr


class anime:
    def __init__(self, animeEntry):
        self.entry = animeEntry
        self.id = self.entry['id']
        if str(self.entry['title']['romaji']) != 'None':
            self.title = self.entry['title']['romaji']
        else:
            self.title = 'Unknown'
        self.frmt = ' '.join(str(self.entry['format']).split('_')).capitalize()
        if str(self.entry['description']) != 'None' and str(self.entry[
               'description']) != '':
            self.description = self.entry['description'].replace('<br>', '\n')
            self.description = self.description.replace('</br>', '\n')
            self.description = self.description.replace('<i>', '*')
            self.description = self.description.replace('<I>', '*')
            self.description = self.description.replace('</i>', '*')
            self.description = self.description.replace('</I>', '*')
            self.description = self.description.replace('\n\n\n', '\n')
            self.description = self.description.replace('\n\n', '\n')
        else:
            self.description = 'Unknown'
        if str(self.entry['status']) == 'RELEASING':
            self.status = 'Airing'
        elif str(self.entry['status']) == 'NOT_YET_RELEASED':
            self.status = 'Not Yet Aired'
        elif str(self.entry['status']) == 'FINISHED':
            self.status = 'Finished Airing'
        else:
            self.status = 'Unknown'
        if str(self.entry['startDate']['year']) != 'None':
            self.styear = str(self.entry['startDate']['year'])
        else:
            self.styear = 'Unknown'
        if (str(self.entry['startDate']['year']) != 'None') and (
                str(self.entry['startDate']['month']) != 'None'):
            self.stmonth = month_abbr[int(self.entry['startDate']['month'])]
            self.stmonthint = int(self.entry['startDate']['month'])
        else:
            self.stmonth = 'Unknown'
            self.stmonthint = 0
        if str(self.entry['status']) == 'FINISHED':
            self.edyear = self.entry['endDate']['year']
            if (str(self.entry['endDate']['year']) != 'None') and (
                    str(self.entry['endDate']['month']) != 'None'):
                self.edmonth = month_abbr[int(self.entry['endDate']['month'])]
                self.edmonthint = int(self.entry['endDate']['month'])
            else:
                self.edmonth = 'Unknown'
                self.edmonthint = 0
        else:
            self.edyear = 'Unknown'
            self.edmonth = 'Unknown'
            self.edmonthint = 0
        if str(self.entry['season']) != 'None':
            self.season = (self.entry['season']).capitalize()
        else:
            self.season = 'Unknown'
        if str(self.entry['episodes']) != 'None':
            self.episodes = str(self.entry['episodes'])
        else:
            self.episodes = 'Unknown'
        self.source = ' '.join(str(self.entry['source']
                                   ).split('_')).capitalize()
        self.image = self.entry['coverImage']['large']
        self.genres = self.entry['genres'] if (
            (str(self.entry['genres']) != 'None') and (
                self.entry['genres'] != [])) else 'Unknown'
        if self.entry['synonyms'] != []:
            self.synonyms = self.entry['synonyms']
        else:
            self.synonyms = 'None'
        if str(self.entry['nextAiringEpisode']) != 'None':
            self.nextep = str(self.entry['nextAiringEpisode']['episode'] - 1)
        else:
            self.nextep = 'Unknown'
        self.url = self.entry['siteUrl']


async def queryAiring():
    pages = []
    pagedict, lastpage = await fetch()
    for i in range(1, lastpage+1):
        pages = pages + pagedict[i]['data']['Page']['media']
    entries = []
    for entry in pages:
        entries.append(anime(entry))
    return entries


async def fetch():
    pagedict = {}
    pending = []
    dt = date.today().year - 1
    with open('airing-query.txt', 'r') as file:
        query = file.read().replace('\n', '')
    async with aiohttp.ClientSession() as session:
        res = await fetchPage(query, 1, dt, session)
        if res == 'error':
            return res
        lstpage = res['data']['Page']['pageInfo']['lastPage']
        pagedict[1] = res
    async with aiohttp.ClientSession() as session:
        for i in range(2, lstpage + 1):
            pendingPage = asyncio.ensure_future(fetchPage(query, i,
                                                          dt, session))
            pending.append(pendingPage)
        gatheredPages = await asyncio.gather(*pending)
    for i in range(0, len(gatheredPages)):
        pagedict[(i+2)] = gatheredPages[i]
    return pagedict, lstpage


async def fetchPage(query, page, stdt, session):
    stdt = int(str(stdt) + '0000')
    url = 'https://graphql.anilist.co'
    async with session.post(url, json={'query': query, 'variables':
                                       {'page': page, 'stdt':
                                        stdt}}) as response:
        respcode = response.status
        if respcode != 200:
            print('Error: Code: ' + str(respcode) + '\n' +
                  'Full Error Code: ' + str(await response.json()))
            return 'error'
        return await response.json()
