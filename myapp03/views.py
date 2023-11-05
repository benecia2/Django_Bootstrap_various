from django.shortcuts import render, redirect
from myapp03.models import Board, Comment, Movie, Forecast
from django.views.decorators.csrf import csrf_exempt
from .form import UserForm
import math
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import pandas as pd

import json
from myapp03 import dataProcess
from django.db.models.aggregates import Count, Avg


# Create your views here.

# wordcloud
def wordcloud(request):
    a_path = 'D:\\DJANGOWORK\\myDjango03\\data\\'
    data = json.loads(open(a_path+'4차 산업혁명.json', 'r', encoding='utf-8').read())

    dataProcess.make_wordCloud(data)
    return render(request, 'bigdata/word.html', {"img_data":'k_wordCloud.png'})

# wordcloud2
def wordcloud2(request):
    a_path = 'D:\\DJANGOWORK\\myDjango03\\data\\'
    data = json.loads(open(a_path+'4차 산업혁명.json', 'r', encoding='utf-8').read())

    dataProcess.make_wordCloud(data)
    return render(request, 'bigdata/word.html', {"img_data":'pytag_word.png'})


# melon
def melon(request):
    # 순위  곡명  가수  앨범
    datas = []
    dataProcess.melon_crawing(datas)
    return render(request, 'bigdata/melon1.html',{'data':datas})

# map
def map(request):
    dataProcess.map()
    return render(request, 'bigdata/map.html')

# movie_chart
def movie_chart(request):
    data = []
    data = dataProcess.movie_crawing(data)
    # print(data)
    df = pd.DataFrame(data, columns=['제목','평점','예매율'])
    # print(df)
    group_title =df.groupby('제목')
    # print(group_title)

    # 제목별 그룹화 해서 평점의 평균
    group_mean = df.groupby('제목')['평점'].mean().sort_values(ascending=False).head(10)
    # print(group_mean)
    df1 = pd.DataFrame(group_mean, columns=['평점'])
    dataProcess.movie_daum_chart(df1.index, df1.평점)


    # dataProcess.movie_daum_chart()
    return render(request, 'bigdata/movie_daum.html',
                {'img_data':'movie_daum_fig.png'})


# movie ==> 테이블에(Movie)에 insert
def movie(request):
    data = []
    dataProcess.movie_crawing(data)
    # data 들어있는 순서 : title, point, reserve
    for r in data:
        movie = Movie(title = r[0], point = r[1],reserve = r[2])
        movie.save()
    return redirect('/')

# movie_dbchart
def movie_dbchart(request):
    # movie 테이블에서 제목(title)에 해당하는 평점(point) 평균을 구하기
    # data = Movie.objects.values('title').annotate(point_avg=Avg('point'))[0:10]
    data = Movie.objects.values('title').annotate(point_avg=Avg('point')).order_by('-point_avg')[0:10]
    print('data query:',data.query)
    df = pd.DataFrame(data)
    print('data df:',df)
    dataProcess.movie_chart(df.title, df.point_avg)
    return render(request,'bigdata/movie.html',
                {'img_data':'movie_fig.png',
                'data':data})

# weather
def weather(request):
    last_date =Forecast.objects.values('tmef').order_by('-tmef')[:1]
    print('last_date.query :',last_date.query)
    weather = {}
    dataProcess.weather_crawing(last_date,weather)
    for i in weather:
        for j in weather[i]:
            dto = Forecast(city = i, tmef = j[0], wf = j[1], tmn=j[2], tmx=j[3])
            dto.save()
    
# 부산 정보만 출력
    result = Forecast.objects.filter(city='부산')

    result1 = Forecast.objects.filter(city='부산').values('wf').annotate(dcount = Count('wf')).values("dcount", "wf")
    # print('result1',result1.query)
    df = pd.DataFrame(result1)
    print('df',df)
    image_dic = dataProcess.weather_chart(result,df.wf, df.dcount)

    print('image_dic : ',image_dic)
    return render(request, 'bigdata/chart.html',
                {'img_data':image_dic})



######################
# write_form (추가폼)
@login_required(login_url='/login/')
def write_form(request):
    return render(request, 'board/insert.html')

# 업로드 파일위치
UPLOAD_DIR = 'D:/DJANGOWORK/upload/'

# signup 회원가입
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request,user)
            return redirect('/')
        else:
            print("signup POST un_valid")
    else:
        form = UserForm()
        
    return render(request, 'common/signup.html',{'form':form})


# insert 추가하기
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0
    if 'file' in request.FILES :
        file = request.FILES['file']
        fsize = file.size
        fname = file.name
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    board = Board(writer = request.user,
                    title = request.POST['title'],
                    content = request.POST['content'],
                    filename = fname,
                    filesize = fsize
                    )
    board.save()
    return redirect("/list/")

# list(검색추가)
def list(request):
    page = request.GET.get('page',1)
    word = request.GET.get('word','')
    field = request.GET.get('field', 'title')
    # count
    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count

    # page
    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    # 123[다음]    [이전]456[다음]      [이전]7(89) 
    totPage = math.ceil(boardCount/pageSize) # 총 페이지 수(7)
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1
    endPage = startPage+blockPage-1 #( 현재 페이지가 7이라면 )
    if  endPage > totPage :
        endPage = totPage

    start = (currentPage-1)*pageSize

    # 내용
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    else:
        boardList = Board.objects.all().order_by('-id')[start:start+pageSize]


    context = {'boardList' : boardList,
                'boardCount' : boardCount,
                'field' : field,
                'word' : word,
                'startPage' : startPage,
                'blockPage' : blockPage,
                'endPage' : endPage,
                'totPage': totPage,
                'range': range(startPage,endPage+1),
                'currentPage' : currentPage}
    return render(request, 'board/list.html', context)


# list_page
def list_page(request):
    page = request.GET.get('page',1)
    word = request.GET.get('word','')

    boardCount = Board.objects.filter(
                                    # Q(writer__contains = word)|  이걸 제외시켜야 list_page.html이 출력된다.
                                    Q(title__contains = word)|
                                    Q(content__contains = word)).count()
    
    boardList = Board.objects.filter(
                                    # Q(writer__contains = word)|
                                    Q(title__contains = word)|
                                    Q(content__contains = word)).order_by('-id')

    # 페이징 처리
    pageSize = 5

    paginator = Paginator(boardList,pageSize)
    page_obj = paginator.get_page(page)
    print('page_obj:',page_obj)

    context = {
        'boardCount':boardCount,
        'page_list' :page_obj,
        'word':word
    }

    return render(request, 'board/list_page.html',context)
