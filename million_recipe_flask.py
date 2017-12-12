

from flask import Flask,render_template,redirect,request,url_for,request
from flaskext.mysql import MySQL
import pymysql
import re
import requests


mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'wnsgus35'
app.config['MYSQL_DATABASE_DB'] = 'million_recipe'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_CHARSET'] = 'utf-8'
mysql.init_app(app)

class CurrentUser:
    def __init__(self,customerID,customerPW,refrigID,name):
        self.customerID = customerID
        self.customerPW = customerPW
        self.refrigID = refrigID
        self.name = name
    def getCustomerID(self):
        return self.customerID
    def getCusomterPW(self):
        return self.customerPW
    def getrefrigID(self):
        return self.refrigID
    def getName(self):
        return self.name
    def setCustomerID(self,customerID):
        self.customerID = customerID
    def setCustomerPW(self,customerPW):
        self.customerPW = customerPW
    def setRefrigID(self,refrigID):
        self.refrigID = refrigID
    def setName(self,name):
        self.name = name


current_user = None
@app.route('/')
#@app.route('/<bool:isUserMatch>')
@app.route('/<int:isUserMatch>')
def login(isUserMatch=None):
    global current_user
    if (current_user!=None): # 이미 로그인 되어있는 경우
        return render_template('loginpage.html')
    else:
        return render_template('login.html',isUserMatch=isUserMatch)
# static, templates 폴더를 만들어서 html 코드를 작성해줘야한다.

@app.route('/main')
def main_menu():
    return render_template('loginpage.html')

'''
로그인,회원가입,로그아웃,비밀번호 변경
'''

@app.route('/signup')
def sign_up():
    return render_template('register.html')

@app.route('/signupReq',methods=['POST'])
def signupReq():
    if request.method =="POST":
        id = request.form['id']
        password = request.form['password']
        name = request.form['name']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("SELECT * from Customer where customerID in (%s)",(id))
        datas = cur.fetchall()
        if(datas.__len__()==0): # 아이디가 DB에 존재하지 않는다면 sign up.
            cur.execute("INSERT INTO Refrig values()")

            cur.execute("SELECT * from Refrig order by refrigID desc limit 1")

            ((maxrefrigID,),) = cur.fetchall()

            cur.execute("INSERT INTO Customer(customerID,customerPw, refrigID, name) VALUES(%s, %s ,%s,%s)", (id,password,maxrefrigID,name))

            con.commit()
            con.close()
            global current_user
            current_user = CurrentUser(id,password,maxrefrigID,name)

            return render_template('loginpage.html')
        else : # 이미 아이디가 DB에 존재한다면 회원가입불가.


            return render_template('login.html')
@app.route('/reqLogin',methods=['POST'])
def reqLogin(id=None,password=None):
    if request.method =="POST":
        temp_id = request.form['id']
        temp_pw = request.form['password']
        # db에 있는 값과 비교하여 일치하면 return값 1로 줌.
        #if
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("SELECT customerID,customerPW, refrigID, name from Customer where customerID in (%s) and customerPw in (%s)", (temp_id,temp_pw))
        datas = cur.fetchall()

        if(datas.__len__()==1): # 회원가입 되어있으면



            ((customerID,customerPW,refrigID,name),) =  datas
            global current_user
            current_user = CurrentUser(customerID,customerPW,refrigID,name)
            con.close()
            return render_template('loginpage.html',name=current_user.getName())

        # db에 있는 값과 비교하여 일치하지 않으면 return값 0으로 줌.
        else:


            isUserMatch = 0
            con.close()
            return render_template('login.html', isUserMatch=isUserMatch)


@app.route('/changePW',methods=['POST'])
def changePW():
    global current_user
    if (current_user==None): # 로그인이 안되어 있을 경우
        return render_template('login.html')# redirect to index(login page).
    else:# 로그인이 되어 있을 경우
        new_pw = request.form['password']

        current_user.setCustomerPW(new_pw)
        con = mysql.connect()# db에 수정 사항 반영
        cur = con.cursor()
        cur.execute("UPDATE Customer set customerPW = (%s) where customerID = (%s) ",(new_pw,current_user.getCustomerID()))
        con.commit()
        con.close()
        current_user = None # 로그아웃 시키고, 로그인페이지 다시뜨게하여 로그인 다시하게함
        return render_template('login.html')

@app.route('/logout')
def logout():
    global current_user
    if (current_user==None): # 로그인이 안되어 있을 경우
        return render_template('login.html')# redirect to index(login page).
    else:# 로그인이 되어 있을 경우
        current_user = None
        return render_template('login.html') # redirect to index(login page).

