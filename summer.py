import json
import time
import steam.webauth as wa
from steampy.guard import generate_one_time_code
import logging
import re
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')



def main():
    categories = [
        "arcade_rhythm", "strategy_cities_settlements", "sports", "simulation", "multiplayer_coop",
        "casual", "rpg", "horror", "vr", "strategy",
        ]
    with open(r'accounts.txt', 'r') as f:
        accounts = f.read().split('\n')
    mafiles_on = int(input('ACC WITH MAFILES? (0 || 1): '))
    for index, account in enumerate(accounts):
        try:
            if len(account) < 5 or not ':' in account: continue
            username = account.split(":")[0]
            password = account.split(":")[1]
            mafilees = (f"mafiles\{username}.maFile")
            user = wa.WebAuth(username)
            one_time_authentication_code = None
            if mafiles_on == 1:
                with open(mafilees,'r',encoding='UTF-8') as f:
                    content:dict = json.load(f)
                    shared_secret = content.get('shared_secret')
                one_time_authentication_code = generate_one_time_code(shared_secret)
            try:
                user.login(password,twofactor_code=one_time_authentication_code)
            except Exception as exp:
                if isinstance(exp, wa.LoginIncorrect):
                    logging.warning(f"[ {username} ] акк не валид")
                    continue
                if isinstance(exp, wa.CaptchaRequired):
                    input(f"[ {username} ] требует капчу, меняй айпи")
                time.sleep(5)
                continue
            su = user.logged_on
            if su == True:
                try:
                    resp0 = user.session.get("https://store.steampowered.com/sale/clorthax_quest")
                    data_userinfo = re.findall(r'data-userinfo="{(.*?)}"', resp0.text)[0]
                    clan_accountid = re.findall(r"clans/(\d+?)/", resp0.text)[0]
                    authwgtoken = str(data_userinfo).split(':&quot;')[-2].split('&quot;')[0]
                    sessionid = user.session.cookies.get('sessionid', domain='store.steampowered.com')
                    first_url = 'https://store.steampowered.com/saleaction/ajaxopendoor'
                    data = {
                                "sessionid": sessionid,
                                "authwgtoken": authwgtoken,
                                "door_index": 0,
                                "clan_accountid": clan_accountid,
                            }
                    first_req = user.session.post(first_url, data = data)
                    assert first_req.status_code == 200
                    logging.info(f'[ {username} ][{index+1}/{len(accounts)}] Registered_sale = {first_req.status_code}')
                    time.sleep(0.2)
                    for _, category in enumerate(categories):
                        try:
                            index_game = _+1
                            if index_game == 10:
                                bef_clanid = data["clan_accountid"]
                                data["clan_accountid"] = 41316928
                            if category != "vr":
                                url = f"https://store.steampowered.com/category/{category}/?snr=1_614_615_clorthaxquest_1601"
                            else:
                                url = f"https://store.steampowered.com/{category}/?snr=1_614_615_clorthaxquest_1601"
                            req1 = user.session.get(url)
                            logging.info(f'[ {username} ][{index+1}/{len(accounts)}] Getting_game [{category} {index_game}/10] = {req1.status_code}')
                            assert req1.status_code == 200
                            datarecord = str(re.findall(r'datarecord(.*?)}"', req1.text)[0]).replace("&quot;",'').replace(":",'')
                            data["datarecord"] = datarecord
                            data["door_index"] = index_game
                            req2 = user.session.post(first_url, data=data)
                            logging.info(f'[ {username} ][{index+1}/{len(accounts)}] find game [{category} {index_game}/10] = {req2.status_code}')
                            time.sleep(1)
                        except Exception as e:
                            logging.info(f'ERROR: YOU abobus = {e}')
                            time.sleep(2)
                    data["datarecord"] = ''
                    data.pop("datarecord")
                    data["door_index"] = 11
                    data["clan_accountid"] = bef_clanid
                    completereq = user.session.post(first_url, data=data)
                    logging.info(f'[ {username} ][{index+1}/{len(accounts)}] FINISHED = {completereq.status_code}')
                    time.sleep(2)
                except Exception as e:
                    err = f'[{username}] ERROR {e}'
                    logging.warning(err)
                    time.sleep(4)
            else:
                logging.warning(f"[ {username} ] всё плохо с данным акком спасаай")
                time.sleep(4)
        except Exception as e:
            logging.warning(f'Произошла неизвестная ошибка {e}')
            time.sleep(4)
    for _ in range(5):
        logging.info('FINISH')
        input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.warning(e)
        input()