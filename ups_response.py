import requests
import re
import json
from datetime import datetime
import config.base_config as base_config



# 定义正则表达式
red_regex = re.compile(r'(押红|我红|我左|红[^蓝]|左)')
blue_regex = re.compile(r'(押蓝|我蓝|我右|[^红]蓝|右)')


# 获取 feedId 的函数
def get_feed_id(uid):
    url = f'{base_config.base_url}/getSomeOneFeeds?feedTypes=1,2,3,4,6,7,10,11&someOneUid={uid}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'feeds' in data['result'] and len(data['result']['feeds']) > 0:
            return data['result']['feeds'][0]['id']
    return None


# 获取 feed 详细信息的函数
def get_feed_details(feed_id):
    url = f'{base_config.base_url}/facade?feedId={feed_id}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            user_nick = data['result']['userInfos'][0]['user']['nick']
            create_time = data['result']['feed']['createTime']
            content_json = data['result']['feed']['content']
            content_data = json.loads(content_json)
            body_text = content_data['body']['text']
            return {
                'user_nick': user_nick,
                'create_time': create_time,
                'body_text': body_text
            }
        except (KeyError, IndexError, json.JSONDecodeError):
            return None
    return None


# 检查发布时间是否符合规则
def is_time_valid(create_time):
    # 定义时间段
    valid_time_ranges = [(10, 12), (12, 14), (14, 16), (16, 18), (18, 20), (20, 22), (22, 24)]
    now = datetime.now()

    # 获取发布时间
    post_time = datetime.fromtimestamp(create_time / 1000)  # 假设 create_time 是毫秒级时间戳
    post_hour = post_time.hour

    # 检查发布时间是否在有效时间段内
    for start, end in valid_time_ranges:
        if start <= post_hour < end and start <= now.hour < end:
            return True
    return False


# 分析 body_text 来判断投注结果
def analyze_bet(body_text):
    red_span=9999
    blue_span=9999
    if red_regex.search(body_text):
        red_span=red_regex.search(body_text).start()
    if blue_regex.search(body_text):
        blue_span=blue_regex.search(body_text).start()
    if red_span < blue_span:
        return '红方'
    elif red_span > blue_span:
        return '蓝方'
    return '未知'



# 主函数，遍历这批 uid
def process_uids_with_names(uids):
    red_count = 0
    blue_count = 0
    bet_details = []

    for user in uids:
        uid = user['id']
        name = user['name']
        feed_id = get_feed_id(uid)
        if feed_id:
            details = get_feed_details(feed_id)
            if details and is_time_valid(int(details['create_time'])) and details['body_text']:
                bet_result = analyze_bet(details['body_text'])
                bet_rate = re.compile(r"([5-9]\d%|\d+开|[一二三四五六七八九十零]+开|([红蓝][一二三四五六七八九十零,0-9])+)").search(details.get('body_text'))
                bet_rate = f", {bet_rate.group()}" if bet_rate else ""
                
                bet_info = {
                    "name": name,
                    "nickname": details['user_nick'],
                    "bet": bet_result,
                    "rate": bet_rate.strip(", ")
                }
                bet_details.append(bet_info)

                if bet_result == '红方':
                    red_count += 1
                elif bet_result == '蓝方':
                    blue_count += 1
            else:
                break

    # 生成结果字符串
    if red_count > blue_count:
        decision = f"推荐投注 红方 ({red_count} 对 {blue_count})"
    elif blue_count > red_count:
        decision = f"推荐投注 蓝方 ({blue_count} 对 {red_count})"
    elif blue_count == red_count == 0:
        decision = "不在竞猜时间段内"
    else:
        decision = f"红蓝投注持平 ({red_count} 对 {blue_count})，请自行决定"

    result = {
        "bet_details": bet_details,
        "decision": decision
    }

    return result