'''
재료 관리

'''
@app.route('/showIngre')
def showIngre():
    global current_user

    if (current_user == None):  # 로그인이 안되어 있을 경우
        return render_template('login.html')  # redirect to index(login page).
    else:  # 로그인이 되어 있을 경우
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT ingreID,refrigID,quantity,name from refriingre where refrigID = (%s)",(current_user.getrefrigID()))
        rows = cur.fetchall()
        con.close()
        return render_template('ManageFridge.html',ingredients=rows)

@app.route('/addIngre',methods=['POST','GET']) # 재료 추가
def addIngre():
    global current_user
    if request.method == "GET":


        if (current_user==None): # 로그인이 안되어 있을 경우
            return render_template('login.html')# redirect to index(login page).
        else:# 로그인이 되어 있을 경우
            return render_template('addingre.html') # addingre.html로 render
    elif request.method == "POST":
        ingre_quantity = request.form['ingre_quantity']
        ingre_name = request.form['ingre_name']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("SELECT * from Refriingre where name Like (%s)", (ingre_name))
        datas = cur.fetchall()
        if(datas.__len__() == 0):
            cur.execute("INSERT INTO Refriingre(refrigID,quantity,name) VALUES (%s,%s,%s)",(current_user.getrefrigID(),ingre_quantity,ingre_name))
            con.commit()
            con.close()
            return redirect(url_for('showIngre'))
        else:# 재료이름이 중복되면, 재료 추가 불가#.
            con.commit()
            con.close()
            return render_template('addingre.html')

@app.route('/deleteIngre',methods=['POST'])
def deleteIngre():
    global current_user
    if (current_user==None):
        return render_template('login.html')
    else:
        ingre_id = request.form['delete']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("delete from refriingre where ingreID = (%s)",(ingre_id))
        con.commit()
        con.close()
        return redirect(url_for('showIngre'))


'''
친구 관리
'''



@app.route('/Friends/Index') # 친구관리 index페이지
def friendIdx():
    global current_user
    if (current_user==None):
        return render_template('login.html')
    else:
        '''
            친구 목록
        '''
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT customer1ID,customer2ID from friend where (customer1ID like (%s) or customer2ID like (%s)) and status = 1 ",(current_user.getCustomerID(),current_user.getCustomerID()))
        friend_lists = cur.fetchall()

        '''
            친구 신청한 목록
        '''
        cur.execute("SELECT customer2ID,status from friend where customer1ID like (%s) ",(current_user.getCustomerID())) # customer1ID에는 신청자, custome2ID에는 신청받은 사람. status가 2이면 승인 대기중,status가 0이면 거절됨.
        request_lists = cur.fetchall()


        '''
            친구 신청 받은 목록
        '''
        cur.execute("SELECT customer1ID from friend where customer2ID like (%s) and status = 2 ",(current_user.getCustomerID()))
        requested_lists = cur.fetchall()

        con.close()

        return render_template('ManageFriend.html',friend_lists=friend_lists,request_lists=request_lists,requested_lists=requested_lists,current_user=current_user)

@app.route('/Friends/Search',methods=['POST'])
def SearchFriend():
    global current_user
    if (current_user == None):
        return render_template('login.html')
    else:
        friendID = request.form['friendID']
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT customerID,name from Customer where customerID like (%s)',(friendID))
        datas = cur.fetchall()

        if datas.__len__()==0:  # 회원 목록중에 없으면
            return render_template('SearchFriend.html',customer=None)
        else: # 회원 목록중에 있으면
            return render_template('SearchFriend.html',customer=datas)
@app.route('/FriendsAddReq',methods=['POST']) #친구 추가 요청
def FriendsAddReq():
    global current_user
    if (current_user == None):
        return render_template('login.html')
    else:

        customer2ID = request.form['friendID'] #   버튼으로 부터 값이 넘겨와짐
        if (current_user.getCustomerID()==customer2ID): # 내 자신에게 친구 신청하려는 경우
            return "내 자신에게 친구 신청할 수 없습니다."
        else:
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            cur.execute("SELECT * from friend where (customer1ID in (%s,%s) or customer2ID in (%s,%s)) and status = 1",(current_user.getCustomerID(),customer2ID,current_user.getCustomerID(),customer2ID)) # 이미 친구로 등록되어있는데, 친구 신청 요청자와 받은자가 달라질 뿐 인데 친구 신청했을 경우에 대한 예외 처리
            datas = cur.fetchall()
            if datas.__len__()==0:
                cur.execute("INSERT INTO friend(customer1ID,customer2ID,status) values(%s,%s,%s)",(current_user.getCustomerID(),customer2ID,2))  # customer1ID에는 친구 신청자 ID가 들어가고 customer2ID에는 친구의 ID가 들어간다.
                con.commit()
                con.close()
                return redirect(url_for('friendIdx'))
            else: # 이미 친구로 등록되어있는데 , 신청자 받는자 아이디만 바꿔서 신청하는 경우
                return '이미 친구로 등록되어있습니다.'




