from pyrogram.errors import PeerIdInvalid, UserIsBlocked
from .helpers import *


@db_session
def report_to_admins(admin, user, c, message):
    for k, v in get_admins().items():
        if k != admin.uid:
            try:
                c.send_message(
                    k,
                    format_message(
                        MSG[v.language][message],
                        user, admin=admin.link()))
            except PeerIdInvalid:
                pass


@Client.on_message(is_admin & filters.reply & filters.private &
                   filters.command(MSG['commands']['block']))
def block(c, m):
    user = get_id(m)
    if not user:
        return
    user = get_user(user)
    if user.is_admin:
        return
    admin = get_user(m.from_user.id)
    if str(user.uid) not in data['ban']:
        data['ban'].append(str(user.uid))
        m.reply(format_message(MSG[admin.language]['user_block'], user), quote=True)
        save_data()
    else:
        return m.reply(format_message(
            MSG[admin.language]['already_blocked'], user
        ), quote=True)
    report_to_admins(admin, user, c, 'user_block_admin')


@Client.on_message(is_admin & filters.reply & filters.private &
                   filters.command(MSG['commands']['unblock']))
def unblock(c, m):
    user = get_id(m)
    if not user:
        return
    user = get_user(user)
    if user.is_admin:
        return
    admin = get_user(m.from_user.id)
    if str(user.uid) in data['ban']:
        data['ban'].remove(str(user.uid))
        m.reply(format_message(MSG[admin.language]['user_unblock'], user), quote=True)
        save_data()
        try:
            c.send_message(user.uid, MSG[user.language]['unban_msg'])
        except UserIsBlocked:
            with db_session:
                delete(u for u in User if u.uid == user.uid)
    else:
        return m.reply(format_message(
            MSG[admin.language]['not_blocked'], user
        ), quote=True).cr_await
    report_to_admins(admin, user, c, 'user_unblock_admin')
