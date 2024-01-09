from linebot.models import TextSendMessage, TemplateSendMessage, ConfirmTemplate, MessageAction
import csv
import os

def handle_add_list(event, line_bot_api, user_states, user_data):
    # 请求用户输入王国名称
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='请输入王国名称：')
    )
    user_states[event.source.user_id] = 'awaiting_kingdom_name'

def process_state(user_id, event, line_bot_api, user_states, user_data):
    msg = event.message.text
    state = user_states.get(user_id)

    if state == 'awaiting_kingdom_name':
        # 存储王国名称并询问用户是否正确
        user_data[user_id] = {'kingdom_name': msg}
        confirm_template_message = TemplateSendMessage(
            alt_text='确认王国名称',
            template=ConfirmTemplate(
                text=f'{msg}王国的子民你好，王国名称输入正确吗？',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='否', text='否')
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_template_message)
        user_states[user_id] = 'confirming_kingdom_name'

    elif state == 'confirming_kingdom_name':
        if msg == '是':
            # 王国名称确认正确，继续下一步
            user_info = {'user_id': user_id, 'kingdom_name': user_data[user_id]['kingdom_name']}
            save_to_csv(user_info)  # 保存到 CSV
            user_states[user_id] = 'done'  # 或者转移到下一个状态
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='王国名称已确认')
            )
        elif msg == '否':
            # 用户选择重新输入王国名称
            user_states[user_id] = 'awaiting_kingdom_name'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='请重新输入王国名称：')
            )

def save_to_csv(user_data, file_name='user_data.csv'):
    file_exists = os.path.isfile(file_name)

    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'kingdom_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # 文件不存在则写入头部

        writer.writerow(user_data)