@app.route('/FriendsDelete',methods=['POST']) # 친구 삭제
def FriendsDelete():
    global current_user
    if (current_user==None):
        return render_template('login.html')
    else:
        '''
            친구 삭제
        '''
        friendID = request.form['friendID']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("DELETE from friend where (customer1ID in (%s,%s) or customer2ID in (%s,%s)) and status = 1 ",(current_user.getCustomerID(),friendID,current_user.getCustomerID(),friendID))
        con.commit()
        con.close()
        return redirect(url_for('friendIdx'))



@app.route('/FriendsGrant',methods=['POST']) # 친구 요청 승인
def FriendsGrant():
    global current_user
    if( current_user == None):
        return render_template('login.html')

    else:
        friendID = request.form['friendID'] #   버튼으로 부터 값이 넘겨와짐
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("UPDATE friend SET status = 1 where customer1ID like (%s) and customer2ID like (%s) ",(friendID,current_user.getCustomerID()))
        con.commit()
        con.close()

        return redirect(url_for('friendIdx'))

@app.route('/FriendsReject',methods=['POST']) # 친구 요청 거부
def FriendsReject():
    global current_user
    if (current_user == None):
        return render_template('login.html')
    else:
        friendID = request.form['friendID'] #   버튼으로 부터 값이 넘겨와짐
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("UPDATE friend SET status = 0 where customer1ID like (%s) and customer2ID like (%s) ",(friendID,current_user.getCustomerID()))
        con.commit()
        con.close()
        return redirect(url_for('friendIdx'))


'''
레시피 검색

'''


@app.route('/SearchRecipe/Index')
def SearchRecipeIndex():

    global current_user
    if (current_user==None): #로그인이 안되어있으면 login 페이지로 이동.
        return render_template('login.html')
    else: # 로그인이 되어있으면 search 가능
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT ingreID,name,quantity from refriingre where refrigID = (%s)",(current_user.getrefrigID()))
        ingres = cur.fetchall()
        con.close()
        return render_template('SearchRecipe.html',ingredients=ingres)

@app.route('/SearchRecipe',methods=['POST'])
def SearchRecipe():

    global current_user
    if (current_user == None): #로그인이 안되어있으면 login 페이지로 이동.
        return render_template('login.html')
    else: # 로그인이 되어있으면 search가능
        foodstuffs = request.form.getlist('foodstuffs')
        foodstype = request.form['foodsType']

        ################################################## 페이지별 url, 제목 , 이미지 크롤링 ########################################
        url = []
        title = []  # 2차원 배열로 저장될 것임
        ahref = []  # 2차원 배열로 저장될 것임
        image = []  # 2차원 배열로 저장 될 것임
        if foodstype == 0:  # 전체 선택 눌렀을 경우
            url.append('http://www.10000recipe.com/recipe/list.html?q=' + "+".join(foodstuffs) + '&cat4=&page=')
        else:
            url.append('http://www.10000recipe.com/recipe/list.html?q=' + '+'.join(foodstuffs) + '&cat4='+str(foodstype)+'&page=')


        received = requests.get(url[0])
        # print(received) # received에 대한 상태 코드가 출력됨 200이 성공했다는 반응.
        # print(received.text) -> 인코딩이 제대로 안되있네.
        text = received.content  # text,content의 차이 : content는 웹 서버로 부터 받은 최초 데이터. byte단위로 출력하겠다 이소리임. -> 해석하지 않는다.( 제일 위에 b' 라는게 나옴)
        text = text.decode('utf-8')
        # print(text)
        FirstPage_ResultNotfound = re.findall(r'에 대한 검색결과가 없습니다.', text, re.DOTALL)
        if (FirstPage_ResultNotfound.__len__() == 1):  # 첫페이지에서 검색 결과를 출력하지 않을 때
            print('검색 결과가 없습니다.')
        else:  # 첫페이지에서 검색결과가 있을 때

            # *** 첫 페이지에서의 결과값들 ***********************
            # 첫페이지에서 filtering:
            title.append(re.findall(r'class="ellipsis_title2">(.+?)</h4>', text))
            temp_ahref = re.findall(r'<a class="thumbnail" href="(.+?)">', text)
            temp_ahref.pop(-1)
            ahref.append(temp_ahref)
            image.append(re.findall(r'<img src="(.+?)" style="width:275px; height:275px;">', text))

            # ***********************************************

            isFoundInten = True  # 10페이지 이내에서 결과값이 있는가?
            i = 2
            while (i <= 10 and isFoundInten == True):  # 10페이지 이상으로 넘어가거나, 10페이지 내에서 검색결과가 더이상 없을때 while문을 벗어남
                temp_url = url[0] + str(i)
                received = requests.get(temp_url)
                text = received.content
                text = text.decode('utf-8')
                isResultFound = re.findall(r'에 대한 검색결과가 없습니다.', text, re.DOTALL)
                if (isResultFound.__len__() == 1):  # 검색 결과가 없으면
                    isFoundInten = False
                else:  # 검색 결과가 있을때
                    title.append(re.findall(r'class="ellipsis_title2">(.+?)</h4>', text))
                    temp_ahref = re.findall(r'<a class="thumbnail" href="(.+?)">', text)
                    temp_ahref.pop(-1)
                    ahref.append(temp_ahref)
                    image.append(re.findall(r'<img src="(.+?)" style="width:275px; height:275px;">', text))
                    i = i + 1
            
            return render_template('ViewRecipe.html',title=title,ahref=ahref,image=image)

