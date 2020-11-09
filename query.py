"""
This module implements a (partial, sample) query interface for elasticsearch movie search.
You will need to rewrite and expand sections to support the types of queries over the fields in your UI.

Documentation for elasticsearch query DSL:
https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

For python version of DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/

Search DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html
"""

import re
from flask import *
# from index import Movie
from index import my_analyzer
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList
import thulac
from elasticsearch_dsl.analysis import tokenizer, analyzer

app = Flask(__name__)

# Initialize global variables for rendering page
tmp_text = ""
tmp_raw = ""
tmp_star = ""
tmp_min = ""
tmp_max = ""
gresults = {}
posMap = {"名词": "_n", "人名": "_np", "地名": "_ns", "机构名": "_ni", "其它专名": "_nz",
          "数词": "_m", "量词": "_q", "数量词": "_mq", "时间词": "_t", "方位词": "_f", "处所词": "_s",
          "动词": "_v", "形容词": "_a", "副词": "_d", "前接成分": "_h", "后接成分": "_k", "习语": "_i",
          "简称": "_j", "代词": "_r", "连词": "_c", "介词": "_p", "助词": "_u", "语气助词": "_y",
          "叹词": "_e", "拟声词": "_o", "语素": "_g", "标点": "_w", "其它": "_x"}
# my_analyzer = analyzer('custom', tokenizer='whitespace',filter = [])

# display query page
@app.route("/")
def search():
    return render_template('page_query.html')


# display results page for first set of results and "next" sets.
@app.route("/results", defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/results/<page>", methods=['GET', 'POST'])
def results(page):
    global tmp_raw
    global tmp_text
    global tmp_wordA
    global tmp_wordB
    global tmp_posA
    global tmp_location
    global tmp_posB
    global tmp_categories
    global tmp_min
    global tmp_max
    global gresults
    global gFlag

    gFlag = "text"
   # convert the <page> parameter in url to integer.
    if type(page) is not int:
        page = int(page.encode('utf-8'))
        # if the method of request is post (for initial query), store query in local global variables
    # if the method of request is get (for "next" results), extract query contents from client's global variables
    if request.method == 'POST':
        text_query = request.form['query']
        tmp_text = text_query
        wordA_query = request.form['starring']
        wordB_query = request.form['director']
        tmp_wordA = wordA_query
        tmp_wordB = wordB_query
        location_query = request.form['location']
        tmp_location = location_query
        posA_query = request.form['language']
        posB_query = request.form['time']
        tmp_posA = posA_query
        tmp_posB = posB_query
    else:
        # use the current values stored in global variables.
        text_query = tmp_text
        wordA_query = tmp_wordA
        wordB_query = tmp_wordB
        location_query = tmp_location
        posA_query = tmp_posA
        posB_query = tmp_posB
    # store query values to display in search boxes in UI
    shows = {}
    shows['text'] = text_query
    shows['star'] = wordA_query
    shows['director'] = wordB_query
    shows['location'] = location_query
    shows['language'] = posA_query
    shows['time'] = posB_query
    shows['ptext'] = text_query
    shows['raw'] = text_query
    thu1 = thulac.thulac(seg_only=True)
    # Create a search object to query our index
    search = Search(index='sample_film_index')
    if len(wordA_query) > 0 or len(wordB_query) > 0:
        flag = False
        if len(posA_query) > 0:
            posA_query = posMap[posA_query]
            gFlag = "ptext"
        if len(posB_query) > 0:
            posB_query = posMap[posB_query]
            gFlag = "ptext"
        if len(location_query) > 0:
            if (location_query == "右") or (location_query == "右邻") or (location_query == "右相邻"):
                if len(posA_query) > 0 and len(posB_query) > 0:
                    text_query = wordB_query + posB_query + ' ' + wordA_query+posA_query
                    s = search.query('match_phrase', ptext={
                        'query': text_query, 'slop': 0})
                else:
                    text_query = wordB_query + ' ' + wordA_query
                    s = search.query('match_phrase', text={
                        'query': text_query, 'slop': 0})
                flag = True
            elif (location_query == "左") or (location_query == "左邻") or (location_query == "左相邻"):
                if len(posA_query) > 0 and len(posB_query) > 0:
                    text_query = wordA_query + posA_query + ' ' + wordB_query+posB_query
                    s = search.query('match_phrase', ptext={
                        'query': text_query, 'slop': 0})
                else:
                    text_query = wordA_query + ' ' + wordB_query
                    s = search.query('match_phrase', text={
                        'query': text_query, 'slop': 0})
                flag = True

            elif (location_query == "不")or (location_query == "不邻") or (location_query == "不相邻"):
                if len(posA_query) > 0 and len(posB_query) > 0:
                    text_query = wordA_query + posA_query + ' ' + wordB_query+posB_query
                    text_query2 = wordB_query + posB_query + ' ' + wordA_query+posA_query
                    s = search.query('match_phrase', ptext={
                        'query': text_query, 'slop': 9999})
                    q = ~ Q("match_phrase", ptext=text_query)
                    s = s.query(q)
                    q2 = ~ Q("match_phrase", ptext=text_query2)
                    s = s.query(q2)
                else:
                    text_query = wordA_query + ' ' + wordB_query
                    text_query2 = wordB_query + ' ' + wordA_query
                    s = search.query('match_phrase', text={
                        'query': text_query, 'slop': 9999})
                    q = ~ Q("match_phrase", text=text_query)
                    s = s.query(q)
                    q2 = ~ Q("match_phrase", text=text_query2)
                    s = s.query(q2)
                flag = True
        if flag == False:
            if len(posA_query) > 0 or len(posB_query) > 0:
                text_query = wordA_query + posA_query + ' '+wordB_query + posB_query

                s = search.query('match_phrase', ptext={
                    'query': text_query, 'slop': 9999})
            else:
                text_query = wordA_query + ' ' + wordB_query
                s = search.query('match_phrase', text={
                    'query': text_query, 'slop': 9999})
    elif len(text_query) > 0:
        text_query = thu1.cut(text_query, text=True)
        s = search.query('match', text=text_query)
    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    for key in shows:
        s = s.highlight(key, fragment_size=999999999,
                        number_of_fragments=1)

    # determine the subset of results to display (based on current <page> value)
    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

    # execute search and return results in specified range.
    response = s[start:end].execute()
    print(response.hits)
    # insert data into response
    resultList = {}
    for hit in response.hits:
        result = {}
        result['score'] = hit.meta.score
        for field in hit:
            if field != 'meta':
                result[field] = getattr(hit, field)
        result['raw'] = ''.join(result['raw'])
        if 'highlight' in hit.meta:
            for field in hit.meta.highlight:
                result[field] = getattr(hit.meta.highlight, field)[
                    0].replace(" ", '')
                print(result[field])
        resultList[hit.meta.id] = result

    # make the result list available globally
    gresults = resultList

    # get the total number of matching results
    result_num = response.hits.total.value
    print(result_num)
    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows, gflag=gFlag)
    else:
        message = []
        if len(text_query) > 0:
            message.append('Unknown search term: ' + text_query)
        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows, gflag=gFlag)


if __name__ == "__main__":
    app.run()
