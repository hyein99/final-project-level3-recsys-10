import pandas as pd 

import streamlit as st

# from screen.header import header
# from screen.map import my_map
from screen.components import get_list_component, get_detail_component, my_map, header

from config.config import BACKEND_ADDRESS, DOMAIN_INFO,GU_INFO_CENTER,STATE_KEYS_VALS
from st_click_detector import click_detector
import copy

import requests
import json

COORD_MULT = 1000000000


def logout(session : dict):
    
    for k, v in STATE_KEYS_VALS:
        if k in session:
            del session[k]

def change_center_info(session,coord, level):
    session['center']['coord'] = coord
    session['center']['level'] = level


def show_main(session:dict,item_list:list):
    # print("check" , os.spath.isfile("/opt/ml/3rdproject/final_team_repo/webserver/frontend/config/user_sample.yaml") )
    # item_list = item_list[5:6] if( True == session.show_detail) else item_list
    # show_item_list 는 item_list 로 초기화된다. 
    if( None == session["show_item_list"]):
        # 찜 동기화를 위해 deepcopy 비활성화 
        # session["show_item_list"] = copy.deepcopy(session["item_list"])
        session["show_item_list"] = (session["item_list"])

    button_col1, button_col2, button_col3, button_col4 =st.columns(4)
    
    with button_col1:
        if( st.button('관심 목록 보기')):
            # TODO FT301
            # TODO 찜 목록 요청 
            user_info = {
                "user_id" : session['cur_user_info']['user_id'],
                "user_gu" : session['cur_user_info']['user_gu'],
                "house_ranking":{}
            }
            url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['zzim'], DOMAIN_INFO['items']])
            res = requests.post(url,data=json.dumps(user_info) )
            st.session_state['show_item_list'] = [*res.json()['houses'].values()]
            session['show_heart'] = True
    
    with button_col2:
        if( st.button('현재 위치에서 매물 보기',disabled=True)):
            temp_center = []
            
            if( False == bool(session["map_bounds"])):
                print("현재 map bounds 가 반환되지 않았음 ㅠㅠ 구 중심으로 보여줄게 ")
                temp_selected_gu = session['cur_user_info']['user_gu']
                temp_center = [GU_INFO_CENTER[temp_selected_gu]["lat"],GU_INFO_CENTER[temp_selected_gu]["lng"]]
                change_center_info(session, temp_center , 14 )
            
            else :
                min_lng, min_lat = session['map_bounds']['_southWest']['lng'],session['map_bounds']['_southWest']['lat']
                max_lng, max_lat = session['map_bounds']['_northEast']['lng'],session['map_bounds']['_northEast']['lat']
                params = {
                    "user_id": session['cur_user_info']['user_id'],
                    "user_gu": "",
                    "house_ranking": {},
                    "min_lat": min_lat,
                    "min_lng": min_lng,
                    "max_lat": max_lat,
                    "max_lng": max_lng
                }
                url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['map'],DOMAIN_INFO['items'], DOMAIN_INFO['zoom']])
                res = requests.post(url,data=json.dumps(params) )

                if( 'houses' not in res.json()):
                    st.error('현재 사용할 수 없는 기능입니다.')
                    temp_center = [GU_INFO_CENTER["강남구"]["lat"],GU_INFO_CENTER["강남구"]["lng"]]

                elif( False == bool(res.json()['houses'])):
                    st.warning('현재 위치에 매물이 하나도 없습니다.')
                else:    
                    session['item_list'] = [*res.json()['houses'].values()]
                    temp_center = [min_lat + ( max_lat - min_lat) / 2 ,min_lng + ( max_lng - min_lng) / 2]
                    change_center_info(session, temp_center , 14 )


            session["show_item_list"] = (session["item_list"])
            # 찜 동기화를 위해 deepcopy 비활성화 
            # session["show_item_list"] = copy.deepcopy(session["item_list"])
            session['show_heart'] = False
            session['show_detail'] = False

    with button_col3:
        if( st.button('인프라 변경')):
            session['page_counter'] = 2
            st.experimental_rerun()

    with button_col4:
        if ( st.button('로그아웃')):
            # TODO : session 적용시 서버에 요청   
            logout(session)
            session['page_counter'] = 0
            st.experimental_rerun()


    # 관심 목록은 detail 한 것을 보여준다. ( 기능 제거 )
    # session['show_detail'] = True if ( True == session['show_heart'] ) else session['show_detail']  
    with st.spinner():
        map_data = my_map(session, session["show_item_list"])
        session["map_bounds"] = map_data["bounds"]
            # 클릭된 좌표가 이전 것과 같지 않고, 클릭된 것이 있을 때 
            # detail 한 정보를 보여준다. 
        with st.sidebar:
            if( ( session['ex_loaction'] != map_data["last_object_clicked"] ) and 
                ( None != map_data["last_object_clicked"] ) ):
                session['show_detail'] = True
                session['ex_loaction'] = map_data["last_object_clicked"]
                # session["show_item_list"] = list(filter(lambda item: item['location'] == compare_location, item_list))
                temp_item_list = list(filter(lambda item: (map_data["last_object_clicked"]['lat'] == item['lat'])\
                                            and (map_data["last_object_clicked"]['lng'] == item['lng']) , item_list))
                
                if( 0 != len(temp_item_list)):
                    # DONE FT401
                    # DONE Marker 내 매물 클릭 
                    # TODO 함수화 
                    params = {
                        "user_id" : st.session_state['cur_user_info']['user_id'],
                        "house_id" : session["show_item_list"][0]['house_id'],
                        "log_type" : "M"
                    }
                    url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['map'],DOMAIN_INFO['items'], DOMAIN_INFO['click']])
                    res = requests.post(url,data=json.dumps(params) )
                    
                    last_object_clicked_coord = [ map_data["last_object_clicked"]['lat'] ,map_data["last_object_clicked"]['lng']  ]
                    session["show_item_list"] = temp_item_list
                    change_center_info(session, last_object_clicked_coord, 18)

                    st.experimental_rerun()
                    # pass
                else : 
                    st.warning('선택된 아이템의 매물 정보가 없습니다.', icon="⚠️")
        
            # detail 한 정보를 보여주는 상태일 때 
            if ( (session["show_detail"] == True and (session["show_heart"]==False)) or 
                 (session["show_detail"] == False ) and (session["show_heart"] == True)) :
                # 돌아가기 버튼을 클릭하면 show_item_list 를 item_list 로 다시 교체
                if ( st.button('상세 목록 돌아가기')):
                    temp_selected_gu = session['cur_user_info']['user_gu']
                    temp_center = [GU_INFO_CENTER[temp_selected_gu]["lat"],GU_INFO_CENTER[temp_selected_gu]["lng"]]

                    session['show_heart'] = False
                    session['show_detail'] = False
                    change_center_info(session, temp_center , 14 )
                    # 찜 동기화를 위해 deepcopy 비활성화 
                    # session["show_item_list"] = copy.deepcopy(session["item_list"])
                    session["show_item_list"] = (session["item_list"])
                    # session['ex_loaction'] =  None
                    st.experimental_rerun()
                    # session["show_detail"] = False
                    # session["show_item_list"] = item_list

            elif (session["show_detail"] == True ) and (session["show_heart"] == True):
                # 돌아가기 버튼을 클릭하면 show_item_list 를 item_list 로 다시 교체
                if ( st.button('관심 목록 돌아가기')):
                    user_info = {
                    "user_id" : session['cur_user_info']['user_id'],
                    "user_gu" : session['cur_user_info']['user_gu'],
                    "house_ranking":{}
                    }
                    url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['zzim'], DOMAIN_INFO['items']])
                    res = requests.post(url,data=json.dumps(user_info) )
                    st.session_state['show_item_list'] = [*res.json()['houses'].values()]
                    session['show_heart'] = True
                    session['show_detail'] = False
                    # session['ex_loaction'] =  None
                    st.experimental_rerun()

            str = '\
            <link rel="stylesheet" href="css_basic.css">\
            <link rel="stylesheet" href="font-awesome/css/font-awesome.min.css">\
            <link href="https://hangeul.pstatic.net/hangeul_static/css/nanum-square-neo.css" rel="stylesheet" " crossorigin="anonymous">\
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">\
                <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>\
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>\
            <style>\
            a:link { color: red; text-decoration: none;}\
            a:visited { color: black; text-decoration: none;}\
            a:hover { color: black; text-decoration: none;}\
            body {background-color: powderblue;}\
            h1   {color: #FFD400;}\
            p    {color: red;}\
            div {\
            font-family: "";\
            font-display: "optional";\
            }\
            .h_container{\
                background-color: #cac7c7;\
                border-radius: 20px;\
                box-shadow: 0 2px 8px rgba(0,0,0,.1);\
                display: inline-block;\
                width:35px;\
                height:35px;\
                text-align:center;\
                line-height:45px;\
                }\
                #heart_Y{\
                font-size: 50px;\
                color:red;\
                }\
                #heart_N{\
                font-size: 50px;\
                color:lightgray;\
                }\
                #heart_N:hover{\
                color:red;\
                }\
                </style>\
            <div style="overflow-y: scroll; height:1500px; ">'
            # 실행 순서상 아래 str 만드는 for 문 바로 위에 있어야 함 
            str += " <h1>관심 목록 </h1>" if(True ==session.show_heart ) else ""
            make_html = get_detail_component if( True == session.show_detail) else get_list_component

            for item in session["show_item_list"]: 
                str+= make_html(item)
            str+= "</div>"
            clicked = click_detector(str)
            clicked_info = clicked.split('_')

            if( "" != clicked and "zzim"!=clicked_info[0]):
                # DONE FT402
                # DONE List 내 매물클릭 
                # TODO 함수화 
                params = {
                    "user_id" : st.session_state['cur_user_info']['user_id'],
                    "house_id" : int(clicked_info[0]),
                    "log_type" : "L"
                }
                url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['map'],DOMAIN_INFO['items'], DOMAIN_INFO['click']])
                res = requests.post(url,data=json.dumps(params) )
                
                session["show_detail"] = True
                session["show_item_list"] = list(filter(lambda item:  int(clicked_info[0]) == item['house_id'], item_list) )
                # session["show_item_list"] = list(filter(lambda item: item['location'] == clicked, item_list))
                change_center_info(session, list(map(float,clicked_info[1:]) ), 18)
                st.experimental_rerun()

            if( "" != clicked and "zzim"==clicked_info[0]):
                zzim_status, house_id = clicked_info[1:]
                next_zzim_status =  'N' if ( 'Y' == zzim_status ) else 'Y' 

                # 가지고 있는 item list 의 목록에서 해당하는 데이터의 zzim 여부를 변경한다. 
                change_target = list(filter(lambda item:  int(house_id) == item['house_id'], session["show_item_list"] ) )
                change_target[0]["zzim"] = next_zzim_status

                user_info = {
                    "user_id"  : st.session_state['cur_user_info']['user_id'],
                    "house_id" : house_id,
                    "zzim_yn"  : next_zzim_status,
                }
                url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['zzim'], DOMAIN_INFO['items'], DOMAIN_INFO['register']])
                res = requests.post(url,data=json.dumps(user_info) )
                st.experimental_rerun()

                # params = {'param1': 'value1', 'param2': 'value'}
                # url = ''.join([BACKEND_ADDRESS, DOMAIN_INFO['zzim'], DOMAIN_INFO['house']])
                # res = requests.get(URL, params=params)
            # st.markdown(f"**{clicked} clicked**" if clicked != "" else "**No click**")

            # # bootstrap 4 collapse example
            # components.html(
            #     str,
            #     height=1300,
            #     scrolling=True,
            # )