'''
상세 레시피 정보 보기
'''

@app.route('/recipe/<int:recipenum>')
def showRecipeDetail(recipenum):

    global current_user
    if (current_user == None):
        return render_template('login.html')
    else:

        detail_url = 'http://www.10000recipe.com/recipe/'+str(recipenum)
        detail_received = requests.get(detail_url)
        detail_text = detail_received.content
        detail_text = detail_text.decode('utf-8')
        all_ingredient = re.findall(r'<div class="ready_ingre3" id="divConfirmedMaterialArea">(.+?)</div>', detail_text,
                                    re.DOTALL)
        # 제목
        title_html = re.findall(r'<div class="view2_summary">(.+?)</div>', detail_text, re.DOTALL)
        stripped_title_html = title_html[0].strip()
        detail_title = re.findall(r'<h3>(.+?)</h3>', stripped_title_html, re.DOTALL)

        # 이미지
        detail_image = re.findall(r'<img id="main_thumbs" src="(.+?)" alt="main thumb">', detail_text, re.DOTALL)

        # print(detail_title, detail_image)
        if (all_ingredient.__len__() == 0):  # 재료를 format에 맞춰 쓰지 않은 게시물인 경우
            print(detail_url + " 을 통해 상세 재료 정보 혹은 조리 순서를 확인하세요.")
        else:  # 재료를 format에 맞춰 쓴 게시물 인경우

            ingredients_html = all_ingredient[0].strip()  # 재료관련 부분 크롤링하기 위한 부분 html . * ingredient = ingredient[0].strip 하면 \r \n 같은거 제거 안되네.

            ingredients = re.findall(r'<li>(.+?)                                                ', ingredients_html,
                                     re.DOTALL)
            #print(ingredients)
            # 재료 양 for format 맞춰서 쓴 애들
            quantity = re.findall(r'<span class="ingre_unit">(.*?)</span>', ingredients_html, re.DOTALL)  # 재료의 양
            # ingredient_quantity= quantity[4].strip()
            #print(quantity)

            all_orders = re.findall(r'<div id="stepdescr(.+?)" class="media-body">(.+?)</div>', detail_text,
                                    re.DOTALL)  # plus_tip 없는 조리 순서
            if all_orders.__len__() == 0:  # 조리 순서를 포맷에 맞지 않게 쓴 게시물인 경우
                print(detail_url + " 을 통해 상세 조리 순서를 확인하세요.")
            else:
                cook_orders = []
                for order in all_orders:  # 조리 순서를 포맷에 맞게 쓴 게시물 인경우
                    cook_order_num, cook_order = order
                    cleantext1 = cook_order.replace('<p class="step_add add_tip2">', " * 이 단계에서의 팁: ")
                    cleantext2 = cleantext1.replace('</p>', "")
                    cleantext3 = cleantext2.replace('<br />', "")
                    cleantext4 = cleantext3.replace('<p class="step_add add_tool">', " * 필요한 도구: ")
                    cleantext5 = cleantext4.replace('<p class="step_add add_material">', " * 필요한 재료: ")
                    cook_orders.append(cleantext5)
            return render_template('ViewDetailRecipe.html',detail_title=detail_title,detail_image=detail_image,detail_url=detail_url,ingredients=ingredients,quantity=quantity,cook_orders=cook_orders,recipenum=recipenum)

'''
레시피 저장
'''

@app.route('/SaveRecipe',methods=['POST'])
def SaveRecipe():
    global current_user
    if (current_user ==None):
        return render_template('login.html')
    else:

        title = request.form['title']
        imageUrl = request.form['imageUrl']
        url = request.form['url']

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('INSERT INTO Recipe(title,imageUrl,url) values(%s,%s,%s)',(title,imageUrl,url))# 레시피 생성

        cur.execute("SELECT * from Recipe order by recipeID desc limit 1")

        last_recipe = cur.fetchall()
        for r in last_recipe:
            maxRecipeID = r['recipeID']

        cur.execute('INSERT INTO RecipeList(recipeID,customerID) values(%s,%s)',(maxRecipeID,current_user.getCustomerID())) # 현재 로그인한 사용자의 RecipeList에 추가
        con.commit()
        con.close()
        return redirect(url_for('ShowMyRecipe'))



'''
내 레시피중 추천할 레시피 고르기

'''

'''
@app.route('/selectForRecommend/Myrecipe')
def selectRecipe(friendID):
    global current_user
    if (current_user == None):
        return render_template('login.html')

    else:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT R.title,R.imageUrl,R.kind,R.url from RecipeList AS RL join Recipe R on RL.recipeID = R.recipeID where RL.customerID like (%s)',(current_user.getCustomerID()))
        MyRecipes = cur.fetchall()
        con.close()


        return render_template('selectMyRecipe.html',MyRecipes=MyRecipes,friendID=friendID)
'''

'''
, 레시피결과를 친구에게 추천
'''

@app.route('/RecommendRecipe',methods=['POST'])
def RecommendRecipe():
    global current_user
    if ( current_user == None):
        return render_template('login.html')
    else:
        recipeID = request.form['recipeID']
        receiverID = request.form['receiverID']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('INSERT INTO RecommendedList(senderID,receiverID,recipeID) values(%s,%s,%s)',(current_user.getCustomerID(),receiverID,recipeID))
        con.commit()
        con.close()
        return render_template('loginpage.html')


'''
    레시피 결과를 친구에게 추천해줄 때 친구 선택 
'''

@app.route('/SelectFriendForRecipe',methods=['POST'])
def SelectFriend():
    global current_user
    if (current_user==None):
        return render_template('login.html')
    else:


        title = request.form['title']
        imageUrl = request.form['imageUrl']
        url = request.form['url']

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('INSERT INTO Recipe(title,imageUrl,url) values(%s,%s,%s)',(title,imageUrl,url))# 레시피 생성

        cur.execute("SELECT * from Recipe order by recipeID desc limit 1")

        last_recipe = cur.fetchall()
        for r in last_recipe:
            maxRecipeID = r['recipeID']

        '''
            친구 목록
        '''

        cur.execute("SELECT customer1ID,customer2ID from friend where (customer1ID like (%s) or customer2ID like (%s)) and status = 1 ",(current_user.getCustomerID(),current_user.getCustomerID()))
        friend_lists = cur.fetchall()
        con.commit()
        con.close()
        return render_template('SelectFriend.html',recipeID=maxRecipeID,friend_lists=friend_lists,current_user=current_user)


'''
내 레시피 보기
'''

@app.route('/show/MyRecipe')
def ShowMyRecipe():
    global current_user
    if (current_user ==None):
        return render_template('login.html')
    else:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT R.title as title,R.imageUrl as imageUrl,R.url as url from RecipeList AS RL join Recipe R on RL.recipeID = R.recipeID where RL.customerID like (%s)',(current_user.getCustomerID()))
        MyRecipes = cur.fetchall()
        con.close()

        return render_template('showMyRecipe.html',MyRecipes=MyRecipes)

'''
친구가 추천해준 레시피 보기
'''

@app.route('/show/RecommendedRecipe')
def ShowRecommendedRecipe():
    global current_user
    if (current_user==None):
        return render_template('login.html')
    else:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT R.title as title,R.imageUrl as imageUrl,R.url as url from recommendedlist as RL join Recipe R on RL.recipeID = R.recipeID where RL.receiverID like (%s)',(current_user.getCustomerID()))
        reco_recipes = cur.fetchall()
        return render_template('showRecommendedRecipe.html',recipes=reco_recipes)


'''

'''
if __name__ == '__main__':
    app.run(debug=True)

